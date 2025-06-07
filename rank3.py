import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
from datetime import datetime
import time

class SteamGameScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.base_url = "https://store.steampowered.com"
        
    def get_top_games(self, page_count=1, category="topsellers"):
        """
        스팀에서 인기 게임 목록을 가져옵니다.
        
        Parameters:
        -----------
        page_count : int
            가져올 페이지 수 (기본값: 1)
        category : str
            카테고리 ('topsellers', 'specials', 'popularnew', 'free')
        
        Returns:
        --------
        list: 게임 정보 리스트
        """
        all_games = []
        
        for page in range(page_count):
            url = f"{self.base_url}/search/"
            params = {
                "filter": category,
                "page": page + 1,
                "cc": "US"  # 통화를 달러로 설정
            }
            
            if category == "free":
                params["maxprice"] = "free"
                params["filter"] = "topsellers"
            
            print(f"페이지 {page + 1} 수집 중...")
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                games = self._parse_games(soup)
                all_games.extend(games)
                
                # 요청 간 딜레이 (서버 부하 방지)
                time.sleep(1)
                
            except Exception as e:
                print(f"페이지 {page + 1} 수집 실패: {e}")
                
        return all_games
    
    def _parse_games(self, soup):
        """HTML에서 게임 정보를 파싱합니다."""
        games = []
        game_elements = soup.select("#search_resultsRows > a")
        
        for game_element in game_elements:
            game_data = self._extract_game_info(game_element)
            if game_data:
                games.append(game_data)
                
        return games
    
    def _extract_game_info(self, game_element):
        """개별 게임 요소에서 정보를 추출합니다."""
        try:
            game_data = {
                "rank": 0,  # 나중에 설정
                "title": "N/A",
                "price": "N/A",
                "original_price": "N/A",
                "discount": 0,
                "release_date": "N/A",
                "tags": [],
                "review_score": "N/A",
                "review_count": 0,
                "app_id": "N/A",
                "url": "N/A",
                "image_url": "N/A"
            }
            
            # 게임 URL 및 앱 ID
            game_url = game_element.get("href", "")
            game_data["url"] = game_url
            
            app_id_match = re.search(r"/app/(\d+)/", game_url)
            if app_id_match:
                game_data["app_id"] = app_id_match.group(1)
            
            # 게임 제목
            title_element = game_element.select_one(".title")
            if title_element:
                game_data["title"] = title_element.text.strip()
            
            # 게임 이미지 URL
            img_element = game_element.select_one("img")
            if img_element:
                game_data["image_url"] = img_element.get("src", "")
            
            # 가격 정보
            self._extract_price_info(game_element, game_data)
            
            # 출시일
            release_element = game_element.select_one(".search_released")
            if release_element:
                game_data["release_date"] = release_element.text.strip()
            
            # 태그
            tag_elements = game_element.select(".search_tag")
            if tag_elements:
                game_data["tags"] = [tag.text.strip() for tag in tag_elements]
            
            # 리뷰 정보
            self._extract_review_info(game_element, game_data)
            
            return game_data
            
        except Exception as e:
            print(f"게임 정보 추출 실패: {e}")
            return None
    
    def _extract_price_info(self, game_element, game_data):
        """가격 정보를 추출합니다."""
        # 할인 가격이 있는 경우
        discount_element = game_element.select_one(".discount_pct")
        if discount_element:
            discount_text = discount_element.text.strip()
            game_data["discount"] = int(re.sub(r'[^\d]', '', discount_text))
            
            original_price_element = game_element.select_one(".discount_original_price")
            if original_price_element:
                game_data["original_price"] = original_price_element.text.strip()
                
            discount_price_element = game_element.select_one(".discount_final_price")
            if discount_price_element:
                game_data["price"] = discount_price_element.text.strip()
        else:
            # 일반 가격
            price_element = game_element.select_one(".search_price")
            if price_element:
                price_text = price_element.text.strip()
                game_data["price"] = price_text
                if "Free" not in price_text and price_text != "":
                    game_data["original_price"] = price_text
    
    def _extract_review_info(self, game_element, game_data):
        """리뷰 정보를 추출합니다."""
        review_element = game_element.select_one(".search_review_summary")
        if review_element and review_element.get("data-tooltip-html"):
            tooltip = review_element["data-tooltip-html"]
            
            # 리뷰 점수
            score_match = re.search(r"([^<]+)<br>", tooltip)
            if score_match:
                game_data["review_score"] = score_match.group(1).strip()
            
            # 리뷰 수
            count_match = re.search(r"(\d+(?:,\d+)*)", tooltip)
            if count_match:
                count_str = count_match.group(1).replace(',', '')
                game_data["review_count"] = int(count_str)

