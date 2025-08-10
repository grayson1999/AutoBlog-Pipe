#!/usr/bin/env python3
"""
AutoBlog-Pipe Main Entry Point
Complete content generation and publishing pipeline
"""

import argparse
import sys
import logging
import random
from pathlib import Path
from typing import Dict, List, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import Config
from app.generators.seo_gen import SEOGenerator
from app.publishers.repo_writer import RepoWriter
from app.utils.topic_loader import TopicLoader

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoBlogPipeline:
    """AutoBlog 완전 자동화 파이프라인"""
    
    def __init__(self, dry_run: bool = False):
        """
        파이프라인 초기화
        
        Args:
            dry_run (bool): True면 실제 발행하지 않고 테스트만
        """
        self.dry_run = dry_run
        
        # 컴포넌트 초기화
        logger.info("Initializing AutoBlog Pipeline components...")
        self.seo_generator = SEOGenerator()
        self.repo_writer = RepoWriter()
        self.topic_loader = TopicLoader()
        
        logger.info("All components initialized successfully")
    
    def select_topic(self, mode: str = 'once') -> List[Dict[str, Any]]:
        """
        주제 선택 로직
        
        Args:
            mode (str): 'once' 또는 'seed'
        
        Returns:
            List[Dict]: 선택된 주제 목록
        """
        try:
            # 모든 주제 로드
            all_topics = self.topic_loader.load_topics()
            
            if not all_topics:
                raise ValueError("No topics available in topics.yml")
            
            if mode == 'once':
                # 랜덤하게 1개 선택
                selected = [random.choice(all_topics)]
                logger.info(f"Selected 1 topic: {selected[0]['title']}")
            elif mode == 'seed':
                # 5-10개 랜덤 선택
                count = min(random.randint(5, 10), len(all_topics))
                selected = random.sample(all_topics, count)
                logger.info(f"Selected {count} topics for seed mode")
                for topic in selected:
                    logger.info(f"  - {topic['title']}")
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            return selected
            
        except Exception as e:
            logger.error(f"Error selecting topics: {e}")
            raise
    
    def generate_and_publish_post(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        단일 포스트 생성 및 발행
        
        Args:
            topic (Dict): 주제 정보
        
        Returns:
            Dict: 실행 결과
        """
        result = {
            'success': False,
            'title': topic.get('title', 'Unknown'),
            'file_path': None,
            'commit_hash': None,
            'error': None
        }
        
        try:
            logger.info(f"Processing: {topic['title']}")
            
            # 1. 완전한 포스트 생성 (콘텐츠 + SEO)
            logger.info("Generating complete post with SEO metadata...")
            full_post = self.seo_generator.create_full_post(topic)
            
            if len(full_post) < 500:
                raise ValueError(f"Generated post too short: {len(full_post)} chars")
            
            logger.info(f"Post generated successfully ({len(full_post)} chars)")
            
            # 2. 발행 처리
            if self.dry_run:
                logger.info("DRY RUN: Would publish to repository")
                result['success'] = True
                result['file_path'] = "DRY_RUN_NO_FILE"
                result['commit_hash'] = "DRY_RUN_NO_COMMIT"
            else:
                # 실제 발행
                logger.info("Publishing to repository...")
                publish_result = self.repo_writer.publish_post(
                    post_content=full_post,
                    title=topic['title'],
                    post_type=topic.get('post_type', 'article'),
                    category=topic.get('category', 'general'),
                    push=True  # 원격 저장소에 푸시
                )
                
                if publish_result['success']:
                    result.update(publish_result)
                    logger.info(f"Successfully published: {topic['title']}")
                else:
                    raise Exception(f"Publishing failed: {publish_result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to process '{topic['title']}': {e}"
            logger.error(error_msg)
            result['error'] = error_msg
            return result
    
    def run_pipeline(self, mode: str = 'once') -> Dict[str, Any]:
        """
        완전한 파이프라인 실행
        
        Args:
            mode (str): 실행 모드 ('once' 또는 'seed')
        
        Returns:
            Dict: 전체 실행 결과
        """
        pipeline_result = {
            'mode': mode,
            'success_count': 0,
            'total_count': 0,
            'posts': [],
            'errors': []
        }
        
        try:
            logger.info(f"Starting AutoBlog Pipeline in {mode} mode")
            if self.dry_run:
                logger.info("DRY RUN MODE - No actual publishing")
            
            # 1. 주제 선택
            topics = self.select_topic(mode)
            pipeline_result['total_count'] = len(topics)
            
            # 2. 각 주제별로 포스트 생성 및 발행
            for i, topic in enumerate(topics, 1):
                logger.info(f"Processing {i}/{len(topics)}: {topic['title']}")
                
                post_result = self.generate_and_publish_post(topic)
                pipeline_result['posts'].append(post_result)
                
                if post_result['success']:
                    pipeline_result['success_count'] += 1
                else:
                    pipeline_result['errors'].append(post_result['error'])
            
            # 3. 결과 출력
            success_rate = (pipeline_result['success_count'] / pipeline_result['total_count']) * 100
            logger.info(f"Pipeline completed: {pipeline_result['success_count']}/{pipeline_result['total_count']} posts ({success_rate:.1f}% success)")
            
            if pipeline_result['errors']:
                logger.warning(f"Errors encountered: {len(pipeline_result['errors'])}")
                for error in pipeline_result['errors']:
                    logger.warning(f"  - {error}")
            
            return pipeline_result
            
        except Exception as e:
            error_msg = f"Pipeline failed: {e}"
            logger.error(error_msg)
            pipeline_result['errors'].append(error_msg)
            return pipeline_result


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='AutoBlog-Pipe: AI-powered blog automation')
    parser.add_argument('--mode', choices=['once', 'seed'], default='once',
                       help='Execution mode: once (single post) or seed (5-10 posts)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test mode - generate content but do not publish')
    
    args = parser.parse_args()
    
    try:
        # 환경 설정 검증
        logger.info("Validating configuration...")
        Config.validate()
        
        # 파이프라인 실행
        pipeline = AutoBlogPipeline(dry_run=args.dry_run)
        result = pipeline.run_pipeline(args.mode)
        
        # 최종 결과
        if result['success_count'] > 0:
            print(f"\nSUCCESS: Generated and published {result['success_count']} posts")
            for post in result['posts']:
                if post['success']:
                    print(f"  - {post['title']}")
                    if not args.dry_run:
                        print(f"    File: {post['file_path']}")
                        print(f"    Commit: {post['commit_hash'][:8] if post['commit_hash'] else 'N/A'}")
            
            if args.mode == 'once':
                print("\nNext: Check your Netlify deployment for the new post!")
            else:
                print(f"\nSeed mode complete! {result['success_count']} posts ready for AdSense application")
            
            return 0
        else:
            print(f"\nFAILED: No posts were successfully generated")
            return 1
            
    except Exception as e:
        logger.error(f"AutoBlog-Pipe failed: {e}")
        print(f"ERROR: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())