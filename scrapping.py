import csv
from google_play_scraper import reviews_all

# Tentukan nama paket aplikasi (misalnya untuk aplikasi Digital Korlantas POLRI)
package_name = 'id.qoin.korlantas.user'

# Mengambil semua ulasan
reviews = reviews_all(package_name, lang='id', country='ID')

# Tentukan nama file CSV
filename = 'playstore_reviews.csv'

# Menyimpan hasil scraping ke dalam file CSV
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Menulis header kolom
    writer.writerow(['Review', 'Rating', 'User', 'Date', 'Reply'])

    # Menulis data ulasan ke file CSV
    for review in reviews:
        writer.writerow([
            review['content'],  # Isi ulasan
            review['score'],    # Rating
            review['userName'], # Nama pengguna
            review['at'],       # Tanggal
            review.get('replyContent', 'No reply')  # Balasan (jika ada)
        ])

print(f'CSV file has been saved as {filename}')
