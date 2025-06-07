import requests
from bs4 import BeautifulSoup
import time

# 웹사이트의 구조가 변경되면 아래 선택자(selector)들은 동작하지 않을 수 있습니다.
# 이 코드는 학습 목적으로 작성되었습니다. (2025년 6월 기준)

# HTTP 요청 시 사용자 에이전트(User-Agent)를 설정하여 차단을 피합니다.
HEADERS = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}

def get_top_played_games(limit):
    """스팀 동시 접속자 수 기준 인기 게임 순위를 가져옵니다."""
    url = "https://store.steampowered.com/charts/mostplayed"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        # [수정됨] 현재 스팀 페이지 구조에 맞는 새로운 선택자로 변경
        game_rows = soup.select("tr._3sNv_-650xY1R0X-wD-J_") 

        if not game_rows:
            print("오류: 게임 목록을 찾을 수 없습니다. 스팀 웹사이트의 구조가 변경되었을 수 있습니다.")
            return

        print(f"\n--- 스팀 동시 접속자 수 TOP {limit} ---\n")

        for i, row in enumerate(game_rows[:limit]):
            rank = i + 1
            
            # [수정됨] 게임 이름과 현재 접속자 수 선택자 변경
            game_name_element = row.select_one("div.XFdLdY_1c1G9a-i_2gUz_")
            current_players_element = row.select_one("div.C5X6j2e_uTYG6_S7dI5nU")

            # 요소가 존재하는지 확인 후 텍스트 추출
            if game_name_element and current_players_element:
                game_name = game_name_element.text.strip()
                current_players = current_players_element.text.strip()
                print(f"[{rank}위] {game_name} - 현재 접속자: {current_players}명")
            else:
                print(f"[{rank}위] 정보를 가져오는 데 실패했습니다.")
            
            time.sleep(0.1)

    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지를 가져올 수 없습니다. (에러: {e})")
    except Exception as e:
        print(f"오류: 데이터를 파싱하는 중 문제가 발생했습니다. (에러: {e})")


def get_top_discounts(limit=10):
    """스팀 할인율 TOP 10 게임 순위를 가져옵니다."""
    # specials=1 파라미터는 할인 중인 게임만 보여줍니다.
    url = "https://store.steampowered.com/search/?specials=1"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        game_rows = soup.select("a.search_result_row")

        print(f"\n--- 스팀 할인율 TOP {limit} ---\n")
        
        count = 0
        for row in game_rows:
            if count >= limit:
                break

            discount_span = row.select_one("div.search_discount > span")
            # 할인율 정보가 있는 게임만 처리합니다.
            if discount_span:
                game_name = row.select_one("span.title").text.strip()
                discount_pct = discount_span.text.strip()
                original_price = row.select_one("div.search_price > span > strike").text.strip()
                discounted_price = row.select_one("div.search_price").contents[-1].strip()

                print(f"[{discount_pct}] {game_name}")
                print(f"    └ 가격: {original_price} → {discounted_price}\n")
                
                count += 1
                time.sleep(0.1)

    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지를 가져올 수 없습니다. (에러: {e})")
    except Exception as e:
        print(f"오류: 데이터를 파싱하는 중 문제가 발생했습니다. (에러: {e})")


def get_top_rated_games(limit=10):
    """스팀 사용자 평가 TOP 10 게임 순위를 가져옵니다."""
    # sort_by=Reviews_DESC 파라미터는 긍정적 평가 순으로 정렬합니다.
    url = "https://store.steampowered.com/search/?sort_by=Reviews_DESC"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        game_rows = soup.select("a.search_result_row")
        
        print(f"\n--- 스팀 사용자 평가 TOP {limit} ---\n")

        for i, row in enumerate(game_rows[:limit]):
            rank = i + 1
            game_name = row.select_one("span.title").text.strip()
            review_summary_span = row.select_one("span.search_review_summary")
            
            if review_summary_span:
                review_summary = review_summary_span.get('data-tooltip-html', '평가 정보 없음').replace('<br>', ' | ')
            else:
                review_summary = "평가 정보 없음"

            print(f"[{rank}위] {game_name}\n    └ 평가: {review_summary}\n")
            time.sleep(0.1)

    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지를 가져올 수 없습니다. (에러: {e})")
    except Exception as e:
        print(f"오류: 데이터를 파싱하는 중 문제가 발생했습니다. (에러: {e})")


def main():
    """메인 실행 함수"""
    while True:
        print("\n==========================")
        print("| 1. 스팀 인기 게임 TOP 100 |")
        print("| 2. 스팀 인기 게임 TOP 50  |")
        print("| 3. 스팀 인기 게임 TOP 10  |")
        print("| 4. 스팀 할인률 TOP 10     |")
        print("| 5. 스팀 게임 평점 TOP 10  |")
        print("| 6. 프로그램 종료          |")
        print("==========================")
        
        choice = input("[원하시는 서비스에 해당하는 번호를 입력하세요.]: ")

        if choice == '1':
            get_top_played_games(100)
        elif choice == '2':
            get_top_played_games(50)
        elif choice == '3':
            get_top_played_games(10)
        elif choice == '4':
            get_top_discounts(10)
        elif choice == '5':
            get_top_rated_games(10)
        elif choice == '6':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 번호입니다. 1부터 6 사이의 숫자를 입력해주세요.")

if __name__ == "__main__":
    main()