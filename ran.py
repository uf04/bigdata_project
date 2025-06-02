from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_steam_top_games_selenium(count=20):
    options = Options()
    options.add_argument('--headless')  # 창 없이 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())  # ✅ 여기에 따로 전달
    driver = webdriver.Chrome(service=service, options=options)

    url = 'https://store.steampowered.com/search/?sort_by=_ASC&supportedlang=koreana&filter=topsellers'
    driver.get(url)
    time.sleep(3)  # 페이지 로딩 대기

    results = driver.find_elements(By.CLASS_NAME, 'search_result_row')

    for i, result in enumerate(results[:count], start=1):
        title = result.find_element(By.CLASS_NAME, 'title').text.strip()
        try:
            price = result.find_element(By.CLASS_NAME, 'search_price').text.strip()
        except:
            price = '가격 정보 없음'
        print(f"{i}. {title} - {price}")

    driver.quit()

# ✅ 실행
get_steam_top_games_selenium(20)

