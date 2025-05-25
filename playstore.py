import requests
from bs4 import BeautifulSoup

# 스크래핑할 URL
url = "https://play.google.com/store/games?device=phone&hl=ko"

# HTTP 요청 보내기
response = requests.get(url)

# 응답 상태 확인
if response.status_code == 200:
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 랭킹 정보가 있는 요소 찾기 (예시: class 이름이 'ranking'인 요소)
    rankings = soup.find_all('div', class_='ranking')  # 이 부분은 실제 HTML 구조에 따라 달라짐

    # 랭킹 정보 출력
    for rank in rankings:
        print(rank.text)

else:
    print("HTTP 요청 실패:", response.status_code)

print("hello, world")