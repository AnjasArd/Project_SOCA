from flask import Flask, render_template, jsonify, request, send_file
import os
from werkzeug.utils import secure_filename
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import csv
from threading import Thread
from datetime import datetime
import logging
import pandas as pd
import io
import zipfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

VIOLATIONS_DIR = 'static/violations'
CSV_LOG_FILE = 'static/violation_log.csv'

if not os.path.exists(CSV_LOG_FILE):
    with open(CSV_LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Filename', 'Violation Type', 'Confidence'])

os.makedirs(VIOLATIONS_DIR, exist_ok=True)

violation_files = []
notifications = []


class ViolationHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            filename = os.path.basename(event.src_path)
            if filename not in violation_files:
                violation_files.append(filename)

    def on_deleted(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            if filename in violation_files:
                violation_files.remove(filename)

def start_file_monitoring():
    event_handler = ViolationHandler()
    observer = Observer()
    observer.schedule(event_handler, VIOLATIONS_DIR, recursive=False)
    observer.start()

def get_violation_files():
    if os.path.exists(VIOLATIONS_DIR):
        files = os.listdir(VIOLATIONS_DIR)
        return [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return []

@app.route('/')
def dashboard():
    global violation_files
    violation_files = get_violation_files()
    return render_template('dashboard.html')

@app.route('/api/violations')
def get_violations():
    return jsonify(violation_files)

@app.route('/upload-ppe-violation', methods=['POST'])
def upload_violation():
    try:
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No selected file'}), 400
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        violation_type = request.form.get('violation_type', 'Unknown')
        original_filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_{violation_type}_{original_filename}"
        
        save_path = os.path.join(VIOLATIONS_DIR, unique_filename)
        file.save(save_path)
        
        confidence = request.form.get('confidence', 'N/A')
        
        logger.info(f"Uploaded violation: {unique_filename}")
        logger.info(f"Violation Type: {violation_type}")
        logger.info(f"Confidence: {confidence}")
        
        notif_types = []
        if 'no-helm' in violation_type:
            notif_types.append('no-helm')
        if 'no-vest' in violation_type:
            notif_types.append('no-vest')
        if notif_types:
            for notif in notif_types:
                notification = {
                    'type': notif,
                'filename': unique_filename,
                'timestamp': timestamp
                }
                notifications.append(notification)
                logger.info(f"Added notification: {notification}")
        else:
            logger.warning(f"Invalid violation type: {violation_type}")

        with open(CSV_LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, unique_filename, violation_type, confidence])
            logger.info("Violation logged to CSV")

        return jsonify({
            'message': 'Upload successful', 
            'filename': unique_filename
        }), 200
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/download-log')
def download_log():
    df = pd.read_csv(CSV_LOG_FILE)
    files_now = set(get_violation_files())
    df = df[df['Filename'].isin(files_now)]
    def get_risk_profile(violation_type):
        vt = violation_type.lower()
        if 'no-helm' in vt and 'no-vest' in vt:
            return 'Risiko Tinggi: Terkena percikan las, bahan kimia, tertimpa benda berat, cedera kepala, dan risiko kecelakaan kerja lainnya.'
        elif 'no-helm' in vt:
            return 'Risiko Tanpa Helm: Cedera kepala akibat benda jatuh, benturan dengan struktur kapal, percikan las ke kepala.'
        elif 'no-vest' in vt:
            return 'Risiko Tanpa Vest: Sulit terlihat oleh operator, cedera dada dan perut, kurang perlindungan dari bahan kimia.'
        else:
            return 'Tidak ada pelanggaran.'
    df['Profil Risiko'] = df['Violation Type'].apply(get_risk_profile)
    total_pelanggaran = len(df)
    jenis_pelanggaran = df['Violation Type'].value_counts()
    summary_data = [
        ['Total Pelanggaran', total_pelanggaran],
    ]
    summary_jenis = [['Jenis Pelanggaran', 'Jumlah']]
    for jenis, jumlah in jenis_pelanggaran.items():
        summary_jenis.append([jenis, jumlah])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Pelanggaran')
        workbook  = writer.book
        summary_ws = workbook.add_worksheet('Statistik Pelanggaran')
        writer.sheets['Statistik Pelanggaran'] = summary_ws
        for row_idx, (label, value) in enumerate(summary_data):
            summary_ws.write(row_idx, 0, label)
            summary_ws.write(row_idx, 1, value)
        start_row = len(summary_data) + 2
        for r, row in enumerate(summary_jenis):
            for c, val in enumerate(row):
                summary_ws.write(start_row + r, c, val)
        if len(summary_jenis) > 1:
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name': 'Jumlah per Jenis',
                'categories': ['Statistik Pelanggaran', start_row + 1, 0, start_row + len(summary_jenis) - 1, 0],
                'values':     ['Statistik Pelanggaran', start_row + 1, 1, start_row + len(summary_jenis) - 1, 1],
            })
            chart.set_title({'name': 'Grafik Pelanggaran per Jenis'})
            summary_ws.insert_chart(start_row + 2, 3, chart)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='statistik_pelanggaranAPD.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/api/notifications')
def get_notifications():
    global notifications
    current_notifications = notifications.copy()
    count = len(current_notifications)
    logger.info(f"Returning {count} notifications")
    if count > 0:
        logger.info(f"Notifications content: {current_notifications}")
    notifications.clear()
    return jsonify(current_notifications)

@app.route('/download-all-violations')
def download_all_violations():
    files = [f for f in os.listdir(VIOLATIONS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not files:
        return jsonify({'error': 'No violation images found.'}), 404
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in files:
            file_path = os.path.join(VIOLATIONS_DIR, filename)
            zipf.write(file_path, arcname=filename)
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='bukti_pelanggaran.zip', mimetype='application/zip')

@app.route('/download-violation-image')
def download_violation_image():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided.'}), 400
    file_path = os.path.join(VIOLATIONS_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found.'}), 404
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    Thread(target=start_file_monitoring, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)