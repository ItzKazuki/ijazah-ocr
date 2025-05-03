import shutil
import cv2
import pytesseract
import re
import json
import sys
import os
from pdf2image import convert_from_path

# ====== Cek input dari command line ======
if len(sys.argv) < 2:
    print("Usage: python mypy.py namafile.pdf [--debug]")
    sys.exit(1)

pdf_path = sys.argv[1]
debug = '--debug' in sys.argv

# Buat folder "process" jika belum ada
output_folder = 'process'
if debug and not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Set path untuk Tesseract
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract' 
# TODO: Uncomment and set the correct path for Tesseract when use another platform like Windows or MacOS

# cek apakah tesseract dan poppler terinstall dan terbaca di environment path
# Cek apakah Tesseract terinstall
if not shutil.which("tesseract"):
    print("Tesseract tidak ditemukan di environment path. Pastikan Tesseract sudah terinstall.")
    sys.exit(1)

# Cek apakah Poppler terinstall
if not shutil.which("pdftoppm"):
    print("Poppler (pdftoppm) tidak ditemukan di environment path. Pastikan Poppler sudah terinstall.")
    sys.exit(1)


# ====== Cek apakah file PDF ada ======
if not os.path.exists(pdf_path):
    print(f"File PDF tidak ditemukan: {pdf_path}")
    sys.exit(1)

# ====== STEP 1: Convert PDF page ke gambar ======
try:
    images = convert_from_path(pdf_path, dpi=300)
    if len(images) < 1:
        print("PDF hanya memiliki 1 halaman. Minimal butuh 2 halaman.")
        sys.exit(1)
    page1_image = images[0]
except Exception as e:
    print("Gagal membuka PDF:", e)
    sys.exit(1)

# Simpan gambar halaman 2
page1_image_path = os.path.join(output_folder, 'page1_temp.png') if debug else 'page1_temp.png'
page1_image.save(page1_image_path, 'PNG')

# ====== STEP 2: OCR processing ======
image = cv2.imread(page1_image_path)

# Crop
x, y, w, h = 1100, 720, 400, 150
cropped_image = image[y:y+h, x:x+w]
cropped_path = os.path.join(output_folder, 'cropped_surat-keputusan.png') if debug else 'cropped_surat-keputusan.png'
cv2.imwrite(cropped_path, cropped_image)

# Grayscale, Blur, Threshold
gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh_path = os.path.join(output_folder, 'thresh_surat-keputusan.png') if debug else 'thresh_surat-keputusan.png'
cv2.imwrite(thresh_path, thresh)

# Bersihkan titik-titik kecil
inverted = cv2.bitwise_not(thresh)
contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
clean = inverted.copy()
for cnt in contours:
    if cv2.contourArea(cnt) < 50:
        cv2.drawContours(clean, [cnt], -1, (0, 0, 0), thickness=cv2.FILLED)
final_clean = cv2.bitwise_not(clean)
cleaned_path = os.path.join(output_folder, 'cleaned_image.png') if debug else 'cleaned_image.png'
cv2.imwrite(cleaned_path, final_clean)

# OCR
custom_config = r'--oem 3 --psm 6 -l ind -c tessedit_char_whitelist= 0123456789'
text = pytesseract.image_to_string(final_clean, config=custom_config)

# Bersihkan teks hasil OCR
clean_text = re.sub(r'[^0-9\s]', '', text)
text_lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
text_json = json.dumps(text_lines, ensure_ascii=False, indent=4)

# Output JSON
print(text_json)

# ====== Hapus file jika tidak debug ======
if not debug:
    for f in [page1_image_path, cropped_path, thresh_path, cleaned_path]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception as e:
                print(f"Gagal menghapus file {f}: {e}")

# ====== Selesai ======
