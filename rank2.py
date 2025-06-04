from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time

# 크롬 옵션 설정
options = Options()
options.add_argument("--headless")  # 브라우저 창 안 띄움
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 스팀 통계 페이지 열기
driver.get("https://store.steampowered.com/stats/")
time.sleep(3)  # 페이지 로딩 대기

# HTML 가져오기
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# 테이블 파싱
table = soup.find('table', {'id': 'detailStats'})
rows = table.find_all('tr')[1:11]

print("Steam 인기 게임 순위 (Most Played - Top 10):\n")

for i, row in enumerate(rows, 1):
    cols = row.find_all('td')
    current_players = cols[0].get_text(strip=True)
    peak_today = cols[1].get_text(strip=True)
    name = cols[3].get_text(strip=True)
    print(f"{i}. {name} - 현재 플레이어 수: {current_players}, 오늘 최고: {peak_today}")
