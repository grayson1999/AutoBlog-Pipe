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

        self.default_model = "gpt-5-mini"
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
        summarized_research = self._summarize_research_data(research_data)

        topic = {
            'title': topic_title,
            'research_data': summarized_research
        }
        
        try:
            template = self.load_prompt_template('researched')
            formatted_prompt = self.format_prompt(template, topic)

            # 4. AI 콘텐츠 생성
            generated_content = self.call_openai_api(formatted_prompt, topic_title=topic_title, summarized_research=summarized_research)

            # 5. 품질 검증
            if not self.validate_content(generated_content):
                logger.warning("Generated content failed validation, but proceeding...")

            logger.info(f"Successfully generated post with research: {topic_title}")
            return generated_content

        except Exception as e:
            logger.error(f"Failed to generate post with research for topic '{topic_title}': {e}")
            raise

    def _summarize_research_data(self, research_data: Dict[str, Any]) -> str:
        """리서치 데이터를 LLM이 이해하기 쉬운 자연어 요약으로 변환합니다."""
        summary_parts = []

        if research_data.get('key_facts'):
            summary_parts.append("Key Facts:")
            for fact in research_data['key_facts']:
                summary_parts.append(f"- {fact}")

        if research_data.get('recent_developments'):
            summary_parts.append("\nRecent Developments:")
            for dev in research_data['recent_developments']:
                title = dev.get('title', 'N/A')
                source = dev.get('source', 'N/A')
                summary_parts.append(f"- {title} (Source: {source})")

        return "\n".join(summary_parts)
    
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
    
    def call_openai_api(self, prompt: str, topic_title: str, summarized_research: str,
                        max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        max_tokens = max_tokens or self.default_max_tokens
        # ⭐ gpt-5 계열에선 temperature를 기본적으로 보내지 않도록 None 권장
        if self.default_model.startswith("gpt-5"):
            temperature = None

        for attempt in range(self.max_retries):
            try:
                api_kwargs = dict(
                    model=self.default_model,
                    messages=[
                        {"role": "system", "content": (
                            "당신은 전문 블로그 작가입니다... (생략)\n"
                            f"주제: {topic_title}\n\n리서치 데이터:\n{summarized_research}"
                        )},
                        {"role": "user", "content": prompt},
                    ],
                    # ✅ gpt-5 계열: max_tokens → max_completion_tokens
                    max_completion_tokens=max_tokens,
                )
                if temperature is not None:
                    api_kwargs["temperature"] = temperature

                response = self.client.chat.completions.create(**api_kwargs)

                generated_text = response.choices[0].message.content.strip()
                if not generated_text:
                    raise ValueError("Empty response from OpenAI API")
                return generated_text

            except Exception as e:
                msg = str(e)
                # 🔁 모델이 temperature 미지원이면 제거하고 1회 재시도
                if "temperature" in msg and "Only the default (1) value is supported" in msg and "temperature" in api_kwargs:
                    api_kwargs.pop("temperature", None)
                    response = self.client.chat.completions.create(**api_kwargs)
                    text = response.choices[0].message.content.strip()
                    if not text:
                        raise ValueError("Empty response from OpenAI API")
                    return text

                logger.error(f"OpenAI API error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay)

    
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
        """주제 정보를 바탕으로 블로그 글 생성 (레거시)""" # Legacy method
        required_fields = ['title', 'post_type']
        for field in required_fields:
            if field not in topic:
                raise ValueError(f"Missing required field: {field}")
        
        post_type = topic['post_type']
        template = self.load_prompt_template(post_type)
        formatted_prompt = self.format_prompt(template, topic)
        generated_content = self.call_openai_api(formatted_prompt, topic_title=topic['title'], summarized_research="") # summarized_research is not used in legacy mode
        
        if not self.validate_content(generated_content):
            logger.warning("Generated content failed validation, but proceeding...")
        
        return generated_content

def test_generate_post_with_research():
    """ContentGenerator의 리서치 기반 생성 테스트 함수"""
    try:
        generator = ContentGenerator()
        content = generator.generate_post_with_research("The Future of Artificial Intelligence")
        
        if content:
            print("Research-based content generation test successful!")
            print(f"Generated content length: {len(content)} characters")
            print("\n--- Generated Content Preview ---")
            print(content[:500] + "...")
        else:
            print("Content generation skipped (likely a duplicate or lack of data).")
        
        return True

    except Exception as e:
        print(f"Research-based content generation test failed: {e}")
        return False

if __name__ == "__main__":
    test_generate_post_with_research()
