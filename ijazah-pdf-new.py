import shutil
import cv2
import pytesseract
import re
import json
import sys
import os
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

# ====== Parse Arguments ======
import argparse

parser = argparse.ArgumentParser(description="OCR PDF Halaman ke-N dengan crop")
parser.add_argument("pdf_path", help="Path ke file PDF")
parser.add_argument("--debug", action="store_true", help="Aktifkan debug mode")
parser.add_argument("--page", type=int, default=2, help="Halaman PDF yang akan diproses (mulai dari 1)")

args = parser.parse_args()

pdf_path = args.pdf_path
debug = args.debug
page_number = args.page

# ====== Validasi ======
if not os.path.exists(pdf_path):
    print(f"File PDF tidak ditemukan: {pdf_path}")
    sys.exit(1)

if not shutil.which("tesseract"):
    print("Tesseract tidak ditemukan di PATH")
    sys.exit(1)

if not shutil.which("pdftoppm"):
    print("Poppler (pdftoppm) tidak ditemukan di PATH")
    sys.exit(1)

# ====== Buat folder debug jika perlu ======
output_folder = "process"
if debug and not os.path.exists(output_folder):
    os.makedirs(output_folder)

# ====== Convert PDF ke gambar ======
try:
    images = convert_from_path(pdf_path, dpi=300)
    if len(images) < page_number:
        print(f"PDF hanya memiliki {len(images)} halaman. Halaman {page_number} tidak tersedia.")
        sys.exit(1)
    selected_image = images[page_number - 1]
except Exception as e:
    print("Gagal membuka PDF:", e)
    sys.exit(1)

if debug:
    selected_image_path = os.path.join(output_folder, f'page{page_number}.png')
    selected_image.save(selected_image_path, 'PNG')

# ====== Konversi ke OpenCV dan proses gambar ======
cv_image = cv2.cvtColor(np.array(selected_image), cv2.COLOR_RGB2BGR)

# # Crop
# h, w = cv_image.shape[:2] 
# cropped_image = cv_image[270:h//4, 380:w]

y_start = 300
y_end = 780
cropped_image = cv_image[y_start:y_end, :]

if debug:
    cv2.imwrite(os.path.join(output_folder, 'cropped.png'), cropped_image)

# Grayscale, blur, threshold
gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
if debug:
    cv2.imwrite(os.path.join(output_folder, 'thresh.png'), thresh)

# Hapus noise kecil
inverted = cv2.bitwise_not(thresh)
contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
clean = inverted.copy()
for cnt in contours:
    if cv2.contourArea(cnt) < 50:
        cv2.drawContours(clean, [cnt], -1, (0, 0, 0), thickness=cv2.FILLED)
final_clean = cv2.bitwise_not(clean)
if debug:
    cv2.imwrite(os.path.join(output_folder, 'clean.png'), final_clean)

# ====== OCR ======
# custom_config = r'--oem 3 --psm 6 -l ind -c tessedit_char_whitelist= ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
custom_config = r'--oem 3 --psm 6 -l ind'

text = pytesseract.image_to_string(final_clean, config=custom_config)

# ====== Bersihkan dan cetak output ======
clean_text = re.sub(r'[^A-Za-z0-9\s]', '', text)
text_lines = [line.strip() for line in clean_text.splitlines() if line.strip()]

# for line in text_lines:
#     print(line)

# print(text_json)
# output text_json

# [
#     "INI Oto WIWAPYY KOK NI KU aa",
#     "Nama ISMI  KHASANAH",
#     "Tempat dan Tanggal Lahir Jakarta 4 Tebruari 2004",
#     "Nomor Induk do",
#     "Nomor Induk Siswa Nasional 00401908386",
#     "Kompetensi Keahlian Rekayasa Perangkat Lunak",
#     "Na Mata Palataran Nilai Ujian"
# ]
# ambil nama dan kompetensi keahlian saja

nama = next((line.replace("Nama", "").strip() for line in text_lines if "Nama" in line), "NAMA TIDAK DITEMUKAN")

# Ambil kompetensi
kompetensi = next((line.replace("Kompetensi Keahlian", "").strip() for line in text_lines if "Kompetensi Keahlian" in line), "KOMPETENSI TIDAK DITEMUKAN")

# print("Nama:", nama)
# print("Kompetensi Keahlian:", kompetensi)

text_json = json.dumps([
    nama,
    kompetensi
], ensure_ascii=False, indent=4)

print(text_json)
