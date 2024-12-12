import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
import time

class PlayStoreSpider(scrapy.Spider):
    name = 'playstore'
    start_urls = [
        'https://play.google.com/store/apps/details?id=id.qoin.korlantas.user&hl=id'
    ]

    def __init__(self, *args, **kwargs):
        super(PlayStoreSpider, self).__init__(*args, **kwargs)
        # Setup Chrome WebDriver menggunakan Selenium 4
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def parse(self, response):
        # Memuat halaman menggunakan Selenium
        self.driver.get(response.url)

        # Tunggu beberapa detik agar semua elemen dimuat
        time.sleep(3)

        # Mengambil data halaman setelah dimuat dengan Selenium
        html = self.driver.page_source
        selenium_response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        # Ambil ulasan dari halaman menggunakan selector Scrapy
        users = selenium_response.css('div.X5PpBb span::text').getall()  # Nama pengguna
        dates = selenium_response.css('span.bp9Aid::text').getall()  # Tanggal
        ratings = selenium_response.css('div.iXRFPc::attr(aria-label)').getall()  # Rating
        comments = selenium_response.css('div.h3YV2d span::text').getall()  # Komentar

        # Iterasi data dan yield sebagai output Scrapy
        for user, date, rating, comment in zip(users, dates, ratings, comments):
            yield {
                'user': user.strip() if user else '',
                'date': date.strip() if date else '',
                'rating': rating.strip() if rating else '',
                'comment': comment.strip() if comment else '',
            }

        # Mencari tombol untuk melihat lebih banyak ulasan dan klik jika ada
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, 'button[jsname="LgbsSe"]')
            if next_button.is_displayed():
                next_button.click()
                time.sleep(3)  # Tunggu halaman dimuat
                yield scrapy.Request(self.driver.current_url, callback=self.parse)
        except Exception as e:
            self.logger.info("Tidak ada tombol 'lihat lebih banyak' atau error: %s", str(e))

    def closed(self, reason):
        # Menutup WebDriver setelah selesai scraping
        self.driver.quit()
