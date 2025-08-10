"""
외부 소스에서 트렌딩 주제를 수집하는 모듈
RSS feeds, trends 등에서 블로그 아이디어 수집
"""

import logging
import feedparser
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IdeaCollector:
    """외부 소스에서 블로그 아이디어를 수집하는 클래스"""
    
    def __init__(self):
        """IdeaCollector 초기화"""
        # RSS 피드 소스들 (기술/뉴스 관련)
        self.rss_sources = [
            'https://feeds.feedburner.com/oreilly/radar',
            'https://www.wired.com/feed/rss',
            'https://techcrunch.com/feed/',
            'https://www.theverge.com/rss/index.xml',
            'https://feeds.arstechnica.com/arstechnica/index',
            'https://www.engadget.com/rss.xml'
        ]
        
        # 기본 아이디어 풀 (RSS 실패 시 사용)
        self.fallback_ideas = [
            {'title': 'The Future of Remote Work Technologies', 'source': 'fallback', 'score': 70},
            {'title': 'Artificial Intelligence in Healthcare 2025', 'source': 'fallback', 'score': 85},
            {'title': 'Sustainable Technology Trends', 'source': 'fallback', 'score': 75},
            {'title': 'Cybersecurity Best Practices for Small Businesses', 'source': 'fallback', 'score': 80},
            {'title': '5G Technology Impact on IoT Devices', 'source': 'fallback', 'score': 78},
            {'title': 'Cloud Computing Cost Optimization Strategies', 'source': 'fallback', 'score': 72},
            {'title': 'Machine Learning Applications in Marketing', 'source': 'fallback', 'score': 82},
            {'title': 'Digital Transformation in Traditional Industries', 'source': 'fallback', 'score': 76},
            {'title': 'Blockchain Beyond Cryptocurrency', 'source': 'fallback', 'score': 74},
            {'title': 'Virtual Reality in Education and Training', 'source': 'fallback', 'score': 71}
        ]
        
        logger.info("IdeaCollector initialized successfully")
    
    def collect_trending_topics(self) -> List[Dict[str, Any]]:
        """
        여러 소스에서 트렌딩 주제를 수집
        
        Returns:
            List[Dict]: 수집된 아이디어 목록
        """
        logger.info("Starting to collect trending topics...")
        
        all_ideas = []
        
        # 1. RSS 피드에서 아이디어 수집
        rss_ideas = self._collect_from_rss()
        all_ideas.extend(rss_ideas)
        
        # 2. 기본 아이디어 추가 (다양성 확보)
        fallback_sample = random.sample(self.fallback_ideas, min(3, len(self.fallback_ideas)))
        all_ideas.extend(fallback_sample)
        
        # 3. 중복 제거 및 정렬
        unique_ideas = self._deduplicate_ideas(all_ideas)
        scored_ideas = self._score_ideas(unique_ideas)
        
        # 상위 10개 선택
        top_ideas = sorted(scored_ideas, key=lambda x: x.get('score', 0), reverse=True)[:10]
        
        logger.info(f"Collected {len(top_ideas)} trending topics")
        return top_ideas
    
    def _collect_from_rss(self) -> List[Dict[str, Any]]:
        """RSS 피드에서 아이디어 수집"""
        ideas = []
        
        for rss_url in self.rss_sources:
            try:
                logger.info(f"Fetching RSS feed: {rss_url}")
                feed = feedparser.parse(rss_url)
                
                if feed.bozo:
                    logger.warning(f"RSS feed parsing warning for {rss_url}: {feed.bozo_exception}")
                
                # 최근 7일 이내 항목만 수집
                cutoff_date = datetime.now() - timedelta(days=7)
                
                for entry in feed.entries[:10]:  # 최대 10개씩
                    try:
                        # 발행일 확인
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                            if pub_date < cutoff_date:
                                continue
                        
                        idea = {
                            'title': entry.get('title', 'Untitled'),
                            'source': rss_url,
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'summary': entry.get('summary', '')[:200] + '...' if entry.get('summary') else ''
                        }
                        
                        ideas.append(idea)
                        
                    except Exception as e:
                        logger.warning(f"Error processing RSS entry: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error fetching RSS feed {rss_url}: {e}")
                continue
        
        logger.info(f"Collected {len(ideas)} ideas from RSS feeds")
        return ideas
    
    def _deduplicate_ideas(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """아이디어 중복 제거"""
        unique_ideas = []
        seen_titles = set()
        
        for idea in ideas:
            title_lower = idea.get('title', '').lower()
            
            # 간단한 중복 체크 (단어 기반)
            title_words = set(title_lower.split())
            is_duplicate = False
            
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                # 70% 이상 단어가 겹치면 중복으로 판단
                if len(title_words & seen_words) / len(title_words | seen_words) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_ideas.append(idea)
                seen_titles.add(title_lower)
        
        logger.info(f"Deduplicated to {len(unique_ideas)} unique ideas")
        return unique_ideas
    
    def _score_ideas(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """아이디어 점수화"""
        # 키워드 기반 점수 계산
        tech_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'blockchain', 'cloud',
            'cybersecurity', 'iot', '5g', 'quantum', 'automation', 'robot', 'data',
            'digital', 'technology', 'software', 'app', 'platform', 'development',
            'innovation', 'startup', 'coding', 'programming', 'tech', 'virtual',
            'augmented', 'mobile', 'web', 'api', 'database', 'security', 'crypto'
        ]
        
        for idea in ideas:
            score = 50  # 기본 점수
            title_lower = idea.get('title', '').lower()
            summary_lower = idea.get('summary', '').lower()
            
            # 기술 키워드 포함 시 점수 증가
            for keyword in tech_keywords:
                if keyword in title_lower or keyword in summary_lower:
                    score += 10
            
            # 최근성 보너스
            if 'published' in idea and idea['published']:
                try:
                    # 최근 3일 이내면 보너스 점수
                    pub_date = datetime.strptime(idea['published'][:10], '%Y-%m-%d')
                    if (datetime.now() - pub_date).days <= 3:
                        score += 15
                except:
                    pass
            
            # 제목 길이 보정 (너무 길거나 짧으면 감점)
            title_len = len(idea.get('title', ''))
            if 20 <= title_len <= 80:
                score += 5
            elif title_len > 100:
                score -= 10
            
            idea['score'] = min(100, score)  # 최대 100점
        
        return ideas
    
    def get_fallback_ideas(self) -> List[Dict[str, Any]]:
        """기본 아이디어 목록 반환 (테스트용)"""
        return random.sample(self.fallback_ideas, min(5, len(self.fallback_ideas)))


def test_idea_collector():
    """IdeaCollector 테스트 함수"""
    try:
        collector = IdeaCollector()
        
        print("Testing IdeaCollector...")
        ideas = collector.collect_trending_topics()
        
        print(f"Collected {len(ideas)} trending topics:")
        for i, idea in enumerate(ideas[:5], 1):
            print(f"  {i}. {idea['title']} (Score: {idea.get('score', 'N/A')})")
            print(f"     Source: {idea.get('source', 'Unknown')}")
            
        return True
        
    except Exception as e:
        print(f"IdeaCollector test failed: {e}")
        return False


if __name__ == "__main__":
    # 직접 실행 시 테스트
    test_idea_collector()