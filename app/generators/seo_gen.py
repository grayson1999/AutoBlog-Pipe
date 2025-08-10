"""
SEO 메타데이터 생성 모듈
제목, 슬러그, 메타 설명, 키워드 등 SEO 최적화 요소 자동 생성
"""

import re
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from unidecode import unidecode

from .content_gen import ContentGenerator
from ..config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SEOGenerator:
    """SEO 메타데이터 생성기"""
    
    def __init__(self, content_generator: Optional[ContentGenerator] = None):
        """
        SEOGenerator 초기화
        
        Args:
            content_generator (ContentGenerator, optional): 콘텐츠 생성기 인스턴스
        """
        self.content_generator = content_generator or ContentGenerator()
        
        # SEO 설정
        self.max_title_length = 60
        self.max_description_length = 160
        self.max_slug_length = 50
        self.max_keywords = 8
        
        logger.info("SEOGenerator initialized successfully")
    
    def generate_slug(self, title: str) -> str:
        """
        제목을 SEO 친화적인 URL 슬러그로 변환
        
        Args:
            title (str): 원본 제목
            
        Returns:
            str: SEO 친화적 슬러그
        """
        try:
            # 1. 한글을 영문으로 음역 (unidecode 사용)
            slug = unidecode(title)
            
            # 2. 소문자 변환
            slug = slug.lower()
            
            # 3. 특수문자 제거 및 공백을 하이픈으로 변경
            slug = re.sub(r'[^\w\s-]', '', slug)  # 알파벳, 숫자, 공백, 하이픈만 유지
            slug = re.sub(r'[\s_]+', '-', slug)   # 공백과 언더스코어를 하이픈으로
            slug = re.sub(r'-+', '-', slug)       # 연속된 하이픈을 하나로
            
            # 4. 앞뒤 하이픈 제거
            slug = slug.strip('-')
            
            # 5. 길이 제한
            if len(slug) > self.max_slug_length:
                # 단어 경계에서 자르기
                slug = slug[:self.max_slug_length]
                last_dash = slug.rfind('-')
                if last_dash > 20:  # 너무 짧아지지 않도록
                    slug = slug[:last_dash]
            
            # 6. 빈 문자열 방지
            if not slug:
                slug = "blog-post"
            
            logger.info(f"Generated slug: '{title}' -> '{slug}'")
            return slug
            
        except Exception as e:
            logger.error(f"Error generating slug for '{title}': {e}")
            # 기본 슬러그 반환
            return f"blog-post-{datetime.now().strftime('%Y%m%d')}"
    
    def extract_keywords_from_content(self, content: str, existing_keywords: List[str] = None) -> List[str]:
        """
        콘텐츠에서 중요한 키워드 추출
        
        Args:
            content (str): 콘텐츠 텍스트
            existing_keywords (List[str], optional): 기존 키워드 리스트
            
        Returns:
            List[str]: 추출된 키워드 목록
        """
        existing_keywords = existing_keywords or []
        keywords = []
        
        try:
            # 기존 키워드 먼저 추가
            keywords.extend(existing_keywords)
            
            # 제목과 헤딩에서 키워드 추출
            headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
            for heading in headings:
                # 간단한 키워드 추출 (향후 NLP 라이브러리로 개선 가능)
                words = re.findall(r'\b[가-힣]{2,}\b', heading)
                keywords.extend(words[:2])  # 각 제목에서 최대 2개
            
            # 중복 제거 및 길이 제한
            unique_keywords = []
            for keyword in keywords:
                if keyword not in unique_keywords and len(keyword) >= 2:
                    unique_keywords.append(keyword)
            
            # 최대 키워드 수 제한
            result = unique_keywords[:self.max_keywords]
            
            logger.info(f"Extracted keywords: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return existing_keywords[:self.max_keywords] if existing_keywords else ["블로그", "정보"]
    
    def generate_meta_description(self, title: str, content: str, keywords: List[str] = None) -> str:
        """
        AI를 활용하여 메타 설명 생성
        
        Args:
            title (str): 글 제목
            content (str): 글 내용
            keywords (List[str], optional): 키워드 리스트
            
        Returns:
            str: 생성된 메타 설명
        """
        try:
            # AI를 이용한 메타 설명 생성 요청
            seo_topic = {
                'title': title,
                'content': content[:1000],  # 처음 1000자만 사용
                'keywords': keywords or [],
                'category': 'general'
            }
            
            # SEO 메타 프롬프트 사용
            template = self.content_generator.load_prompt_template('seo_meta')
            formatted_prompt = self.content_generator.format_prompt(template, seo_topic)
            
            # AI 응답에서 메타 설명 부분만 추출
            ai_response = self.content_generator.call_openai_api(
                formatted_prompt, 
                max_tokens=300,  # 짧은 응답
                temperature=0.5  # 더 일관된 결과
            )
            
            # 메타 설명 부분 파싱 (간단한 방식)
            meta_description = self._parse_meta_description(ai_response)
            
            # 길이 조정
            if len(meta_description) > self.max_description_length:
                meta_description = meta_description[:self.max_description_length-3] + "..."
            
            logger.info(f"Generated meta description ({len(meta_description)} chars)")
            return meta_description
            
        except Exception as e:
            logger.error(f"Error generating meta description: {e}")
            # 기본 메타 설명 생성
            return self._generate_fallback_description(title, keywords)
    
    def _parse_meta_description(self, ai_response: str) -> str:
        """AI 응답에서 메타 설명 파싱"""
        try:
            # "메타 설명" 섹션 찾기
            lines = ai_response.split('\n')
            in_meta_section = False
            description_lines = []
            
            for line in lines:
                line = line.strip()
                if '메타 설명' in line or 'Meta Description' in line:
                    in_meta_section = True
                    continue
                elif in_meta_section:
                    if line.startswith('#') or line.startswith('##'):
                        break  # 다음 섹션 시작
                    if line and not line.startswith('-') and not line.startswith('*'):
                        description_lines.append(line)
                        if len(' '.join(description_lines)) > 100:  # 충분한 길이
                            break
            
            if description_lines:
                result = ' '.join(description_lines)
                # 따옴표 제거
                result = re.sub(r'^["\']|["\']$', '', result)
                return result.strip()
            
            # 첫 번째 줄에서 설명 찾기 (fallback)
            for line in lines:
                line = line.strip()
                if len(line) > 50 and not line.startswith('#'):
                    result = re.sub(r'^["\']|["\']$', '', line)
                    return result.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Error parsing meta description: {e}")
            return ""
    
    def _generate_fallback_description(self, title: str, keywords: List[str] = None) -> str:
        """기본 메타 설명 생성"""
        keywords = keywords or []
        keyword_text = ", ".join(keywords[:3]) if keywords else "유용한 정보"
        
        templates = [
            f"{title}에 대한 상세한 가이드입니다. {keyword_text}를 포함한 실용적인 정보를 제공합니다.",
            f"{keyword_text}에 관한 최신 정보와 팁을 정리했습니다. {title}을 통해 더 자세히 알아보세요.",
            f"실용적이고 유용한 {title} 정보를 제공합니다. {keyword_text} 관련 내용을 확인해보세요."
        ]
        
        import random
        description = random.choice(templates)
        
        if len(description) > self.max_description_length:
            description = description[:self.max_description_length-3] + "..."
        
        return description
    
    def categorize_post(self, title: str, content: str, keywords: List[str] = None) -> str:
        """
        글의 내용을 바탕으로 카테고리 분류
        
        Args:
            title (str): 글 제목
            content (str): 글 내용
            keywords (List[str], optional): 키워드 리스트
            
        Returns:
            str: 분류된 카테고리
        """
        # 키워드 기반 카테고리 매핑
        category_keywords = {
            'productivity': ['생산성', '효율', '업무', '일', '도구', '앱', '시간관리'],
            'technology': ['기술', '개발', '프로그래밍', 'AI', '인공지능', '소프트웨어'],
            'lifestyle': ['라이프스타일', '생활', '건강', '취미', '여행', '음식'],
            'business': ['비즈니스', '사업', '창업', '마케팅', '경영', '투자'],
            'education': ['교육', '학습', '공부', '강의', '책', '지식'],
            'finance': ['금융', '돈', '투자', '재테크', '경제', '주식']
        }
        
        # 제목과 키워드에서 카테고리 판단
        text_to_check = f"{title} {' '.join(keywords or [])}".lower()
        
        category_scores = {}
        for category, category_keys in category_keywords.items():
            score = 0
            for key in category_keys:
                if key in text_to_check:
                    score += 1
            category_scores[category] = score
        
        # 가장 높은 점수의 카테고리 선택
        if category_scores and max(category_scores.values()) > 0:
            best_category = max(category_scores, key=category_scores.get)
            logger.info(f"Categorized as: {best_category}")
            return best_category
        
        # 기본 카테고리
        return 'general'
    
    def generate_front_matter(self, topic: Dict[str, Any], content: str, 
                            generated_content: str = None) -> Dict[str, Any]:
        """
        Jekyll용 Front Matter YAML 생성
        
        Args:
            topic (Dict): 원본 주제 정보
            content (str): 생성된 콘텐츠
            generated_content (str, optional): 추가 생성 콘텐츠
            
        Returns:
            Dict: Front matter 데이터
        """
        try:
            title = topic.get('title', '제목 없음')
            existing_keywords = topic.get('keywords', [])
            
            # SEO 메타데이터 생성
            slug = self.generate_slug(title)
            keywords = self.extract_keywords_from_content(content, existing_keywords)
            meta_description = self.generate_meta_description(title, content, keywords)
            category = self.categorize_post(title, content, keywords)
            
            # Front matter 구성
            front_matter = {
                'layout': 'post',
                'title': title,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S +0900'),
                'categories': [category],
                'tags': keywords,
                'excerpt': meta_description,
                'slug': slug,
                'author': 'AutoBot',
                'seo': {
                    'title': title if len(title) <= self.max_title_length else title[:self.max_title_length-3] + "...",
                    'description': meta_description,
                    'keywords': ', '.join(keywords)
                }
            }
            
            logger.info(f"Generated front matter for: {title}")
            return front_matter
            
        except Exception as e:
            logger.error(f"Error generating front matter: {e}")
            # 기본 front matter
            return {
                'layout': 'post',
                'title': topic.get('title', '제목 없음'),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S +0900'),
                'categories': ['general'],
                'tags': topic.get('keywords', ['블로그']),
                'author': 'AutoBot'
            }
    
    def create_full_post(self, topic: Dict[str, Any]) -> str:
        """
        주제를 바탕으로 Front Matter + 콘텐츠가 포함된 완전한 포스트 생성
        
        Args:
            topic (Dict): 주제 정보
            
        Returns:
            str: Front Matter + 콘텐츠가 포함된 완전한 마크다운
        """
        try:
            # 1. 콘텐츠 생성
            logger.info(f"Creating full post for: {topic.get('title')}")
            content = self.content_generator.generate_post(topic)
            
            # 2. Front Matter 생성
            front_matter_data = self.generate_front_matter(topic, content)
            
            # 3. YAML Front Matter 문자열 생성
            front_matter_yaml = yaml.dump(front_matter_data, 
                                        default_flow_style=False, 
                                        allow_unicode=True,
                                        sort_keys=False)
            
            # 4. 완전한 포스트 조합
            full_post = f"---\n{front_matter_yaml}---\n\n{content}"
            
            logger.info(f"Created full post ({len(full_post)} chars)")
            return full_post
            
        except Exception as e:
            logger.error(f"Error creating full post: {e}")
            raise


def test_seo_generator():
    """SEOGenerator 테스트 함수"""
    try:
        # 테스트 주제
        test_topic = {
            "title": "2024년 최고의 생산성 앱 10선",
            "category": "productivity",
            "keywords": ["생산성 앱", "업무 효율", "모바일 앱"],
            "post_type": "listicle",
            "word_count": 800
        }
        
        seo_gen = SEOGenerator()
        
        # 슬러그 생성 테스트
        slug = seo_gen.generate_slug(test_topic['title'])
        print(f"Generated slug: {slug}")
        
        # 완전한 포스트 생성 테스트
        full_post = seo_gen.create_full_post(test_topic)
        
        print("✅ SEO generation test successful!")
        print(f"Full post length: {len(full_post)} characters")
        print("\n--- Full Post Preview ---")
        print(full_post[:800] + "..." if len(full_post) > 800 else full_post)
        
        return True
        
    except Exception as e:
        print(f"❌ SEO generation test failed: {e}")
        return False


if __name__ == "__main__":
    # 직접 실행 시 테스트
    test_seo_generator()