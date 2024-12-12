import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Mengatur driver Chrome."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

def buka_halaman(driver, url):
    """Membuka halaman Play Store."""
    driver.get(url)
    time.sleep(5)

def klik_tombol_lihat_semua_ulasan(driver):
    """Klik tombol 'Lihat Semua Ulasan'."""
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Lihat semua ulasan"]'))
        )
        button.click()
        print("Tombol 'Lihat Semua Ulasan' berhasil diklik.")
        time.sleep(3)
    except Exception as e:
        print("Gagal mengklik tombol 'Lihat Semua Ulasan':", e)

def scroll_popup(driver, popup_element, max_scroll=20):
    """Melakukan scroll pada pop-up hingga batas tertentu."""
    last_height = driver.execute_script("return arguments[0].scrollHeight", popup_element)
    for i in range(max_scroll):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", popup_element)
        print(f"Scroll ke-{i + 1}")
        time.sleep(3)  # Tunggu lebih lama untuk lazy loading
        new_height = driver.execute_script("return arguments[0].scrollHeight", popup_element)
        if new_height == last_height:
            print("Sudah mencapai akhir ulasan.")
            break
        last_height = new_height

def ambil_data_ulasan(driver, popup_selector, output_file):
    """Mengambil data ulasan dan menyimpannya ke file CSV."""
    try:
        popup = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, popup_selector))
        )
        print("Pop-up ulasan berhasil ditemukan.")

        # File CSV untuk menyimpan data
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Nama Akun', 'Rating', 'Tanggal', 'Komentar'])

            # Scroll dan ambil data
            scroll_popup(driver, popup)

            # Ambil semua elemen ulasan
            reviews = driver.find_elements(By.XPATH, '//div[contains(@jscontroller, "H6eOGe")]')
            print(f"Jumlah ulasan ditemukan: {len(reviews)}")

            # Loop untuk mengambil data ulasan
            for idx, review in enumerate(reviews, start=1):
                try:
                    print(f"Mengambil data ulasan ke-{idx}")
                    name = review.find_element(By.CSS_SELECTOR, 'span.X5PpBb').text
                    rating = review.find_element(By.CSS_SELECTOR, 'div.iXRFPc > div').get_attribute('aria-label')
                    date = review.find_element(By.CSS_SELECTOR, 'span.bp9Aid').text
                    comment = review.find_element(By.CSS_SELECTOR, 'div[class="h3YV2d"]').text

                    # Simpan data ke CSV
                    writer.writerow([name, rating, date, comment])
                except Exception as e:
                    print(f"Error saat mengambil data ulasan ke-{idx}: {e}")

    except Exception as e:
        print("Gagal menemukan atau memproses pop-up ulasan:", e)


def main():
    url = 'https://play.google.com/store/apps/details?id=id.qoin.korlantas.user&hl=id'
    output_file = 'komentar_digital_korlantas.csv'
    popup_selector = 'div[role="dialog"]'  # Selector alternatif

    driver = setup_driver()
    try:
        buka_halaman(driver, url)
        klik_tombol_lihat_semua_ulasan(driver)
        ambil_data_ulasan(driver, popup_selector, output_file)
    finally:
        driver.quit()
        print("Driver ditutup.")

if __name__ == "__main__":
    main()
