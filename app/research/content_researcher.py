import wikipedia
from newsapi import NewsApiClient
from typing import Dict, Any, List
from app.config import Config

class ContentResearcher:
    def research_topic(self, topic: str) -> Dict[str, Any]:
        """주어진 주제에 대해 리서치를 수행하고 데이터를 반환합니다."""
        research_data = {
            'topic': topic,
            'key_facts': [],
            'recent_developments': [],
            'sources': []
        }

        wikipedia_summary, wikipedia_source = self._get_wikipedia_summary(topic)
        if wikipedia_summary:
            research_data['key_facts'].append(wikipedia_summary)
            if wikipedia_source:
                research_data['sources'].append(wikipedia_source)

        news_articles, news_sources = self._get_news_articles(topic)
        research_data['recent_developments'].extend(news_articles)
        research_data['sources'].extend(news_sources)

        return research_data

    def _get_wikipedia_summary(self, topic: str) -> (str | None, str | None):
        """Wikipedia에서 주제에 대한 요약 정보와 소스 URL을 가져옵니다."""
        print(f"Researching Wikipedia for '{topic}'...")
        try:
            page = wikipedia.page(topic, auto_suggest=False, redirect=True)
            summary = page.summary.split('\n')[0]
            return summary, page.url
        except wikipedia.exceptions.PageError:
            print(f"Wikipedia page for '{topic}' not found.")
            return None, None
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Disambiguation error for '{topic}'. Trying '{e.options[0]}'...")
            if e.options:
                return self._get_wikipedia_summary(e.options[0])
            return None, None
        except Exception as e:
            print(f"An error occurred with Wikipedia search: {e}")
            return None, None

    def _get_news_articles(self, topic: str) -> (List[Dict], List[str]):
        """News API에서 최신 뉴스 기사를 가져옵니다."""
        print(f"Researching News API for '{topic}'...")
        if not Config.NEWS_API_KEY:
            print("News API key is not configured. Skipping.")
            return [], []

        articles_found = []
        sources_found = []
        try:
            newsapi = NewsApiClient(api_key=Config.NEWS_API_KEY)
            # top_headlines = newsapi.get_top_headlines(q=topic, language='en', page_size=5)
            all_articles = newsapi.get_everything(q=topic, language='en', sort_by='popularity', page_size=5)
            
            print(f"Found {len(all_articles['articles'])} articles from News API.")

            for article in all_articles['articles']:
                articles_found.append({
                    'title': article['title'],
                    'source': article['source']['name'],
                    'description': article['description']
                })
                sources_found.append(article['url'])
            return articles_found, sources_found
        except Exception as e:
            print(f"An error occurred with News API: {e}")
            return [], []


if __name__ == '__main__':
    # .env 파일에 NEWS_API_KEY가 설정되어 있어야 합니다.
    if not Config.NEWS_API_KEY:
        print("WARNING: NEWS_API_KEY is not set in .env file. News research will be skipped.")

    researcher = ContentResearcher()
    test_topic = "Artificial Intelligence"
    data = researcher.research_topic(test_topic)
    
    print(f"\n--- Research for: {test_topic} ---")
    print("\n[Key Facts (Wikipedia)]")
    for fact in data['key_facts']:
        print(f"- {fact}")

    print("\n[Recent Developments (News)]")
    for dev in data['recent_developments']:
        print(f"- {dev['title']} ({dev['source']})")

    print("\n[Sources]")
    for source in data['sources']:
        print(f"- {source}")
