# 🐱 Cat-Kicau-Mania

Project Python yang menggunakan Computer Vision untuk mendeteksi gesture tangan dan wajah, lalu menampilkan video serta suara kucing.

---

## 🎯 Fitur
- Deteksi tangan menggunakan MediaPipe
- Deteksi wajah & posisi mulut
- Gesture:
  - Tangan dekat mulut
  - Tangan melambai
- Menampilkan video kucing
- Memutar suara kucing

---

## 🧠 Cara Kerja
Program akan aktif jika:
1. Satu tangan berada dekat mulut  
2. Tangan lainnya bergerak (melambai)  

Jika kedua kondisi terpenuhi:  
➡️ Video & suara kucing akan diputar

---

## ▶️ Cara Menjalankan

1. Install dependency
```bash
pip install opencv-python mediapipe numpy pygame
```

2. Download asset
cat.mp4
cat_audio.mp3

Letakkan di folder yang sama dengan kicau.py

3. Pastikan path di kode
```bash
video_cat = cv2.VideoCapture("cat.mp4")
sound = pygame.mixer.Sound("cat_audio.mp3")
```

4. Jalankan program
```bash
python kicau.py
```

🧰 Teknologi
OpenCV
MediaPipe
NumPy
Pygame
