import requests
from bs4 import BeautifulSoup # HTML 파싱을 위한 라이브러리


def get_top_sellers(count=10):
    """지정한 수만큼 스팀 최고 인기 게임 목록을 가져옵니다."""
    url = f"https://store.steampowered.com/api/featuredcategories/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 오류 발생 시 예외 처리
        data = response.json()
        
        # 'top_sellers' 카테고리에서 게임 목록 추출
        top_sellers = data.get('top_sellers', {}).get('items', [])
        
        print(f"--- 스팀 인기 게임 TOP {count} ---")
        for i, game in enumerate(top_sellers[:count]):
            print(f"{i+1}. {game['name']}")

    except requests.exceptions.RequestException as e:
        print(f"오류가 발생했습니다: {e}")

# --- 메뉴 선택에 따른 함수 호출 (예시) ---
get_top_sellers(100)
#get_top_sellers(50)
#get_top_sellers(10)

def get_top_discounts(count=10):
    """할인율이 가장 높은 스팀 게임 목록을 가져옵니다."""
    # 검색 조건: 할인 중인 게임, Windows 지원, 출시된 제품
    url = f"https://store.steampowered.com/search/results/?query&sort_by=Price_ASC&specials=1&os=win&filter=topsellers&count={count}"
    headers = {'Accept-Language': 'ko-KR,ko;q=0.9'} # 한글로 된 게임 제목을 보기 위함

    try:
        # 실제로는 HTML을 파싱해야 하지만, API가 있다면 아래와 같은 형태로 데이터를 가져올 수 있습니다.
        # 이 예시에서는 가상의 API 응답을 가정합니다.
        # 실제 구현을 위해서는 BeautifulSoup 같은 라이브러리로 HTML을 직접 파싱해야 합니다.
        
        # 가상 데이터
        mock_games = [
            {'name': 'Game A', 'discount_percent': 90, 'final_formatted': '₩ 1,000'},
            {'name': 'Game B', 'discount_percent': 85, 'final_formatted': '₩ 5,000'},
            {'name': 'Game C', 'discount_percent': 80, 'final_formatted': '₩ 12,000'},
            # ...
        ]
        
        print(f"--- 스팀 할인률 TOP {count} ---")
        # 할인율이 높은 순으로 정렬 (가상)
        sorted_games = sorted(mock_games, key=lambda x: x['discount_percent'], reverse=True)

        for i, game in enumerate(sorted_games[:count]):
            print(f"{i+1}. {game['name']} ({game['discount_percent']}% 할인) - {game['final_formatted']}")

    except requests.exceptions.RequestException as e:
        print(f"오류가 발생했습니다: {e}")


get_top_discounts(10)


def get_top_rated_games(count=10):
    """사용자 평점이 가장 높은 스팀 게임 목록을 가져옵니다."""
    # 검색 조건: 사용자 평가 순 정렬
    url = f"https://store.steampowered.com/search/?sort_by=Reviews_DESC&filter=topsellers&os=win&page=1"
    headers = {'Accept-Language': 'ko-KR,ko;q=0.9'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        games = soup.select('#search_resultsRows > a')
        
        print(f"--- 스팀 게임 평점 TOP {count} ---")
        for i, game_html in enumerate(games[:count]):
            title = game_html.select_one('.title').text.strip()
            
            # 리뷰 요약 정보 추출
            review_summary_span = game_html.select_one('.search_review_summary')
            review_summary = review_summary_span['data-tooltip-html'].replace('<br>', ' | ') if review_summary_span else "평가 정보 없음"
            
            print(f"{i+1}. {title} ({review_summary})")

    except requests.exceptions.RequestException as e:
        print(f"오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"데이터를 파싱하는 중 오류가 발생했습니다: {e}")

get_top_rated_games(10)

def main():
    while True:
        print("\n==========================")
        print("| 1. 스팀 인기 게임 TOP 100 |")
        print("| 2. 스팀 인기 게임 TOP 50  |")
        print("| 3. 스팀 인기 게임 TOP 10  |")
        print("| 4. 스팀 할인률 TOP 10     |")
        print("| 5. 스팀 게임 평점 TOP 10  |")
        print("| 6. 종료                 |")
        print("==========================")
        
        choice = input("[원하시는 서비스에 해당하는 번호를 입력하세요.]: ")
        
        if choice == '1':
            get_top_sellers(100)
        elif choice == '2':
            get_top_sellers(50)
        elif choice == '3':
            get_top_sellers(10)
        elif choice == '4':
            get_top_discounts(10)
        elif choice == '5':
            get_top_rated_games(10)
        elif choice == '6':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 시도해주세요.")

if __name__ == "__main__":
    main()