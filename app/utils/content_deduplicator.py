"""
콘텐츠 중복 체크 모듈
기존 발행 글과의 중복을 방지하는 시스템
"""

import logging
import difflib
from pathlib import Path
from typing import List, Dict, Any
import yaml
import re
from datetime import datetime, timedelta

from ..config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentDeduplicator:
    """콘텐츠 중복 방지 클래스"""
    
    def __init__(self, posts_dir: Path = None):
        """
        ContentDeduplicator 초기화
        
        Args:
            posts_dir (Path, optional): _posts 디렉터리 경로
        """
        self.posts_dir = posts_dir or Config.POSTS_DIR
        self.similarity_threshold = 0.7  # 70% 이상 유사하면 중복으로 판단
        
        logger.info(f"ContentDeduplicator initialized - posts_dir: {self.posts_dir}")
    
    def check_duplicates(self, new_title: str) -> bool:
        """
        새로운 주제가 기존 글과 중복되는지 체크
        
        Args:
            new_title (str): 확인할 새 제목
        
        Returns:
            bool: True면 중복 (발행 금지), False면 유니크 (발행 가능)
        """
        try:
            logger.info(f"Checking duplicates for: '{new_title}'")
            
            # 기존 발행 글 목록 로드
            published_posts = self._load_published_posts()
            
            if not published_posts:
                logger.info("No existing posts found - proceeding with publication")
                return False
            
            # 제목 유사도 체크
            for post in published_posts:
                existing_title = post.get('title', '')
                similarity = self._calculate_similarity(new_title, existing_title)
                
                if similarity >= self.similarity_threshold:
                    logger.warning(f"Duplicate detected! '{new_title}' is {similarity:.2%} similar to '{existing_title}'")
                    return True
            
            # 키워드 기반 중복 체크
            if self._check_keyword_overlap(new_title, published_posts):
                logger.warning(f"High keyword overlap detected for: '{new_title}'")
                return True
            
            logger.info(f"No duplicates found for: '{new_title}'")
            return False
            
        except Exception as e:
            logger.error(f"Error checking duplicates for '{new_title}': {e}")
            # 에러 발생 시에는 안전하게 중복으로 처리하지 않음 (발행 허용)
            return False
    
    def _load_published_posts(self) -> List[Dict[str, Any]]:
        """기존 발행 글 목록을 로드"""
        posts = []
        
        try:
            if not self.posts_dir.exists():
                logger.info("Posts directory doesn't exist yet")
                return posts
            
            # Jekyll _posts 디렉터리에서 모든 .md 파일 읽기
            for post_file in self.posts_dir.glob("*.md"):
                try:
                    with open(post_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Front matter 파싱
                    front_matter = self._extract_front_matter(content)
                    if front_matter:
                        front_matter['filename'] = post_file.name
                        posts.append(front_matter)
                        
                except Exception as e:
                    logger.warning(f"Error reading post file {post_file}: {e}")
                    continue
            
            logger.info(f"Loaded {len(posts)} existing posts")
            
        except Exception as e:
            logger.error(f"Error loading published posts: {e}")
        
        return posts
    
    def _extract_front_matter(self, content: str) -> Dict[str, Any]:
        """마크다운 파일에서 Front Matter 추출"""
        try:
            # Front matter 구분자 찾기
            if not content.startswith('---\n'):
                return {}
            
            # 두 번째 --- 찾기
            end_marker = content.find('\n---\n', 4)
            if end_marker == -1:
                return {}
            
            # YAML 파싱
            yaml_content = content[4:end_marker]
            front_matter = yaml.safe_load(yaml_content)
            
            return front_matter or {}
            
        except Exception as e:
            logger.warning(f"Error extracting front matter: {e}")
            return {}
    
    def _calculate_similarity(self, title1: str, title2: str) -> float:
        """두 제목 간 유사도 계산"""
        try:
            # 정규화: 소문자 변환, 특수문자 제거
            def normalize(text):
                text = text.lower()
                text = re.sub(r'[^\w\s]', '', text)
                text = re.sub(r'\s+', ' ', text).strip()
                return text
            
            norm_title1 = normalize(title1)
            norm_title2 = normalize(title2)
            
            # 완전 동일한 경우
            if norm_title1 == norm_title2:
                return 1.0
            
            # SequenceMatcher를 사용한 유사도 계산
            similarity = difflib.SequenceMatcher(None, norm_title1, norm_title2).ratio()
            
            return similarity
            
        except Exception as e:
            logger.warning(f"Error calculating similarity: {e}")
            return 0.0
    
    def _check_keyword_overlap(self, new_title: str, published_posts: List[Dict]) -> bool:
        """키워드 중복 체크"""
        try:
            # 새 제목에서 키워드 추출
            new_keywords = self._extract_keywords(new_title)
            
            for post in published_posts:
                existing_title = post.get('title', '')
                existing_keywords = self._extract_keywords(existing_title)
                
                # 키워드 교집합 비율 계산
                if new_keywords and existing_keywords:
                    overlap = len(new_keywords & existing_keywords)
                    total_unique = len(new_keywords | existing_keywords)
                    
                    if total_unique > 0:
                        overlap_ratio = overlap / total_unique
                        if overlap_ratio >= 0.6:  # 60% 이상 키워드 겹침
                            return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking keyword overlap: {e}")
            return False
    
    def _extract_keywords(self, title: str) -> set:
        """제목에서 중요 키워드 추출"""
        try:
            # 불용어 리스트
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
                'those', 'how', 'what', 'when', 'where', 'why', 'who', '2024', '2025'
            }
            
            # 정규화 및 토큰화
            title_lower = title.lower()
            words = re.findall(r'\b[a-zA-Z]{3,}\b', title_lower)  # 3글자 이상 영단어만
            
            # 불용어 제거
            keywords = set(word for word in words if word not in stop_words)
            
            return keywords
            
        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return set()
    
    def get_duplicate_stats(self) -> Dict[str, Any]:
        """중복 체크 통계 정보 반환"""
        try:
            published_posts = self._load_published_posts()
            
            stats = {
                'total_posts': len(published_posts),
                'posts_by_date': {},
                'recent_posts': []
            }
            
            # 날짜별 통계
            for post in published_posts:
                date_str = post.get('date', '')[:10]  # YYYY-MM-DD 형식
                if date_str:
                    stats['posts_by_date'][date_str] = stats['posts_by_date'].get(date_str, 0) + 1
            
            # 최근 7일 포스트
            cutoff_date = datetime.now() - timedelta(days=7)
            for post in published_posts:
                try:
                    post_date_str = post.get('date', '')[:10]
                    post_date = datetime.strptime(post_date_str, '%Y-%m-%d')
                    if post_date >= cutoff_date:
                        stats['recent_posts'].append({
                            'title': post.get('title', 'Untitled'),
                            'date': post_date_str
                        })
                except:
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting duplicate stats: {e}")
            return {'error': str(e)}


def test_content_deduplicator():
    """ContentDeduplicator 테스트 함수"""
    try:
        deduplicator = ContentDeduplicator()
        
        print("Testing ContentDeduplicator...")
        
        # 테스트 제목들
        test_titles = [
            "The Future of Artificial Intelligence",
            "Future AI Technologies and Trends",  # 유사한 제목
            "Complete Guide to Machine Learning",  # 다른 주제
            "Best Practices for Remote Work"       # 완전히 다른 주제
        ]
        
        for title in test_titles:
            is_duplicate = deduplicator.check_duplicates(title)
            print(f"  '{title}' -> {'DUPLICATE' if is_duplicate else 'UNIQUE'}")
        
        # 통계 출력
        stats = deduplicator.get_duplicate_stats()
        print(f"\nDuplication Stats:")
        print(f"  Total posts: {stats.get('total_posts', 0)}")
        print(f"  Recent posts (7 days): {len(stats.get('recent_posts', []))}")
        
        return True
        
    except Exception as e:
        print(f"ContentDeduplicator test failed: {e}")
        return False


if __name__ == "__main__":
    # 직접 실행 시 테스트
    test_content_deduplicator()