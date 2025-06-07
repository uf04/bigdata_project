import requests
from bs4 import BeautifulSoup
import time

# 웹사이트의 구조가 변경되면 아래 선택자(selector)도 변경해야 할 수 있습니다.
# 스팀 상점 페이지는 자주 바뀌지 않으므로 한동안은 잘 동작할 것입니다.

# 스팀 게임 매출 순위 URL 및 선택자
TOP_SELLING_URL = 'https://store.steampowered.com/charts/topselling/KR'
TOP_SELLING_ROW_SELECTOR = 'tr[class^="weeklytopsellers_TableRow_"]'
TOP_SELLING_TITLE_SELECTOR = 'div[class^="weeklytopsellers_GameName_"]'
TOP_SELLING_PRICE_SELECTOR = 'div.salepreviewwidgets_StoreSalePriceBox_Wh0L8' # 조금 더 일반적인 선택자

# 스팀 인기 게임(최다 플레이어) 순위 URL 및 선택자
MOST_PLAYED_URL = 'https://store.steampowered.com/charts/mostplayed'
MOST_PLAYED_ROW_SELECTOR = 'tr[class^="dailyglobaltopsellers_TableRow_"]'
MOST_PLAYED_TITLE_SELECTOR = 'div[class^="dailyglobaltopsellers_GameName_"]'
MOST_PLAYED_CURRENT_SELECTOR = 'td:nth-of-type(3)' # 세 번째 'td' 태그

# 'get_top_selling_games' 함수를 아래 코드로 통째로 교체해주세요.

def get_top_selling_games():
    """스팀 최고 매출 게임 100개 정보를 가져옵니다."""
    print("\n스팀 최고 매출 게임 정보를 가져오는 중...")
    try:
        # 헤더 추가 (봇으로 인식되는 것을 방지)
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'}
        response = requests.get('https://store.steampowered.com/charts/topselling/KR', headers=headers)
        response.raise_for_status() # 오류가 발생하면 예외를 발생시킴

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- 여기가 수정된 부분입니다 ---
        # 변경된 웹사이트 구조에 맞는 새로운 CSS 선택자를 사용합니다.
        game_rows = soup.select('tr[class*="weeklytopsellers_TableRow_"]')
        
        if not game_rows:
            print("[!] 게임 목록을 찾을 수 없습니다. 스팀 웹사이트의 구조가 변경되었을 수 있습니다.")
            return []

        games_list = []
        for rank, row in enumerate(game_rows, 1):
            # 게임 제목과 가격 정보 선택자를 더 구체적으로 수정
            title_tag = row.select_one('div[class*="weeklytopsellers_GameName_"]')
            price_tag = row.select_one('div[class*="StoreSalePriceBox"]')
            
            if title_tag:
                title = title_tag.get_text(strip=True)
                # 가격 정보가 없는 경우(예: 출시 예정) 처리
                price = "가격 정보 없음"
                if price_tag:
                    price_text = price_tag.get_text(strip=True)
                    if "Free" in price_text or "무료" in price_text:
                        price = "무료"
                    else:
                        price = price_text
                
                games_list.append({'rank': rank, 'title': title, 'price': price})
        
        print("정보를 성공적으로 가져왔습니다!")
        return games_list

    except requests.exceptions.RequestException as e:
        print(f"오류: 웹사이트에 접속할 수 없습니다. ({e})")
        return None
    except Exception as e:
        print(f"오류: 데이터를 파싱하는 중 문제가 발생했습니다. ({e})")
        return None

