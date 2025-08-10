"""
AI 콘텐츠 생성 모듈
OpenAI API를 활용한 블로그 글 자동 생성
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Any
try:
    from openai import OpenAI
    import openai
except ImportError:
    raise ImportError("OpenAI library not found. Install with: pip install openai")

from ..config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentGenerator:
    """AI 기반 콘텐츠 생성기"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        ContentGenerator 초기화
        
        Args:
            api_key (str, optional): OpenAI API 키. None이면 환경변수에서 로드
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # OpenAI 클라이언트 초기화 (httpx 0.27.2 호환)
        self.client = OpenAI(api_key=self.api_key)
        
        # 프롬프트 디렉터리 경로
        self.prompts_dir = Config.PROMPTS_DIR
        
        # 생성 설정
        self.default_model = "gpt-3.5-turbo"
        self.default_max_tokens = 2000
        self.default_temperature = 0.7
        self.max_retries = 3
        self.retry_delay = 1  # 초
        
        logger.info("ContentGenerator initialized successfully")
    
    def load_prompt_template(self, post_type: str) -> str:
        """
        프롬프트 템플릿 파일 로드
        
        Args:
            post_type (str): 글 유형 ('listicle', 'guide', 'summary', 'seo_meta')
            
        Returns:
            str: 프롬프트 템플릿 내용
            
        Raises:
            FileNotFoundError: 프롬프트 파일을 찾을 수 없는 경우
        """
        template_file = self.prompts_dir / f"post_{post_type}.txt"
        
        if not template_file.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_file}")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template = f.read().strip()
            
            logger.info(f"Loaded prompt template: {post_type}")
            return template
            
        except Exception as e:
            logger.error(f"Error loading prompt template {post_type}: {e}")
            raise
    
    def format_prompt(self, template: str, topic: Dict[str, Any]) -> str:
        """
        프롬프트 템플릿에 주제 정보를 채워넣어 실제 프롬프트 생성
        
        Args:
            template (str): 프롬프트 템플릿
            topic (Dict): 주제 정보 딕셔너리
            
        Returns:
            str: 포매팅된 프롬프트
        """
        # 기본값 설정
        topic_data = {
            'title': topic.get('title', '제목 없음'),
            'category': topic.get('category', '일반'),
            'keywords': ', '.join(topic.get('keywords', [])),
            'word_count': topic.get('word_count', 800),
            'content': topic.get('content', '')  # SEO 메타 생성용
        }
        
        try:
            # 템플릿 변수 치환
            formatted_prompt = template.format(**topic_data)
            logger.info(f"Formatted prompt for topic: {topic_data['title']}")
            return formatted_prompt
            
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise ValueError(f"Template formatting failed: missing variable {e}")
    
    def call_openai_api(self, prompt: str, max_tokens: Optional[int] = None, 
                       temperature: Optional[float] = None) -> str:
        """
        OpenAI API 호출하여 텍스트 생성
        
        Args:
            prompt (str): 입력 프롬프트
            max_tokens (int, optional): 최대 토큰 수
            temperature (float, optional): 창의성 수준 (0.0-2.0)
            
        Returns:
            str: 생성된 텍스트
            
        Raises:
            Exception: API 호출 실패 시
        """
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Calling OpenAI API (attempt {attempt + 1}/{self.max_retries})")
                
                # OpenAI v1.0+ 방식
                response = self.client.chat.completions.create(
                    model=self.default_model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "당신은 전문적인 블로그 작가입니다. 고품질의 유익하고 실용적인 콘텐츠를 작성합니다."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9,
                    frequency_penalty=0.3,
                    presence_penalty=0.3
                )
                
                generated_text = response.choices[0].message.content.strip()
                
                if not generated_text:
                    raise ValueError("Empty response from OpenAI API")
                
                logger.info(f"Successfully generated content ({len(generated_text)} characters)")
                return generated_text
                
            except Exception as e:
                error_msg = str(e).lower()
                if "rate_limit" in error_msg or "rate limit" in error_msg:
                    logger.warning(f"Rate limit exceeded, waiting {self.retry_delay * (attempt + 1)} seconds...")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                elif "api" in error_msg:
                    logger.error(f"OpenAI API error: {e}")
                    if attempt == self.max_retries - 1:
                        raise
                    time.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f"Unexpected error calling OpenAI API: {e}")
                    if attempt == self.max_retries - 1:
                        raise
                    time.sleep(self.retry_delay)
                    continue
        
        raise Exception(f"Failed to generate content after {self.max_retries} attempts")
    
    def validate_content(self, content: str, min_length: int = 500) -> bool:
        """
        생성된 콘텐츠 품질 검증
        
        Args:
            content (str): 검증할 콘텐츠
            min_length (int): 최소 길이 (문자 수)
            
        Returns:
            bool: 검증 통과 여부
        """
        if not content or len(content.strip()) < min_length:
            logger.warning(f"Content too short: {len(content)} characters (minimum: {min_length})")
            return False
        
        # 기본 마크다운 구조 확인
        if not content.strip().startswith('#'):
            logger.warning("Content doesn't start with proper heading")
            return False
        
        # 최소 섹션 수 확인
        section_count = content.count('\n##')
        if section_count < 2:
            logger.warning(f"Content has too few sections: {section_count}")
            return False
        
        logger.info("Content validation passed")
        return True
    
    def generate_post(self, topic: Dict[str, Any]) -> str:
        """
        주제 정보를 바탕으로 블로그 글 생성
        
        Args:
            topic (Dict): 주제 정보
                - title (str): 글 제목
                - category (str): 카테고리
                - keywords (List[str]): 키워드 리스트
                - post_type (str): 글 유형 ('listicle', 'guide', 'summary')
                - word_count (int, optional): 목표 단어 수
        
        Returns:
            str: 생성된 마크다운 콘텐츠
            
        Raises:
            ValueError: 필수 필드 누락 시
            Exception: 생성 실패 시
        """
        # 필수 필드 확인
        required_fields = ['title', 'post_type']
        for field in required_fields:
            if field not in topic:
                raise ValueError(f"Missing required field: {field}")
        
        post_type = topic['post_type']
        logger.info(f"Generating {post_type} post: {topic['title']}")
        
        try:
            # 1. 프롬프트 템플릿 로드
            template = self.load_prompt_template(post_type)
            
            # 2. 프롬프트 포매팅
            formatted_prompt = self.format_prompt(template, topic)
            
            # 3. AI 콘텐츠 생성
            generated_content = self.call_openai_api(formatted_prompt)
            
            # 4. 품질 검증
            if not self.validate_content(generated_content):
                logger.warning("Generated content failed validation, but proceeding...")
            
            logger.info(f"Successfully generated post: {topic['title']}")
            return generated_content
            
        except Exception as e:
            logger.error(f"Failed to generate post for topic '{topic['title']}': {e}")
            raise
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        사용량 통계 반환 (향후 구현)
        
        Returns:
            Dict: 사용량 정보
        """
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0
        }


def test_content_generator():
    """ContentGenerator 테스트 함수"""
    try:
        # 테스트 주제
        test_topic = {
            "title": "2024년 최고의 생산성 앱 10선",
            "category": "productivity", 
            "keywords": ["생산성 앱", "업무 효율", "모바일 앱"],
            "post_type": "listicle",
            "word_count": 800
        }
        
        generator = ContentGenerator()
        content = generator.generate_post(test_topic)
        
        print("✅ Content generation test successful!")
        print(f"Generated content length: {len(content)} characters")
        print("\n--- Generated Content Preview ---")
        print(content[:500] + "..." if len(content) > 500 else content)
        
        return True
        
    except Exception as e:
        print(f"❌ Content generation test failed: {e}")
        return False


if __name__ == "__main__":
    # 직접 실행 시 테스트
    test_content_generator()