# OCR Final Project

## Deskripsi
Proyek ini adalah sebuah script Python untuk melakukan OCR (Optical Character Recognition) pada file PDF, khususnya untuk memproses halaman kedua dari dokumen PDF. Script ini dirancang untuk mengekstrak teks dari area tertentu pada halaman kedua dokumen PDF dengan menggunakan pustaka seperti `pytesseract`, `cv2`, dan `pdf2image`.

## Fitur
1. **Konversi PDF ke Gambar**  
   Mengonversi halaman-halaman dalam file PDF menjadi gambar dengan resolusi tinggi (300 DPI).

2. **Pemrosesan Gambar**  
   - **Crop Area Tertentu**: Memotong area tertentu dari halaman kedua PDF untuk fokus pada bagian yang relevan.
   - **Grayscale, Blur, dan Thresholding**: Mengubah gambar menjadi grayscale, menghaluskan gambar dengan Gaussian Blur, dan menerapkan thresholding untuk meningkatkan kualitas OCR.
   - **Pembersihan Gambar**: Menghapus titik-titik kecil atau noise dari gambar untuk meningkatkan akurasi OCR.

3. **OCR (Optical Character Recognition)**  
   Menggunakan Tesseract OCR untuk mengekstrak teks dari gambar yang telah diproses.

4. **Pembersihan Teks**  
   Membersihkan teks hasil OCR dari karakter yang tidak diinginkan dan mengonversinya menjadi format JSON.

5. **Mode Debug**  
   - Menyimpan file sementara (gambar hasil crop, threshold, dll.) untuk keperluan debugging.
   - Menghapus file sementara secara otomatis jika mode debug tidak diaktifkan.

## Alur Pemrosesan
1. **Input PDF**  
   - Script menerima file PDF sebagai input melalui command line.
   - Jika file PDF tidak diberikan atau hanya memiliki satu halaman, script akan berhenti dengan pesan error.

2. **Konversi PDF ke Gambar**  
   - Halaman kedua dari PDF dikonversi menjadi gambar dengan resolusi 300 DPI.

3. **Penyimpanan Gambar Halaman Kedua**  
   - Gambar halaman kedua disimpan sementara untuk diproses lebih lanjut.

4. **Pemrosesan Gambar**  
   - Area tertentu dari gambar dipotong (crop) berdasarkan koordinat yang telah ditentukan.
   - Gambar hasil crop diubah menjadi grayscale, di-blur, dan di-threshold.
   - Noise atau titik-titik kecil pada gambar dihapus.

5. **OCR**  
   - Teks diekstrak dari gambar yang telah diproses menggunakan Tesseract OCR.
   - Hanya karakter alfanumerik yang diizinkan dalam hasil OCR.

6. **Pembersihan dan Output Teks**  
   - Teks hasil OCR dibersihkan dari karakter yang tidak diinginkan.
   - Teks yang telah dibersihkan diubah menjadi format JSON dan ditampilkan di terminal.

7. **Penghapusan File Sementara**  
   - Jika mode debug tidak diaktifkan, semua file sementara akan dihapus secara otomatis.

## Cara Penggunaan

### 1. Instalasi
Pastikan Anda memiliki Python 3.x terinstal di sistem Anda. Kemudian, pastikan Anda telah menginstal Tesseract OCR di sistem Anda. Untuk pengguna Linux, Anda dapat menginstalnya dengan perintah:

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-ind # untuk bahasa indonesia
```

> Pengguna Windows harus menginstall lewat package .exe

Untuk Pengguna windows harus install beberapa aplikasi yang dibutuhkan seperti [Tesseract for Windows](https://github.com/tesseract-ocr/tesseract/releases) dan juga [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)

Jangan lupa tambahkan path tesseract dan poppler ke Environment Variable di windows agar poppler dan tesseract dapat di akses dimana saja.

Lalu instal semua dependensi yang diperlukan dengan perintah berikut:

```bash
pip install opencv-python pytesseract pdf2image
```


### 2. Eksekusi Script
Jalankan script dengan memberikan file PDF sebagai argumen. Anda juga dapat menambahkan opsi `--debug` untuk menyimpan file sementara selama proses.

Contoh tanpa debug:
```bash
python ijazah-pdf-final.py namafile.pdf
```

Contoh dengan debug:
```bash
python ijazah-pdf-final.py namafile.pdf --page 2 --crop 950,297,1326,505 --debug
```

### 3. Output
- Jika berhasil, teks yang diekstrak dari halaman kedua PDF akan ditampilkan dalam format JSON di terminal.
- Jika mode debug diaktifkan, file sementara seperti gambar hasil crop, threshold, dan gambar yang telah dibersihkan akan disimpan di folder `process`.

## Catatan
- Pastikan file PDF memiliki minimal 2 halaman, karena script ini hanya memproses halaman kedua.
- Koordinat crop (x, y, w, h) dapat disesuaikan di dalam script jika area yang diproses berbeda.