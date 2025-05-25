from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# Chrome 드라이버 옵션 설정
options = Options()
options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Chrome 드라이버 경로 설정 (자신의 환경에 맞게 수정)
driver_path = 'C:/chromedriver.exe'  # 예: 'C:/chromedriver.exe' 또는 '/usr/local/bin/chromedriver'

# Service 객체 생성
service = Service(executable_path=driver_path)

# Chrome 드라이버 실행
driver = webdriver.Chrome(service=service, options=options)

# 모바일인덱스 실시간 게임 순위 페이지 접속
url = 'https://www.mobileindex.com/mi-chart/realtime-rank'
driver.get(url)

# 페이지 로딩 대기
time.sleep(10)  # 필요에 따라 조정

# 순위 데이터 추출
ranks = []
try:
    # 순위 항목들을 포함하는 요소 찾기
    rank_elements = driver.find_elements(By.CSS_SELECTOR, '.ranking-item')  # 실제 클래스명은 페이지 구조에 따라 다를 수 있음

    for elem in rank_elements[:100]:  # 상위 100개 항목만 추출
        rank = elem.find_element(By.CSS_SELECTOR, '.rank-number').text
        app_name = elem.find_element(By.CSS_SELECTOR, '.app-name').text
        company = elem.find_element(By.CSS_SELECTOR, '.company-name').text
        ranks.append({
            'rank': rank,
            'app_name': app_name,
            'company': company
        })
finally:
    driver.quit()

# 결과 출력
for item in ranks:
    print(f"{item['rank']}위: {item['app_name']} ({item['company']})")