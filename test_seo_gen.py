#!/usr/bin/env python3
"""
SEO 메타데이터 생성기 테스트 스크립트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.generators.seo_gen import SEOGenerator

def main():
    """테스트 실행"""
    print("AutoBlog-Pipe SEO Generator Test")
    print("=" * 50)
    
    # .env 파일 확인
    env_file = project_root / '.env'
    if not env_file.exists():
        print("Error: .env file not found.")
        print("Please create .env file based on .env.example and set OPENAI_API_KEY.")
        return False
    
    # OpenAI API 키 확인
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not set.")
        print("Please add OPENAI_API_KEY to .env file.")
        return False
    
    print(f"OpenAI API Key confirmed: {api_key[:8]}...")
    
    # 테스트 주제들
    test_topics = [
        {
            "title": "2024년 최고의 생산성 앱 10선",
            "category": "productivity", 
            "keywords": ["생산성 앱", "업무 효율", "모바일 앱", "업무 도구"],
            "post_type": "listicle",
            "word_count": 800
        },
        {
            "title": "AI 도구로 업무 자동화하는 방법",
            "category": "technology",
            "keywords": ["AI 도구", "업무 자동화", "인공지능", "효율성"],
            "post_type": "guide", 
            "word_count": 1000
        }
    ]
    
    try:
        seo_gen = SEOGenerator()
        print("SEOGenerator initialized successfully")
        
        for i, topic in enumerate(test_topics, 1):
            print(f"\nTest {i}: {topic['title']}")
            print(f"   Type: {topic['post_type']}")
            print(f"   Category: {topic['category']}")
            
            try:
                # 1. 슬러그 생성 테스트
                slug = seo_gen.generate_slug(topic['title'])
                print(f"   Generated slug: {slug}")
                
                # 2. 키워드 추출 테스트 (간단한 더미 콘텐츠)
                dummy_content = f"# {topic['title']}\n\n## 주요 내용\n\n업무 효율성을 높이는 방법에 대해 알아보겠습니다."
                keywords = seo_gen.extract_keywords_from_content(dummy_content, topic['keywords'])
                print(f"   Extracted keywords: {keywords}")
                
                # 3. 카테고리 분류 테스트
                category = seo_gen.categorize_post(topic['title'], dummy_content, keywords)
                print(f"   Categorized as: {category}")
                
                # 4. 완전한 포스트 생성 테스트 (OpenAI API 호출)
                print("   Generating full post with AI...")
                full_post = seo_gen.create_full_post(topic)
                print(f"   Full post generated! ({len(full_post)} chars)")
                
                # 5. Front Matter 부분 출력
                front_matter_end = full_post.find('\n---\n') + 5
                front_matter = full_post[:front_matter_end] if front_matter_end > 5 else full_post[:500]
                print(f"\n--- Front Matter Preview ---")
                print(front_matter)
                print("--- End Preview ---\n")
                
            except Exception as e:
                print(f"   Test failed: {e}")
                return False
        
        print("\nAll SEO generation tests passed!")
        print("Phase 2.3 SEO Meta Generator Implementation Complete")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)