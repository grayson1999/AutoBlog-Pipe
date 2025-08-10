#!/usr/bin/env python3
"""
Phase 2.4: 통합 테스트 - 전체 콘텐츠 생성 파이프라인 테스트
ContentGenerator + SEOGenerator 완전 통합 테스트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.generators.content_gen import ContentGenerator
from app.generators.seo_gen import SEOGenerator

def main():
    """통합 테스트 실행"""
    print("AutoBlog-Pipe Integration Test - Phase 2.4")
    print("=" * 60)
    
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
    
    # 통합 테스트 주제들 (다양한 타입으로)
    test_topics = [
        {
            "title": "2024년 최고의 개발자 도구 10선",
            "category": "technology", 
            "keywords": ["개발자 도구", "코딩 도구", "프로그래밍", "생산성"],
            "post_type": "listicle",
            "word_count": 800
        },
        {
            "title": "완벽한 원격근무 환경 만들기",
            "category": "productivity",
            "keywords": ["원격근무", "홈오피스", "업무 효율", "재택근무"],
            "post_type": "guide", 
            "word_count": 1000
        },
        {
            "title": "AI 시대의 블로그 운영 전략",
            "category": "business",
            "keywords": ["AI", "블로그", "콘텐츠 마케팅", "인공지능"],
            "post_type": "summary",
            "word_count": 600
        }
    ]
    
    try:
        # 1. 각 생성기 개별 초기화 테스트
        print("\n1. Individual generator initialization test...")
        content_gen = ContentGenerator()
        print("   OK ContentGenerator initialized")
        
        seo_gen = SEOGenerator()
        print("   OK SEOGenerator initialized")
        
        # 2. 통합 테스트 실행
        success_count = 0
        total_tests = len(test_topics)
        
        for i, topic in enumerate(test_topics, 1):
            print(f"\n{i}. Integration Test: {topic['title']}")
            print(f"   Type: {topic['post_type']} | Category: {topic['category']}")
            
            try:
                # 2-1. 개별 콘텐츠 생성 테스트
                print("   -> Testing individual content generation...")
                content = content_gen.generate_post(topic)
                print(f"   OK Content generated ({len(content)} chars)")
                
                # 2-2. 개별 SEO 요소 생성 테스트
                print("   -> Testing individual SEO elements...")
                slug = seo_gen.generate_slug(topic['title'])
                keywords = seo_gen.extract_keywords_from_content(content, topic['keywords'])
                category = seo_gen.categorize_post(topic['title'], content, keywords)
                print(f"   OK SEO elements: slug='{slug}', keywords={len(keywords)}, category='{category}'")
                
                # 2-3. 통합 전체 포스트 생성 테스트 (가장 중요!)
                print("   -> Testing integrated full post generation...")
                full_post = seo_gen.create_full_post(topic)
                print(f"   OK Full post generated ({len(full_post)} chars)")
                
                # 2-4. 구조 검증
                print("   -> Validating post structure...")
                if not validate_post_structure(full_post):
                    raise Exception("Post structure validation failed")
                print("   OK Post structure validated")
                
                # 2-5. Front matter 파싱 테스트
                print("   -> Testing front matter parsing...")
                front_matter, content_part = parse_full_post(full_post)
                if not front_matter or not content_part:
                    raise Exception("Front matter parsing failed")
                print(f"   OK Front matter parsed ({len(front_matter)} metadata fields)")
                
                success_count += 1
                print(f"   PASSED Test {i}\n")
                
                # 결과 샘플 출력
                if i == 1:  # 첫 번째 테스트만 상세 출력
                    print("--- Sample Full Post Preview ---")
                    front_matter_end = full_post.find('\n---\n') + 5
                    preview = full_post[:front_matter_end + 200]
                    print(preview + "..." if len(full_post) > len(preview) else preview)
                    print("--- End Preview ---\n")
                
            except Exception as e:
                print(f"   FAILED Test {i}: {e}")
                continue
        
        # 3. 최종 결과 출력
        print(f"\n" + "=" * 60)
        print(f"INTEGRATION TEST RESULTS")
        print(f"Passed: {success_count}/{total_tests}")
        print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")
        
        if success_count == total_tests:
            print("\nALL INTEGRATION TESTS PASSED!")
            print("Phase 2.4 Integration Testing Complete")
            print("Content + SEO generation pipeline working perfectly")
            return True
        else:
            print(f"\n{total_tests - success_count} test(s) failed")
            return False
        
    except Exception as e:
        print(f"\nCritical error in integration test: {e}")
        return False

def validate_post_structure(full_post: str) -> bool:
    """포스트 구조 검증"""
    try:
        # 1. Front matter 구조 확인
        if not full_post.startswith('---\n'):
            print("     ERROR Missing front matter start")
            return False
        
        # 2. Front matter 끝 확인
        front_matter_end = full_post.find('\n---\n')
        if front_matter_end == -1:
            print("     ERROR Missing front matter end")
            return False
        
        # 3. 콘텐츠 부분 확인
        content_part = full_post[front_matter_end + 5:].strip()
        if len(content_part) < 300:
            print(f"     ERROR Content too short ({len(content_part)} chars)")
            return False
        
        # 4. 마크다운 헤딩 확인
        if not content_part.startswith('#'):
            print("     ERROR Content doesn't start with heading")
            return False
        
        return True
        
    except Exception as e:
        print(f"     ERROR Structure validation error: {e}")
        return False

def parse_full_post(full_post: str) -> tuple:
    """Front matter와 콘텐츠 분리"""
    try:
        # Front matter 추출
        front_matter_end = full_post.find('\n---\n')
        if front_matter_end == -1:
            return None, None
        
        front_matter_raw = full_post[4:front_matter_end]  # '---\n' 다음부터
        content_part = full_post[front_matter_end + 5:].strip()  # '\n---\n' 다음부터
        
        # YAML 파싱
        import yaml
        front_matter_data = yaml.safe_load(front_matter_raw)
        
        return front_matter_data, content_part
        
    except Exception as e:
        print(f"     ERROR Parsing error: {e}")
        return None, None

def test_error_cases():
    """에러 케이스 테스트"""
    print("\n4. Error Case Testing...")
    
    try:
        seo_gen = SEOGenerator()
        
        # 빈 제목 테스트
        try:
            slug = seo_gen.generate_slug("")
            print(f"   OK Empty title handled: '{slug}'")
        except Exception as e:
            print(f"   ERROR Empty title failed: {e}")
        
        # 잘못된 토픽 테스트
        try:
            invalid_topic = {"title": "Test"}  # post_type 누락
            content_gen = ContentGenerator()
            content_gen.generate_post(invalid_topic)
            print("   ERROR Invalid topic should have failed")
        except Exception:
            print("   OK Invalid topic properly rejected")
        
        return True
        
    except Exception as e:
        print(f"   ERROR Error case testing failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting comprehensive integration test...")
    success = main()
    
    if success:
        print("\nPhase 2 Complete - Content Generation Pipeline Ready!")
        print("Next: Phase 3 - Publishing Automation Implementation")
    else:
        print("\nIntegration test failed - check errors above")
    
    sys.exit(0 if success else 1)