from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Chrome 드라이버 설정
options = Options()
options.add_argument("--headless=new")  # 최신 headless 모드
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--remote-debugging-port=9222")

# ChromeDriver 자동 설치
service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=options)

driver.get("https://store.steampowered.com/search/?filter=topsellers")
time.sleep(3)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

games = soup.select(".search_result_row")

for i, game in enumerate(games[:10], 1):
    title = game.select_one(".title").text.strip()
    price_tag = game.select_one(".search_price")
    
    if price_tag:
        price = price_tag.get_text(separator=" ", strip=True)
        if not price:
            price = "무료"
    else:
        price = "정보 없음"

    print(f"{i}. {title} - 가격: {price}")

driver.quit()
