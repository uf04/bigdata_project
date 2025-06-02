import requests
from bs4 import BeautifulSoup

url = "https://store.steampowered.com/search/?filter=topsellers"
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

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
