import shutil
import cv2
import re
import json
import sys
import os
from pdf2image import convert_from_path
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

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

# Cek apakah file PDF ada
if not os.path.exists(pdf_path):
    print(f"File PDF tidak ditemukan: {pdf_path}")
    sys.exit(1)

# ====== STEP 1: Convert PDF page ke gambar ======
try:
    images = convert_from_path(pdf_path, dpi=300)
    if len(images) < 2:
        print("PDF hanya memiliki 1 halaman. Minimal butuh 2 halaman.")
        sys.exit(1)
    page2_image = images[1]
except Exception as e:
    print("Gagal membuka PDF:", e)
    sys.exit(1)

# Simpan gambar halaman 2
page2_image_path = os.path.join(output_folder, 'page2_temp.png') if debug else 'page2_temp.png'
page2_image.save(page2_image_path, 'PNG')

# ====== STEP 2: OCR processing ======
image = cv2.imread(page2_image_path)

# Crop
x, y, w, h = 1050, 340, 900, 500
cropped_image = image[y:y+h, x:x+w]
cropped_path = os.path.join(output_folder, 'cropped_ijazah.png') if debug else 'cropped_ijazah.png'
cv2.imwrite(cropped_path, cropped_image)

# Grayscale, Blur, Threshold
gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh_path = os.path.join(output_folder, 'thresh_ijazah.png') if debug else 'thresh_ijazah.png'
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

# ====== STEP 3: OCR dengan TrOCR ======
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# Buka gambar yang sudah dibersihkan
final_image = Image.open(cleaned_path).convert("RGB")

# Lakukan OCR
pixel_values = processor(images=final_image, return_tensors="pt").pixel_values
generated_ids = model.generate(pixel_values)
text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

# Bersihkan teks hasil OCR
clean_text = re.sub(r'[^A-Za-z0-9\s]', '', text)
text_lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
text_json = json.dumps(text_lines, ensure_ascii=False, indent=4)

# Output JSON
print(text_json)

# ====== Hapus file jika tidak debug ======
if not debug:
    for f in [page2_image_path, cropped_path, thresh_path, cleaned_path]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception as e:
                print(f"Gagal menghapus file {f}: {e}")

# ====== Selesai ======
