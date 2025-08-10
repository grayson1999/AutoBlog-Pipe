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
from typing import Dict, List, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import Config
from app.generators.content_gen import ContentGenerator
from app.generators.seo_gen import SEOGenerator
from app.publishers.repo_writer import RepoWriter
from app.utils.topic_loader import TopicLoader
from app.collectors.idea_collector import IdeaCollector

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
        self.content_generator = ContentGenerator()
        self.seo_generator = SEOGenerator()
        self.repo_writer = RepoWriter()
        self.topic_loader = TopicLoader()
        self.idea_collector = IdeaCollector()
        
        logger.info("All components initialized successfully")
    
    def select_topic(self, mode: str = 'once') -> List[Dict[str, Any]]:
        """
        주제 선택 로직 (기존 topics.yml 기반)
        
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

    def generate_and_publish_post(self, topic: Dict[str, Any], generated_content: Optional[str] = None) -> Dict[str, Any]:
        """
        단일 포스트 생성 및 발행
        
        Args:
            topic (Dict): 주제 정보
            generated_content (str, optional): 이미 생성된 콘텐츠 (dynamic 모드에서 사용)
        
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
            
            if generated_content:
                # dynamic 모드: 이미 생성된 콘텐츠 사용
                final_content = generated_content
                logger.info("Using pre-generated content from dynamic pipeline.")
            else:
                # 기존 topics.yml 모드: SEO Generator를 통해 콘텐츠 생성
                logger.info("Generating complete post with SEO metadata (legacy mode)...")
                final_content = self.seo_generator.create_full_post(topic)
            
            if len(final_content) < 500:
                raise ValueError(f"Generated post too short: {len(final_content)} chars")
            
            logger.info(f"Post content ready ({len(final_content)} chars)")
            
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
                    post_content=final_content,
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

    def run_dynamic_pipeline(self, count: int = 1) -> Dict[str, Any]:
        """
        동적 콘텐츠 생성 파이프라인 실행 (아이디어 수집 -> 리서치 -> 생성 -> 발행)
        
        Args:
            count (int): 생성할 포스트 수. 1이면 once, 5-10이면 seed와 유사
        """
        pipeline_result = {
            'mode': 'dynamic',
            'success_count': 0,
            'total_count': 0,
            'posts': [],
            'errors': []
        }

        logger.info(f"Starting dynamic content generation pipeline for {count} posts...")
        if self.dry_run:
            logger.info("DRY RUN MODE - No actual publishing")

        collected_ideas = self.idea_collector.collect_trending_topics()
        if not collected_ideas:
            logger.warning("No ideas collected. Exiting dynamic pipeline.")
            return pipeline_result

        # 아이디어를 무한히 순환하며 사용 (중복 방지 로직이 있으므로)
        idea_iterator = iter(collected_ideas)
        
        posts_to_generate = count
        generated_posts_count = 0
        total_ideas_processed = 0
        max_ideas_to_process = len(collected_ideas) * 3 # 무한 루프 방지

        while generated_posts_count < posts_to_generate and total_ideas_processed < max_ideas_to_process:
            total_ideas_processed += 1
            try:
                # 아이디어가 고갈되면 다시 수집 (또는 기존 아이디어 재활용)
                try:
                    idea = next(idea_iterator)
                except StopIteration:
                    logger.info("Ran out of initial ideas, collecting more...")
                    new_ideas = self.idea_collector.collect_trending_topics()
                    if not new_ideas:
                        logger.warning("No new ideas collected. Stopping.")
                        break
                    collected_ideas.extend(new_ideas) # 기존 아이디어에 추가
                    idea_iterator = iter(new_ideas) # 새로 수집한 아이디어부터 시작
                    idea = next(idea_iterator) # 새로 수집한 아이디어에서 첫 번째 가져오기

                topic_title = idea.get('title', 'Untitled Idea')
                logger.info(f"Attempting to generate post for: {topic_title} (Processed idea {total_ideas_processed})")
                
                # generate_post_with_research 내부에서 중복 체크 및 리서치 수행
                generated_content = self.content_generator.generate_post_with_research(
                    topic_title=topic_title,
                    category='AI_Trends', # 동적 파이프라인 기본 카테고리
                    keywords=[] # 키워드는 리서치에서 추출하거나 AI가 생성하도록
                )

                if generated_content:
                    # 생성된 콘텐츠를 바탕으로 발행
                    publish_topic = {'title': topic_title, 'post_type': 'article', 'category': 'AI_Trends', 'tags': extracted_tags}
                    post_result = self.generate_and_publish_post(publish_topic, generated_content=generated_content)
                    pipeline_result['posts'].append(post_result)
                    
                    if post_result['success']:
                        pipeline_result['success_count'] += 1
                        generated_posts_count += 1
                    else:
                        pipeline_result['errors'].append(post_result['error'])
                else:
                    logger.info(f"Skipped generation for '{topic_title}' (e.g., duplicate or insufficient research).")
                    pipeline_result['errors'].append(f"Skipped: {topic_title}")

            except Exception as e:
                error_msg = f"Failed to process dynamic idea '{topic_title}': {e}"
                logger.error(error_msg)
                pipeline_result['errors'].append(error_msg)

        pipeline_result['total_count'] = generated_posts_count # 실제로 생성된 포스트 수
        success_rate = (pipeline_result['success_count'] / pipeline_result['total_count']) * 100 if pipeline_result['total_count'] > 0 else 0
        logger.info(f"Dynamic pipeline completed: {pipeline_result['success_count']}/{pipeline_result['total_count']} posts ({success_rate:.1f}% success)")
        
        if pipeline_result['errors']:
            logger.warning(f"Errors/Skips encountered: {len(pipeline_result['errors'])}")
            for error in pipeline_result['errors']:
                logger.warning(f"  - {error}")

        return pipeline_result

    def run_pipeline(self, mode: str = 'once', count: Optional[int] = None) -> Dict[str, Any]:
        """
        완전한 파이프라인 실행
        
        Args:
            mode (str): 실행 모드 ('once', 'seed', 'dynamic')
            count (int, optional): dynamic 모드에서 생성할 포스트 수
        
        Returns:
            Dict: 전체 실행 결과
        """
        if mode == 'dynamic':
            return self.run_dynamic_pipeline(count=count if count is not None else 1)
        
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
    parser.add_argument('--mode', choices=['once', 'seed', 'dynamic'], default='once',
                       help='Execution mode: once (single post), seed (5-10 posts), or dynamic (collect ideas and generate)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test mode - generate content but do not publish')
    parser.add_argument('--count', type=int, default=1,
                       help='Number of posts to generate in dynamic mode (default: 1)')
    
    args = parser.parse_args()
    
    try:
        # 환경 설정 검증
        logger.info("Validating configuration...")
        Config.validate()
        
        # 파이프라인 실행
        pipeline = AutoBlogPipeline(dry_run=args.dry_run)
        result = pipeline.run_pipeline(args.mode, count=args.count)
        
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
            elif args.mode == 'dynamic':
                print("\nDynamic pipeline complete! Check your Netlify deployment for new posts!")
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