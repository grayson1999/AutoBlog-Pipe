#!/usr/bin/env python3
"""
콘텐츠 생성기 테스트 스크립트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.generators.content_gen import ContentGenerator

def main():
    """테스트 실행"""
    print("AutoBlog-Pipe Content Generator Test")
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
            "title": "완벽한 홈오피스 구축하는 방법",
            "category": "workspace",
            "keywords": ["홈오피스", "재택근무", "업무 환경", "생산성"],
            "post_type": "guide", 
            "word_count": 1000
        }
    ]
    
    try:
        generator = ContentGenerator()
        print(f"ContentGenerator initialized successfully")
        
        for i, topic in enumerate(test_topics, 1):
            print(f"\nTest {i}: {topic['title']}")
            print(f"   Type: {topic['post_type']}")
            print(f"   Category: {topic['category']}")
            
            try:
                content = generator.generate_post(topic)
                print(f"Generation successful! ({len(content)} chars)")
                
                # 결과 미리보기
                lines = content.split('\n')[:10]
                preview = '\n'.join(lines)
                print(f"\n--- Preview ---")
                print(preview)
                if len(content.split('\n')) > 10:
                    print("...")
                print("--- Preview End ---\n")
                
            except Exception as e:
                print(f"Generation failed: {e}")
                return False
        
        print("\nAll tests passed!")
        print("Phase 2.2 Content Generator Core Implementation Complete")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)