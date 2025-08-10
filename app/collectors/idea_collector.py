import feedparser
from pytrends.request import TrendReq
from typing import List, Dict, Set

class IdeaCollector:
    def collect_trending_topics(self) -> List[Dict]:
        """
        다양한 소스에서 트렌드 토픽을 수집하고, 중복을 제거하여 반환합니다.
        """
        ideas = []
        # ideas.extend(self.get_google_trends()) # Google Trends API 404 오류로 임시 비활성화
        ideas.extend(self.get_rss_feeds([
            'https://feeds.feedburner.com/oreilly/radar',
            'https://www.wired.com/feed/',
            'https://techcrunch.com/feed/',
            'https://www.theverge.com/rss/index.xml'
        ]))
        # ideas.extend(self.get_reddit_hot_topics())
        # ideas.extend(self.get_hackernews_trends())
        return self._deduplicate_and_score(ideas)

    def get_google_trends(self, region: str = 'US') -> List[Dict]:
        """Google Trends에서 최신 트렌드를 가져옵니다."""
        print("Fetching Google Trends...")
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            trending_searches_df = pytrends.trending_searches(pn='US') # Changed to US
            trends = trending_searches_df[0].tolist()
            return [{'title': trend, 'source': 'Google Trends'} for trend in trends]
        except Exception as e:
            print(f"Error fetching Google Trends: {e}")
            return []

    def get_rss_feeds(self, feed_urls: List[str]) -> List[Dict]:
        """주어진 RSS 피드 목록에서 최신 게시물을 가져옵니다."""
        print(f"Fetching RSS feeds...")
        ideas = []
        for url in feed_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    ideas.append({'title': entry.title, 'source': feed.feed.title, 'link': entry.link})
            except Exception as e:
                print(f"Error fetching RSS feed {url}: {e}")
        return ideas

    def _deduplicate_and_score(self, ideas: List[Dict]) -> List[Dict]:
        """아이디어를 중복 제거하고 점수를 매깁니다."""
        print(f"Deduplicating and scoring {len(ideas)} ideas...")
        unique_ideas: List[Dict] = []
        seen_titles: Set[str] = set()

        for idea in ideas:
            if idea['title'] not in seen_titles:
                idea['score'] = 1.0  # 기본 점수
                unique_ideas.append(idea)
                seen_titles.add(idea['title'])
        
        print(f"Found {len(unique_ideas)} unique ideas.")
        return unique_ideas

if __name__ == '__main__':
    collector = IdeaCollector()
    trending_ideas = collector.collect_trending_topics()
    print("\n--- Collected Ideas ---")
    for idea in trending_ideas:
        print(f"- {idea['title']} (Source: {idea['source']})")

