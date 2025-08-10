"""
AI 콘텐츠 생성 모듈
OpenAI API를 활용한 블로그 글 자동 생성
"""

import os
import time
import logging
import json
from pathlib import Path
from typing import Dict, Optional, Any, List

try:
    from openai import OpenAI
    import openai
except ImportError:
    raise ImportError("OpenAI library not found. Install with: pip install openai")

from ..config import Config
from ..research.content_researcher import ContentResearcher
from ..utils.content_deduplicator import ContentDeduplicator

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
        
        self.client = OpenAI(api_key=self.api_key)
        self.prompts_dir = Config.PROMPTS_DIR
        
        self.default_model = "gpt-3.5-turbo"
        self.default_max_tokens = 2500
        self.default_temperature = 0.7
        self.max_retries = 3
        self.retry_delay = 1
        
        logger.info("ContentGenerator initialized successfully")

    def generate_post_with_research(self, topic_title: str, category: str = 'Tech', keywords: List[str] = []) -> Optional[str]:
        """리서치 기반으로 블로그 글을 생성하는 전체 파이프라인"""
        logger.info(f"--- Starting research-based generation for: {topic_title} ---")

        # 1. 중복 체크
        deduplicator = ContentDeduplicator()
        if deduplicator.check_duplicates(topic_title):
            logger.warning(f"Topic '{topic_title}' is a duplicate. Skipping generation.")
            return None

        # 2. 리서치 수행
        researcher = ContentResearcher()
        research_data = researcher.research_topic(topic_title)

        if not research_data.get('key_facts') and not research_data.get('recent_developments'):
            logger.error(f"Not enough research data found for '{topic_title}'. Skipping generation.")
            return None

        # 3. 프롬프트 준비
        topic = {
            'title': topic_title,
            'category': category,
            'keywords': keywords,
            'word_count': 1200,
            'research_data': json.dumps(research_data, indent=2, ensure_ascii=False)
        }
        
        try:
            template = self.load_prompt_template('researched')
            formatted_prompt = self.format_prompt(template, topic)

            # 4. AI 콘텐츠 생성
            generated_content = self.call_openai_api(formatted_prompt)

            # 5. 품질 검증
            if not self.validate_content(generated_content):
                logger.warning("Generated content failed validation, but proceeding...")

            logger.info(f"Successfully generated post with research: {topic_title}")
            return generated_content

        except Exception as e:
            logger.error(f"Failed to generate post with research for topic '{topic_title}': {e}")
            raise
    
    def load_prompt_template(self, post_type: str) -> str:
        """프롬프트 템플릿 파일 로드"""
        template_file = self.prompts_dir / f"post_{post_type}.txt"
        if not template_file.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_file}")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading prompt template {post_type}: {e}")
            raise
    
    def format_prompt(self, template: str, topic: Dict[str, Any]) -> str:
        """프롬프트 템플릿에 주제 정보를 채워넣어 실제 프롬프트 생성"""
        topic_data = {
            'title': topic.get('title', '제목 없음'),
            'category': topic.get('category', '일반'),
            'keywords': ', '.join(topic.get('keywords', [])),
            'word_count': topic.get('word_count', 800),
            'content': topic.get('content', ''),
            'research_data': topic.get('research_data', '{}')
        }
        
        try:
            return template.format(**topic_data)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise ValueError(f"Template formatting failed: missing variable {e}")
    
    def call_openai_api(self, prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        """OpenAI API 호출하여 텍스트 생성"""
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.default_model,
                    messages=[
                        {"role": "system", "content": "당신은 전문적인 블로그 작가입니다. 고품질의 유익하고 실용적인 콘텐츠를 작성합니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                generated_text = response.choices[0].message.content.strip()
                if not generated_text:
                    raise ValueError("Empty response from OpenAI API")
                return generated_text
            except Exception as e:
                logger.error(f"OpenAI API error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay)
        
        raise Exception(f"Failed to generate content after {self.max_retries} attempts")
    
    def validate_content(self, content: str, min_length: int = 500) -> bool:
        """생성된 콘텐츠 품질 검증"""
        if not content or len(content.strip()) < min_length:
            logger.warning(f"Content too short: {len(content)} characters (minimum: {min_length})")
            return False
        if not content.strip().startswith('#'):
            logger.warning("Content doesn't start with proper heading")
            return False
        if content.count('\n##') < 2:
            logger.warning(f"Content has too few sections: {content.count('##')}")
            return False
        return True
    
    def generate_post(self, topic: Dict[str, Any]) -> str:
        """주제 정보를 바탕으로 블로그 글 생성 (레거시)"""
        required_fields = ['title', 'post_type']
        for field in required_fields:
            if field not in topic:
                raise ValueError(f"Missing required field: {field}")
        
        post_type = topic['post_type']
        template = self.load_prompt_template(post_type)
        formatted_prompt = self.format_prompt(template, topic)
        generated_content = self.call_openai_api(formatted_prompt)
        
        if not self.validate_content(generated_content):
            logger.warning("Generated content failed validation, but proceeding...")
        
        return generated_content

def test_generate_post_with_research():
    """ContentGenerator의 리서치 기반 생성 테스트 함수"""
    try:
        generator = ContentGenerator()
        content = generator.generate_post_with_research("The Future of Artificial Intelligence")
        
        if content:
            print("✅ Research-based content generation test successful!")
            print(f"Generated content length: {len(content)} characters")
            print("\n--- Generated Content Preview ---")
            print(content[:500] + "...")
        else:
            print("⚠️ Content generation skipped (likely a duplicate or lack of data).")
        
        return True

    except Exception as e:
        print(f"❌ Research-based content generation test failed: {e}")
        return False

if __name__ == "__main__":
    test_generate_post_with_research()
