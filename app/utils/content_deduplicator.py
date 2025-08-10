import os
from difflib import SequenceMatcher
from typing import List, Dict, Any
import re

class ContentDeduplicator:
    def __init__(self, posts_dir: str = 'site/_posts'):
        self.posts_dir = posts_dir
        self.published_posts = self._load_published_posts()

    def _load_published_posts(self) -> List[Dict[str, Any]]:
        """`_posts` 디렉터리에서 모든 게시물의 제목을 로드합니다."""
        posts = []
        if not os.path.exists(self.posts_dir):
            return posts

        for filename in os.listdir(self.posts_dir):
            if filename.endswith('.md') or filename.endswith('.markdown'):
                filepath = os.path.join(self.posts_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 첫 번째 # 헤딩에서 제목 추출
                        match = re.search(r'^#\s*(.*)', content, re.MULTILINE)
                        if match:
                            title = match.group(1).strip()
                            posts.append({'title': title})
                except Exception as e:
                    print(f"Error loading post {filename}: {e}")
        return posts

    def _calculate_similarity(self, a: str, b: str) -> float:
        """두 문자열 간의 유사도를 계산합니다."""
        return SequenceMatcher(None, a, b).ratio()

    def check_duplicates(self, new_topic_title: str, similarity_threshold: float = 0.7) -> bool:
        """새로운 주제가 기존 콘텐츠와 중복되는지 확인합니다."""
        for post in self.published_posts:
            similarity = self._calculate_similarity(new_topic_title, post['title'])
            if similarity > similarity_threshold:
                print(f"Duplicate found: '{new_topic_title}' is {similarity:.2f} similar to '{post['title']}'")
                return True
        
        # TODO: 카테고리별 발행 주기 체크 로직 추가

        return False

if __name__ == '__main__':
    # 테스트를 위해 더미 포스트 파일 생성
    if not os.path.exists('site/_posts'):
        os.makedirs('site/_posts')
    
    dummy_post_1 = """# Complete Guide to Setting Up a Home Office

This is a guide.
"""
    dummy_post_2 = """# The Ultimate Guide to Home Office Setup

This is another guide.
"""
    with open('site/_posts/2025-01-01-dummy-post-1.md', 'w', encoding='utf-8') as f:
        f.write(dummy_post_1)
    with open('site/_posts/2025-01-02-dummy-post-2.md', 'w', encoding='utf-8') as f:
        f.write(dummy_post_2)

    deduplicator = ContentDeduplicator()
    
    # 테스트 케이스
    test_title_1 = "A Complete Guide for Home Office Setup" # 중복이어야 함
    test_title_2 = "How to be Productive at Work"      # 중복이 아니어야 함

    print(f"Checking for title: '{test_title_1}'")
    is_duplicate_1 = deduplicator.check_duplicates(test_title_1)
    print(f"Is duplicate? {is_duplicate_1}\n")

    print(f"Checking for title: '{test_title_2}'")
    is_duplicate_2 = deduplicator.check_duplicates(test_title_2)
    print(f"Is duplicate? {is_duplicate_2}\n")

    # 테스트 파일 삭제
    os.remove('site/_posts/2025-01-01-dummy-post-1.md')
    os.remove('site/_posts/2025-01-02-dummy-post-2.md')
