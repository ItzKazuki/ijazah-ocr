import os
import cv2
from pdf2image import convert_from_path
from PIL import Image

def convert_pdf_to_images(pdf_path, output_folder, debug=False):
    """
    Mengonversi PDF menjadi gambar, memproses halaman kedua, dan menyimpan hasil akhir.
    """
    try:
        # Konversi PDF ke gambar
        images = convert_from_path(pdf_path, dpi=300)
        if len(images) < 2:
            print(f"PDF {pdf_path} hanya memiliki 1 halaman. Minimal butuh 2 halaman.")
            return None
        
        # Simpan halaman kedua sebagai gambar sementara
        page2_image = images[1]
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        page2_image_path = os.path.join(output_folder, f'{base_filename}_page2.png')
        page2_image.save(page2_image_path, 'PNG')

        # ====== STEP 2: OCR processing ======
        image = cv2.imread(page2_image_path)

        # Crop
        x, y, w, h = 1050, 340, 900, 500
        cropped_image = image[y:y+h, x:x+w]
        cropped_path = os.path.join(output_folder, f'{base_filename}_cropped.png')
        cv2.imwrite(cropped_path, cropped_image)

        # Grayscale, Blur, Threshold
        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh_path = os.path.join(output_folder, f'{base_filename}_thresh.png')
        cv2.imwrite(thresh_path, thresh)

        # Bersihkan titik-titik kecil
        inverted = cv2.bitwise_not(thresh)
        contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        clean = inverted.copy()
        for cnt in contours:
            if cv2.contourArea(cnt) < 50:
                cv2.drawContours(clean, [cnt], -1, (0, 0, 0), thickness=cv2.FILLED)
        final_clean = cv2.bitwise_not(clean)
        cleaned_path = os.path.join(output_folder, f'{base_filename}_cleaned.png')
        cv2.imwrite(cleaned_path, final_clean)

        # Simpan gambar final
        final_image = Image.open(cleaned_path).convert("RGB")
        final_image_path = os.path.join(output_folder, f'{base_filename}_final.png')
        final_image.save(final_image_path, 'PNG')

        return final_image_path
    except Exception as e:
        print(f"Gagal memproses PDF {pdf_path}: {e}")
        return None

def process_pdf_folder(folder_path, output_folder, debug=False):
    """
    Membaca semua file PDF di folder tertentu dan memprosesnya.
    """
    if not os.path.exists(folder_path):
        print(f"Folder tidak ditemukan: {folder_path}")
        return

    if debug and not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("Tidak ada file PDF di folder.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        print(f"Memproses file: {pdf_path}")
        final_image_path = convert_pdf_to_images(pdf_path, output_folder, debug)
        if final_image_path:
            print(f"Gambar final disimpan di: {final_image_path}")
        else:
            print(f"Gagal memproses file: {pdf_path}")

# Contoh penggunaan
if __name__ == "__main__":
    folder_path = "C:/Users/ASUS/Downloads/IJAZAH KLS XII ANIMASI"  # Ganti dengan path folder PDF Anda
    output_folder = "d:/coding/ijazah-ocr/train/images"  # Ganti dengan path folder output
    debug = True  # Ubah ke False jika tidak ingin menyimpan file sementara
    process_pdf_folder(folder_path, output_folder, debug)