class SteamDataAnalyzer:
    def __init__(self, games_data):
        self.df = pd.DataFrame(games_data)
        self._preprocess_data()
    
    def _preprocess_data(self):
        """데이터 전처리를 수행합니다."""
        # 랭킹 설정
        self.df['rank'] = range(1, len(self.df) + 1)
        
        # 가격 정보 정리
        self.df['price_numeric'] = self.df['price'].apply(self._clean_price)
        self.df['original_price_numeric'] = self.df['original_price'].apply(self._clean_price)
        
        # 리뷰 점수 수치화
        review_score_map = {
            'Overwhelmingly Positive': 10, 'Very Positive': 8, 'Positive': 7,
            'Mostly Positive': 6, 'Mixed': 5, 'Mostly Negative': 4,
            'Negative': 3, 'Very Negative': 2, 'Overwhelmingly Negative': 1
        }
        self.df['review_score_numeric'] = self.df['review_score'].map(
            lambda x: review_score_map.get(x, 0)
        )
    
    def _clean_price(self, price_str):
        """가격 문자열을 숫자로 변환합니다."""
        if pd.isna(price_str) or price_str in ["N/A", "Free to Play"] or "Free" in str(price_str):
            return 0
        
        price_match = re.search(r'[\d,.]+', str(price_str))
        if price_match:
            return float(price_match.group().replace(',', ''))
        return 0
    
    def get_top_games(self, n=10, sort_by='rank'):
        """상위 N개 게임을 반환합니다."""
        if sort_by == 'rank':
            return self.df.head(n)
        elif sort_by == 'review_score':
            return self.df.sort_values(['review_score_numeric', 'review_count'], 
                                     ascending=False).head(n)
        elif sort_by == 'price':
            return self.df.sort_values('price_numeric').head(n)
    
    def get_statistics(self):
        """데이터 통계를 반환합니다."""
        stats = {
            "total_games": len(self.df),
            "free_games": len(self.df[self.df['price_numeric'] == 0]),
            "paid_games": len(self.df[self.df['price_numeric'] > 0]),
            "games_on_sale": len(self.df[self.df['discount'] > 0]),
            "avg_price": self.df['price_numeric'].mean(),
            "avg_discount": self.df['discount'].mean(),
            "avg_review_score": self.df['review_score_numeric'].mean(),
            "most_common_tags": self._get_most_common_tags()
        }
        return stats
    
    def _get_most_common_tags(self):
        """가장 흔한 태그들을 반환합니다."""
        all_tags = []
        for tags_list in self.df['tags']:
            all_tags.extend(tags_list)
        
        if all_tags:
            tag_counts = pd.Series(all_tags).value_counts()
            return tag_counts.head(5).to_dict()
        return {}
    
    def save_data(self, filename="steam_games_ranking.csv", output_dir="./output"):
        """데이터를 CSV 파일로 저장합니다."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filepath = os.path.join(output_dir, filename)
        self.df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"데이터가 {filepath}에 저장되었습니다.")
        return filepath
    
    def create_visualizations(self, output_dir="./output"):
        """데이터 시각화를 생성합니다."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        plt.style.use('default')
        
        # 1. 상위 10개 게임 랭킹
        fig, ax = plt.subplots(figsize=(12, 8))
        top_10 = self.get_top_games(10)
        bars = ax.barh(range(len(top_10)), top_10['rank'], color='steelblue')
        ax.set_yticks(range(len(top_10)))
        ax.set_yticklabels(top_10['title'], fontsize=10)
        ax.set_xlabel('랭킹')
        ax.set_title('스팀 인기 게임 TOP 10', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        
        # 순위 표시
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'#{int(width)}', ha='left', va='center')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'top_10_games.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 가격 분포
        fig, ax = plt.subplots(figsize=(10, 6))
        paid_games = self.df[self.df['price_numeric'] > 0]
        if len(paid_games) > 0:
            ax.hist(paid_games['price_numeric'], bins=20, alpha=0.7, color='lightcoral')
            ax.set_xlabel('가격 ($)')
            ax.set_ylabel('게임 수')
            ax.set_title('유료 게임 가격 분포')
        plt.savefig(os.path.join(output_dir, 'price_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 할인율 분포
        fig, ax = plt.subplots(figsize=(10, 6))
        games_on_sale = self.df[self.df['discount'] > 0]
        if len(games_on_sale) > 0:
            ax.hist(games_on_sale['discount'], bins=15, alpha=0.7, color='lightgreen')
            ax.set_xlabel('할인율 (%)')
            ax.set_ylabel('게임 수')
            ax.set_title('할인 중인 게임의 할인율 분포')
        plt.savefig(os.path.join(output_dir, 'discount_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. 리뷰 점수 분포
        fig, ax = plt.subplots(figsize=(10, 6))
        review_games = self.df[self.df['review_score_numeric'] > 0]
        if len(review_games) > 0:
            ax.hist(review_games['review_score_numeric'], bins=10, alpha=0.7, color='gold')
            ax.set_xlabel('리뷰 점수')
            ax.set_ylabel('게임 수')
            ax.set_title('게임 리뷰 점수 분포')
        plt.savefig(os.path.join(output_dir, 'review_score_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"시각화 파일들이 {output_dir}에 저장되었습니다.")

def main():
    """메인 실행 함수"""
    print("🎮 스팀 게임 랭킹 수집기 시작!")
    print("=" * 50)
    
    # 스크래퍼 초기화
    scraper = SteamGameScraper()
    
    # 사용자 옵션
    print("수집할 카테고리를 선택하세요:")
    print("1. 인기 베스트셀러 (topsellers)")
    print("2. 할인 중인 게임 (specials)")
    print("3. 신규 인기 게임 (popularnew)")
    print("4. 무료 게임 (free)")
    
    choice = input("선택 (1-4, 기본값: 1): ").strip()
    
    category_map = {
        "1": "topsellers",
        "2": "specials", 
        "3": "popularnew",
        "4": "free"
    }
    
    category = category_map.get(choice, "topsellers")
    
    # 페이지 수 입력
    try:
        page_count = int(input("수집할 페이지 수 (기본값: 1): ") or "1")
    except ValueError:
        page_count = 1
    
    print(f"\n📊 '{category}' 카테고리에서 {page_count}페이지 수집 시작...")
    
    # 데이터 수집
    games_data = scraper.get_top_games(page_count=page_count, category=category)
    
    if not games_data:
        print("❌ 데이터를 수집할 수 없습니다.")
        return
    
    print(f"✅ {len(games_data)}개 게임 정보 수집 완료!")
    
    # 데이터 분석
    analyzer = SteamDataAnalyzer(games_data)
    
    # 통계 출력
    stats = analyzer.get_statistics()
    print("\n📈 수집 결과 통계:")
    print(f"- 총 게임 수: {stats['total_games']}")
    print(f"- 무료 게임: {stats['free_games']}")
    print(f"- 유료 게임: {stats['paid_games']}")
    print(f"- 할인 중인 게임: {stats['games_on_sale']}")
    print(f"- 평균 가격: ${stats['avg_price']:.2f}")
    print(f"- 평균 할인율: {stats['avg_discount']:.1f}%")
    print(f"- 평균 리뷰 점수: {stats['avg_review_score']:.1f}/10")
    
    # 상위 10개 게임 출력
    print("\n🏆 인기 게임 TOP 10:")
    top_10 = analyzer.get_top_games(10)
    for idx, game in top_10.iterrows():
        print(f"{game['rank']:2d}. {game['title'][:50]:<50} | {game['price']}")
    
    # 데이터 저장
    print("\n💾 데이터 저장 중...")
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"steam_{category}_ranking_{current_time}.csv"
    analyzer.save_data(filename=filename)
    
    # 시각화 생성
    print("📊 시각화 생성 중...")
    analyzer.create_visualizations()
    
    print("\n🎉 작업 완료!")
    print("생성된 파일들을 './output' 폴더에서 확인하세요.")

if __name__ == "__main__":
    main()
