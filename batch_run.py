import os
import subprocess

PDF_FOLDER = (
    # "/home/kazuki/Desktop/tatausaha/IJAZAH KLS XII RPL",  # ganti sesuai folder kamu
    "/home/kazuki/Downloads/IJAZAH KLS XII RPL 1"
)

# Ambil semua file PDF

for filename in os.listdir(PDF_FOLDER):
    if filename.lower().endswith(".pdf"):
        file_path = os.path.join(PDF_FOLDER, filename)
        print(f"🔍 Memproses: {filename}")

        subprocess.run(["python3", "ijazah-pdf-new.py", file_path, "--page", "2"])


# new

# import os
# import subprocess
# from rapidfuzz import process, fuzz

# PDF_FOLDER = (
#     "/home/kazuki/Desktop/tatausaha/IJAZAH KLS XII RPL",
# )  # ganti sesuai folder kamu
# DAFTAR_NAMA_FILE = "daftar_nama_RPL_2021.txt"
# THRESHOLD = 85  # Batas kemiripan minimal (0-100)

# # Load daftar nama referensi
# with open(DAFTAR_NAMA_FILE, encoding="utf-8") as f:
#     daftar_nama = [line.strip().upper() for line in f if line.strip()]

# nama_terbaca = set()
# nama_ocr_raw = []

# for filename in os.listdir(PDF_FOLDER):
#     if filename.lower().endswith(".pdf"):
#         file_path = os.path.join(PDF_FOLDER, filename)
#         print(f"🔍 Memproses: {filename}")

#         # Jalankan script dan ambil output
#         result = subprocess.run(
#             ["python3", "ijazah-pdf-new.py", file_path, "--page", "2"],
#             capture_output=True,
#             text=True,
#         )
#         # Cari baris yang diawali dengan 'Nama:'
#         for line in result.stdout.splitlines():
#             if line.strip().startswith("Nama:"):
#                 nama_ocr = line.replace("Nama:", "").strip().upper()
#                 nama_ocr_raw.append(nama_ocr)
#                 # Fuzzy matching ke daftar nama
#                 match, score, _ = process.extractOne(
#                     nama_ocr, daftar_nama, scorer=fuzz.token_sort_ratio
#                 )
#                 if score >= THRESHOLD:
#                     nama_terbaca.add(match)

# # Analisis hasil
# terbaca = set(nama_terbaca)
# tidak_terbaca = set(daftar_nama) - terbaca

# print("\n=== REKAP ===")
# print(f"Total nama di daftar: {len(daftar_nama)}")
# print(f"Terbaca di output: {len(terbaca)}")
# print(f"Tidak terbaca: {len(tidak_terbaca)}")
# print("\nNama yang tidak terbaca:")
# for nama in sorted(tidak_terbaca):
#     print(nama)

# print("\nNama hasil OCR yang tidak match threshold:")
# for nama_ocr in nama_ocr_raw:
#     match, score, _ = process.extractOne(
#         nama_ocr, daftar_nama, scorer=fuzz.token_sort_ratio
#     )
#     if score < THRESHOLD:
#         print(f"{nama_ocr} (kemiripan {score}%) -> kemungkinan: {match}")
