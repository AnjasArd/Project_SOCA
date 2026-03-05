# Safety Officer Computerized Assistant (SOCA)

**Safety Officer Computerized Assistant (SOCA)** merupakan sistem
pemantauan penggunaan **Alat Pelindung Diri (APD)** berbasis **Computer
Vision** yang dirancang untuk membantu proses pengawasan keselamatan
kerja di lingkungan **galangan kapal**. Sistem ini memanfaatkan
algoritma **YOLOv5** untuk mendeteksi penggunaan **helm keselamatan**
dan **rompi keselamatan (safety vest)** secara otomatis melalui kamera
pengawas (CCTV), kemudian menampilkan hasil deteksi melalui **website
berbasis Flask**. SOCA dikembangkan untuk membantu **safety officer** dalam
mengidentifikasi pelanggaran penggunaan APD secara lebih cepat, akurat,
dan terdokumentasi secara digital.

---

# 🚀 Fitur Utama

- 🔍 Deteksi APD berbasis YOLOv5
- 🎥 Pemantauan real-time dari kamera
- 📹 Deteksi dari video
- 🖼 Deteksi dari gambar
- 🌐 Dashboard website berbasis Flask yang ringan dan fleksibel
- 📊 Visualisasi data pelanggaran
- 📁 Download log pelanggaran (ZIP / XLSX)
- ⚠️ Notifikasi pelanggaran APD

---

# 🧠 Kelas Deteksi

Model mendeteksi **4 kelas utama**:

---

- **helm** Pekerja menggunakan helm
- **vest** Pekerja menggunakan rompi
- **no_helm** Pekerja tidak menggunakan helm
- **no_vest** Pekerja tidak menggunakan rompi

---

# ⚙️ Tech Stack

- Python
- YOLOv5
- PyTorch
- Flask
- OpenCV
- HTML / CSS / JavaScript
- Matplotlib & Pandas

---

# 🖥 Cara Menjalankan Web Application

### 1. Bypass PowerShell Security

*Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass -Force*

### 2. Masuk ke directory Web App

*cd webapp*

### 3. Membuat Virtual Environment

*virtualenv envdir*

### 4. Aktivasi Virtual Environment

*.\envdir\Scripts\activate*

### 5. Menjalankan Web Application

*python app.py*

Buka browser:

http://localhost:5000

---

# 🎥 Menjalankan Deteksi APD YOLOv5

### Masuk ke directory YOLOv5

*cd yolov5*

### Real-Time Camera

*python detect.py --weights runs/train/skenario4s_best/weights/best.pt
--img 640 --source 0 --view-img*

### Video Source

*python detect.py --weights runs/train/skenario4s_best/weights/best.pt
--img 640 --source video/NoAPD2.mp4 --view-img*

### Image Source

*python detect.py --weights runs/train/skenario4s_best/weights/best.pt
--img 640 --source image/testimage.jpg --view-img*

---

# 📊 Dataset

Dataset diperoleh dari rekaman **CCTV galangan kapal** yang kemudian
melalui proses:

1.  Frame extraction dari video
2.  Image annotation
3.  Dataset preprocessing
4.  Training model YOLOv5

Total dataset: **808 gambar teranotasi** dengan resolusi **640×640**.

---

# 📈 Hasil Model Terbaik
---

- Precision 0.91
- Recall 0.87
- mAP@0.5 0.93

Model terbaik diperoleh dari **Skenario 4**.

---

# 🧪 Evaluasi Sistem

Evaluasi sistem dilakukan menggunakan:

- Confusion Matrix
- Blackbox Testing
- Kuesioner Pengguna

---

# 🏭 Use Case

Sistem dapat digunakan pada:

- Galangan kapal
- Industri manufaktur
- Area konstruksi
- Pelabuhan
- Area industri berisiko tinggi

---

# 👨‍💻 Author

**Anjas Ard**\
Safety Officer Computerized Assistant (SOCA) Project\
Computer Vision Based PPE Monitoring System

---

# 📜 License

Project ini dikembangkan untuk **kepentingan penelitian dan akademik**.
