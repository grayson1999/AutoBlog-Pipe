"""
콘텐츠 리서치 모듈
주제에 대한 정보를 다양한 소스에서 자동 수집
"""

import logging
import wikipedia
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

try:
    from newsapi import NewsApiClient
except ImportError:
    NewsApiClient = None

from ..config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentResearcher:
    """콘텐츠 리서치를 위한 정보 수집 클래스"""
    
    def __init__(self):
        """ContentResearcher 초기화"""
        # News API 초기화 (키가 있는 경우에만)
        self.news_client = None
        if NewsApiClient and Config.NEWS_API_KEY:
            try:
                self.news_client = NewsApiClient(api_key=Config.NEWS_API_KEY)
                logger.info("NewsAPI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize NewsAPI client: {e}")
        else:
            logger.info("NewsAPI not available (missing key or library)")
        
        # Wikipedia 언어 설정
        wikipedia.set_lang("en")  # 영어로 설정 (더 많은 정보)
        
        logger.info("ContentResearcher initialized successfully")
    
    def research_topic(self, topic: str) -> Dict[str, Any]:
        """
        주제에 대한 종합적인 리서치 수행
        
        Args:
            topic (str): 리서치할 주제
            
        Returns:
            Dict: 리서치 결과 데이터
        """
        logger.info(f"Starting research for topic: {topic}")
        
        research_data = {
            'topic': topic,
            'key_facts': [],
            'recent_developments': [],
            'statistics': [],
            'related_terms': [],
            'sources': [],
            'research_timestamp': datetime.now().isoformat()
        }
        
        try:
            # 1. Wikipedia에서 기본 정보 수집
            wiki_data = self._research_wikipedia(topic)
            research_data['key_facts'].extend(wiki_data.get('facts', []))
            research_data['related_terms'].extend(wiki_data.get('related_terms', []))
            research_data['sources'].extend(wiki_data.get('sources', []))
            
            # 2. News API에서 최신 동향 수집
            news_data = self._research_news(topic)
            research_data['recent_developments'].extend(news_data.get('articles', []))
            research_data['sources'].extend(news_data.get('sources', []))
            
            # 3. 추가 통계/데이터 (향후 확장 가능)
            # research_data['statistics'] = self._collect_statistics(topic)
            
            logger.info(f"Research completed for '{topic}': {len(research_data['key_facts'])} facts, {len(research_data['recent_developments'])} news")
            
        except Exception as e:
            logger.error(f"Error during research for '{topic}': {e}")
        
        return research_data
    
    def _research_wikipedia(self, topic: str) -> Dict[str, Any]:
        """Wikipedia에서 정보 수집"""
        wiki_data = {
            'facts': [],
            'related_terms': [],
            'sources': []
        }
        
        try:
            logger.info(f"Researching Wikipedia for: {topic}")
            
            # Wikipedia 검색
            search_results = wikipedia.search(topic, results=3)
            
            if not search_results:
                logger.warning(f"No Wikipedia results found for: {topic}")
                return wiki_data
            
            # 첫 번째 결과에서 정보 추출
            page_title = search_results[0]
            page = wikipedia.page(page_title)
            
            # 요약 정보 추출 (첫 3 문장)
            summary_sentences = page.summary.split('. ')[:3]
            for sentence in summary_sentences:
                if sentence.strip() and len(sentence) > 20:
                    wiki_data['facts'].append(sentence.strip() + '.')
            
            # 관련 링크에서 관련 용어 추출
            wiki_data['related_terms'] = page.links[:10]  # 상위 10개 링크
            
            # 소스 정보
            wiki_data['sources'].append({
                'type': 'wikipedia',
                'title': page.title,
                'url': page.url
            })
            
            logger.info(f"Wikipedia research successful: {len(wiki_data['facts'])} facts collected")
            
        except wikipedia.exceptions.DisambiguationError as e:
            # 모호한 검색어인 경우 첫 번째 옵션 사용
            logger.warning(f"Disambiguation for '{topic}', using first option")
            try:
                page = wikipedia.page(e.options[0])
                summary_sentences = page.summary.split('. ')[:2]
                for sentence in summary_sentences:
                    if sentence.strip() and len(sentence) > 20:
                        wiki_data['facts'].append(sentence.strip() + '.')
                
                wiki_data['sources'].append({
                    'type': 'wikipedia',
                    'title': page.title,
                    'url': page.url
                })
            except Exception as e2:
                logger.error(f"Error handling disambiguation: {e2}")
                
        except wikipedia.exceptions.PageError:
            logger.warning(f"Wikipedia page not found for: {topic}")
            
        except Exception as e:
            logger.error(f"Wikipedia research error for '{topic}': {e}")
        
        return wiki_data
    
    def _research_news(self, topic: str) -> Dict[str, Any]:
        """News API에서 최신 뉴스 수집"""
        news_data = {
            'articles': [],
            'sources': []
        }
        
        if not self.news_client:
            logger.info("News API not available, skipping news research")
            return news_data
        
        try:
            logger.info(f"Researching news for: {topic}")
            
            # 최근 30일간 뉴스 검색
            articles = self.news_client.get_everything(
                q=topic,
                language='en',
                sort_by='publishedAt',
                page_size=5,  # 최대 5개 기사
                from_param=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            )
            
            if articles['status'] == 'ok' and articles['articles']:
                for article in articles['articles']:
                    if article['title'] and article['description']:
                        news_item = {
                            'title': article['title'],
                            'description': article['description'][:200] + '...' if len(article['description']) > 200 else article['description'],
                            'source': article['source']['name'],
                            'url': article['url'],
                            'published_at': article['publishedAt']
                        }
                        news_data['articles'].append(news_item)
                        
                        # 소스 정보 추가
                        source_info = {
                            'type': 'news',
                            'title': article['title'],
                            'url': article['url'],
                            'source': article['source']['name']
                        }
                        news_data['sources'].append(source_info)
                
                logger.info(f"News research successful: {len(news_data['articles'])} articles collected")
            else:
                logger.warning(f"No news articles found for: {topic}")
                
        except Exception as e:
            logger.error(f"News research error for '{topic}': {e}")
        
        return news_data
    
    def _collect_statistics(self, topic: str) -> List[Dict[str, Any]]:
        """통계 데이터 수집 (향후 구현)"""
        # 향후 구현: 웹 스크래핑, API 등을 통한 통계 데이터 수집
        return []
    
    def get_research_summary(self, research_data: Dict[str, Any]) -> str:
        """리서치 데이터를 요약 텍스트로 변환"""
        summary_parts = []
        
        if research_data.get('key_facts'):
            summary_parts.append("Key Information:")
            for fact in research_data['key_facts'][:3]:  # 상위 3개만
                summary_parts.append(f"• {fact}")
        
        if research_data.get('recent_developments'):
            summary_parts.append("\nRecent News:")
            for article in research_data['recent_developments'][:2]:  # 상위 2개만
                summary_parts.append(f"• {article['title']} ({article['source']})")
        
        if research_data.get('sources'):
            source_names = [s.get('source', s.get('title', 'Unknown')) for s in research_data['sources'][:3]]
            summary_parts.append(f"\nSources: {', '.join(source_names)}")
        
        return "\n".join(summary_parts)


def test_content_researcher():
    """ContentResearcher 테스트 함수"""
    try:
        researcher = ContentResearcher()
        
        print("Testing ContentResearcher...")
        test_topic = "Artificial Intelligence"
        
        research_data = researcher.research_topic(test_topic)
        
        print(f"Research results for '{test_topic}':")
        print(f"  Key facts: {len(research_data['key_facts'])}")
        print(f"  Recent developments: {len(research_data['recent_developments'])}")
        print(f"  Sources: {len(research_data['sources'])}")
        
        # 요약 출력
        summary = researcher.get_research_summary(research_data)
        print("\n--- Research Summary ---")
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        return True
        
    except Exception as e:
        print(f"ContentResearcher test failed: {e}")
        return False


if __name__ == "__main__":
    # 직접 실행 시 테스트
    test_content_researcher()