def get_most_played_games():
    """스팀 최다 플레이어 게임 100개 정보를 가져옵니다."""
    print("\n스팀 인기 게임 정보를 가져오는 중...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(MOST_PLAYED_URL, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        game_rows = soup.select(MOST_PLAYED_ROW_SELECTOR)

        games_list = []
        rank = 1
        for row in game_rows:
            title_tag = row.select_one(MOST_PLAYED_TITLE_SELECTOR)
            current_players_tag = row.select_one(MOST_PLAYED_CURRENT_SELECTOR)

            if title_tag and current_players_tag:
                title = title_tag.get_text(strip=True)
                current_players = current_players_tag.get_text(strip=True)
                
                games_list.append({'rank': rank, 'title': title, 'current_players': current_players})
                rank += 1
        
        print("정보를 성공적으로 가져왔습니다!")
        return games_list
        
    except requests.exceptions.RequestException as e:
        print(f"오류: 웹사이트에 접속할 수 없습니다. ({e})")
        return None
    except Exception as e:
        print(f"오류: 데이터를 파싱하는 중 문제가 발생했습니다. ({e})")
        return None

def display_top_selling(games, count):
    """매출 순위 게임 목록을 출력합니다."""
    if not games:
        return
    print(f"\n======= 스팀 게임 매출 TOP {count} =======")
    for game in games[:count]:
        print(f"{game['rank']:>3}. {game['title']} - {game['price']}")
    print("=" * 35)

def display_most_played(games, count):
    """인기 게임 목록을 출력합니다."""
    if not games:
        return
    print(f"\n======= 스팀 인기 게임 TOP {count} =======")
    for game in games[:count]:
        print(f"{game['rank']:>3}. {game['title']} (현재 플레이어: {game['current_players']})")
    print("=" * 35)

def get_top_rated_games():
    """스팀 게임 평점 TOP 10 기능 (현재는 구현되지 않음)."""
    print("\n[알림]")
    print("스팀은 공식적으로 '평점 순위' 차트를 제공하지 않습니다.")
    print("이 기능은 SteamDB와 같은 외부 사이트의 정보를 가져와야 구현할 수 있으며,")
    print("해당 사이트의 정책 및 구조 변경에 매우 취약할 수 있습니다.")
    print("따라서 이 메뉴는 현재 구현되지 않은 상태입니다.")


def main():
    """메인 프로그램 루프입니다."""
    top_selling_cache = None
    most_played_cache = None
    
    while True:
        print("\n==========================")
        print("| 1. 스팀 게임 매출 TOP 100 |")
        print("| 2. 스팀 게임 매출 TOP 50  |")
        print("| 3. 스팀 게임 매출 TOP 10  |")
        print("| 4. 스팀 인기 게임 TOP 100 |")
        print("| 5. 스팀 인기 게임 TOP 50  |")
        print("| 6. 스팀 인기 게임 TOP 10  |")
        print("| 7. 스팀 게임 평점 TOP 10  |")
        print("| 0. 프로그램 종료          |")
        print("==========================")
        
        choice = input("[원하시는 서비스에 해당하는 번호를 입력하세요.]: ")

        if choice == '1':
            if not top_selling_cache:
                top_selling_cache = get_top_selling_games()
            display_top_selling(top_selling_cache, 100)
        elif choice == '2':
            if not top_selling_cache:
                top_selling_cache = get_top_selling_games()
            display_top_selling(top_selling_cache, 50)
        elif choice == '3':
            if not top_selling_cache:
                top_selling_cache = get_top_selling_games()
            display_top_selling(top_selling_cache, 10)
        elif choice == '4':
            if not most_played_cache:
                most_played_cache = get_most_played_games()
            display_most_played(most_played_cache, 100)
        elif choice == '5':
            if not most_played_cache:
                most_played_cache = get_most_played_games()
            display_most_played(most_played_cache, 50)
        elif choice == '6':
            if not most_played_cache:
                most_played_cache = get_most_played_games()
            display_most_played(most_played_cache, 10)
        elif choice == '7':
            get_top_rated_games()
        elif choice == '0':
            print("\n프로그램을 종료합니다. 이용해주셔서 감사합니다.")
            break
        else:
            print("\n[!] 잘못된 입력입니다. 0부터 7까지의 숫자 중 하나를 입력해주세요.")
            
        # 다음 입력을 위해 잠시 대기
        time.sleep(1)

if __name__ == "__main__":
    main()