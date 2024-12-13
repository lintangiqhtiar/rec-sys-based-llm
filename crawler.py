# Chrome driver
chrome_driver = '../chromedriver'

# URL for app collection
URL = 'https://play.google.com/store/apps/details?id=id.qoin.korlantas.user&hl=id'

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from time import sleep
import random
import pandas as pd
import re
from selenium.webdriver.chrome.options import Options

# 스크롤을 내리는 function (불러오기 포함, 최하단으로)
def scroll(model):
    try:        
        last_height = driver.execute_script("return arguments[0].scrollHeight", model)
        while True:
            # 아무 숫자 넣어도 됩니다. 약 0.5~2초 사이면 될듯 시간 아까우니
            pause = 1.5

            # 최하단까지 스크롤
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", model)
            time.sleep(pause)

            # 끝까지 스크롤을 하기 위한 위치조정
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight-50);", model)
            time.sleep(pause)

            # 스크롤 높이 측정
            new_height = driver.execute_script("return arguments[0].scrollHeight", model)

            try:
                # '더보기' 버튼 경우
                all_review_button = driver.find_element_by_xpath('/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/div[2]/div/span/span').click()
            except:
                # 스크롤 완료 경우
                if new_height == last_height:
                    break
                last_height = new_height
                
    except Exception as e:
        print("terjadi kesalahan: ", e)

# Setting Chrome Drivers dengan Selenium 4.x+
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-gpu')  # Menonaktifkan GPU untuk menghindari error DirectComposition

# Inisialisasi driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.maximize_window()

# Membuka URL
driver.get(URL)

# 페이지 로딩 대기
wait = WebDriverWait(driver, 15)

# '리뷰 모두 보기' 버튼 렌더링 확인(2022-08-08 selenium 새버전으로 고침)
all_review_button_xpath = '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[2]/div/div[1]/div[1]/c-wiz[5]/section/div/div[2]/div[5]/div/div/button/span'
button_loading_wait = wait.until(EC.element_to_be_clickable((By.XPATH, all_review_button_xpath)))

# '리뷰 모두 보기' 버튼 클릭 (2022-08-08 xpath 재설정)
driver.find_element("xpath", all_review_button_xpath).click()
all_review_page_xpath = '//*[@id="yDmH0d"]/div[6]/div[2]/div/div/div/div/div[2]/div'
page_loading_wait = wait.until(EC.element_to_be_clickable((By.XPATH, all_review_page_xpath)))

# acroll halaman
model = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yDmH0d"]/div[6]/div[2]/div/div/div/div/div[2]')))
scroll(model)

# html parsing
html_source = driver.page_source
soup_source = BeautifulSoup(html_source, 'html.parser')
# 크롬 드라이버 종료
driver.quit()

# html 데이터 저장
with open("../dataset/data_html.html", "w", encoding = 'utf-8') as file:
    file.write(str(soup_source))

# 리뷰 데이터 클래스 설정
review_source = soup_source.find_all(class_ = 'RHo1pe')
# 필요한 Value들 설정
dataset = []
review_num = 0 
# 스크랩한 전체 리뷰정보 추출
for review in review_source:
    review_num+=1
    # 리뷰 등록일
    date_full = review.find_all(class_ = 'bp9Aid')[0].text
    # 닉네임
    user_name = review.find_all(class_ = 'X5PpBb')[0].text 
    # 평점 (여섯번째 단어가 평점 숫자)
    rating = review.find_all(class_ = "iXRFPc")[0]['aria-label'][10]
    # 리뷰 (컨텐츠)
    content = review.find_all(class_ = 'h3YV2d')[0].text # 리뷰 데이터 추출

    data = {
        "id": review_num, 
        "date": date_full,
        "rating": rating,
        "userName": user_name,
        "content": content
    }
    dataset.append(data)

df_crawl = pd.DataFrame(dataset)
df_crawl.to_csv('../dataset/review_dataset.csv', encoding = 'utf-8-sig') # csv 파일로 저장

# 저장한 리뷰 정보 불러오기
df_crawl = pd.read_csv('../dataset/review_dataset.csv', encoding = 'utf-8-sig')
df_crawl = df_crawl.drop(['Unnamed: 0'], axis = 1)
print(df_crawl)