"""
주제 로더 유틸리티
topics.yml 파일에서 블로그 주제 목록을 로드하고 관리
"""

import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TopicLoader:
    """블로그 주제 로더"""
    
    def __init__(self, topics_file: Optional[Path] = None):
        """
        TopicLoader 초기화
        
        Args:
            topics_file (Path, optional): topics.yml 파일 경로. None이면 기본값 사용
        """
        self.topics_file = topics_file or Config.TOPICS_FILE
        
        # 파일 존재 확인
        if not self.topics_file.exists():
            raise FileNotFoundError(f"Topics file not found: {self.topics_file}")
        
        logger.info(f"TopicLoader initialized with: {self.topics_file}")
    
    def load_topics(self) -> List[Dict[str, Any]]:
        """
        topics.yml에서 주제 목록 로드
        
        Returns:
            List[Dict]: 주제 정보 리스트
            
        Raises:
            Exception: 파일 로드 실패 시
        """
        try:
            with open(self.topics_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # topics 키에서 주제 리스트 추출
            topics = data.get('topics', [])
            
            if not topics:
                logger.warning("No topics found in topics.yml")
                return []
            
            # 주제 검증 및 기본값 설정
            validated_topics = []
            for i, topic in enumerate(topics):
                try:
                    validated_topic = self._validate_topic(topic, i)
                    validated_topics.append(validated_topic)
                except Exception as e:
                    logger.warning(f"Skipping invalid topic {i}: {e}")
                    continue
            
            logger.info(f"Loaded {len(validated_topics)} valid topics")
            return validated_topics
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {self.topics_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading topics from {self.topics_file}: {e}")
            raise
    
    def _validate_topic(self, topic: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        주제 정보 검증 및 기본값 설정
        
        Args:
            topic (Dict): 원본 주제 정보
            index (int): 주제 인덱스 (에러 표시용)
        
        Returns:
            Dict: 검증된 주제 정보
        """
        # 필수 필드 확인
        required_fields = ['title', 'post_type']
        for field in required_fields:
            if not topic.get(field):
                raise ValueError(f"Missing required field '{field}' in topic {index}")
        
        # 기본값 설정
        validated = {
            'title': topic['title'].strip(),
            'post_type': topic['post_type'].lower(),
            'category': topic.get('category', 'general'),
            'keywords': topic.get('keywords', []),
            'word_count': topic.get('word_count', 800)
        }
        
        # post_type 검증
        valid_post_types = ['listicle', 'guide', 'summary']
        if validated['post_type'] not in valid_post_types:
            logger.warning(f"Unknown post_type '{validated['post_type']}' in topic {index}, using 'guide'")
            validated['post_type'] = 'guide'
        
        # keywords가 문자열인 경우 리스트로 변환
        if isinstance(validated['keywords'], str):
            validated['keywords'] = [kw.strip() for kw in validated['keywords'].split(',')]
        
        # word_count 검증
        try:
            validated['word_count'] = int(validated['word_count'])
            if validated['word_count'] < 300:
                validated['word_count'] = 300
            elif validated['word_count'] > 2000:
                validated['word_count'] = 2000
        except (ValueError, TypeError):
            validated['word_count'] = 800
        
        return validated
    
    def get_topics_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        특정 카테고리의 주제들만 반환
        
        Args:
            category (str): 찾을 카테고리
        
        Returns:
            List[Dict]: 해당 카테고리의 주제 리스트
        """
        all_topics = self.load_topics()
        return [topic for topic in all_topics if topic['category'] == category]
    
    def get_topics_by_type(self, post_type: str) -> List[Dict[str, Any]]:
        """
        특정 글 유형의 주제들만 반환
        
        Args:
            post_type (str): 찾을 글 유형
        
        Returns:
            List[Dict]: 해당 유형의 주제 리스트
        """
        all_topics = self.load_topics()
        return [topic for topic in all_topics if topic['post_type'] == post_type]
    
    def get_topic_stats(self) -> Dict[str, Any]:
        """
        주제 통계 정보 반환
        
        Returns:
            Dict: 주제 통계
        """
        topics = self.load_topics()
        
        if not topics:
            return {'total': 0, 'categories': {}, 'types': {}}
        
        # 카테고리별 통계
        categories = {}
        for topic in topics:
            cat = topic['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        # 유형별 통계
        types = {}
        for topic in topics:
            ptype = topic['post_type']
            types[ptype] = types.get(ptype, 0) + 1
        
        return {
            'total': len(topics),
            'categories': categories,
            'types': types
        }


def test_topic_loader():
    """TopicLoader 테스트 함수"""
    try:
        loader = TopicLoader()
        
        # 모든 주제 로드
        topics = loader.load_topics()
        print(f"Loaded {len(topics)} topics")
        
        # 처음 3개 주제 출력
        for i, topic in enumerate(topics[:3]):
            print(f"  {i+1}. {topic['title']} ({topic['post_type']}, {topic['category']})")
        
        # 통계 출력
        stats = loader.get_topic_stats()
        print(f"\nStatistics:")
        print(f"  Total topics: {stats['total']}")
        print(f"  Categories: {stats['categories']}")
        print(f"  Types: {stats['types']}")
        
        print("TopicLoader test successful!")
        return True
        
    except Exception as e:
        print(f"TopicLoader test failed: {e}")
        return False


if __name__ == "__main__":
    # 직접 실행 시 테스트
    test_topic_loader()