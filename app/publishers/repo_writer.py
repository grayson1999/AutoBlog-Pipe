"""
Git 리포지토리 퍼블리셔 모듈
마크다운 파일 저장, Git 커밋/푸시 자동화
"""

import os
import git
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from ..config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepoWriter:
    """Git 리포지토리 퍼블리셔"""
    
    def __init__(self, repo_path: Optional[str] = None, site_dir: Optional[str] = None):
        """
        RepoWriter 초기화
        
        Args:
            repo_path (str, optional): Git 저장소 경로. None이면 프로젝트 루트 사용
            site_dir (str, optional): Jekyll 사이트 디렉터리. None이면 기본값 사용
        """
        # 경로 설정
        self.repo_path = Path(repo_path or Config.PROJECT_ROOT)
        self.site_dir = Path(site_dir or Config.SITE_DIR)
        self.posts_dir = self.site_dir / '_posts'
        
        # Git 저장소 확인 및 초기화
        self._init_repo()
        
        # 설정값
        self.default_branch = 'main'
        self.commit_message_template = Config.GIT_COMMIT_TEMPLATE or "feat: 새 블로그 글 발행 - {title}"
        
        logger.info(f"RepoWriter initialized - repo: {self.repo_path}, posts: {self.posts_dir}")
    
    def _init_repo(self):
        """Git 저장소 초기화 및 검증"""
        try:
            # Git 저장소 확인
            self.repo = git.Repo(self.repo_path)
            logger.info(f"Git repository detected: {self.repo_path}")
            
            # posts 디렉터리 생성
            self.posts_dir.mkdir(parents=True, exist_ok=True)
            
        except git.exc.InvalidGitRepositoryError:
            logger.error(f"Not a Git repository: {self.repo_path}")
            raise ValueError(f"Directory is not a Git repository: {self.repo_path}")
        except Exception as e:
            logger.error(f"Error initializing Git repository: {e}")
            raise
    
    def generate_post_filename(self, title: str, date: Optional[datetime] = None) -> str:
        """
        Jekyll 블로그 포스트 파일명 생성
        
        Args:
            title (str): 글 제목
            date (datetime, optional): 발행 날짜. None이면 현재 시간
        
        Returns:
            str: Jekyll 파일명 규칙에 맞는 파일명
        """
        if not date:
            date = datetime.now()
        
        # Jekyll 파일명 형식: YYYY-MM-DD-title.md
        date_str = date.strftime('%Y-%m-%d')
        
        # 제목을 파일명으로 변환 (영문 슬러그 사용)
        from ..generators.seo_gen import SEOGenerator
        seo_gen = SEOGenerator()
        slug = seo_gen.generate_slug(title)
        
        filename = f"{date_str}-{slug}.md"
        
        logger.info(f"Generated filename: '{title}' -> '{filename}'")
        return filename
    
    def save_post(self, post_content: str, title: str, 
                  date: Optional[datetime] = None) -> Path:
        """
        블로그 포스트를 Jekyll _posts 디렉터리에 저장
        
        Args:
            post_content (str): 완전한 마크다운 콘텐츠 (Front Matter 포함)
            title (str): 글 제목
            date (datetime, optional): 발행 날짜
        
        Returns:
            Path: 저장된 파일의 전체 경로
            
        Raises:
            Exception: 파일 저장 실패 시
        """
        try:
            # 파일명 생성
            filename = self.generate_post_filename(title, date)
            file_path = self.posts_dir / filename
            
            # 중복 파일명 체크
            if file_path.exists():
                logger.warning(f"File already exists: {filename}")
                # 시간 추가로 중복 방지
                timestamp = datetime.now().strftime('%H%M%S')
                name_parts = filename.rsplit('.', 1)
                filename = f"{name_parts[0]}-{timestamp}.{name_parts[1]}"
                file_path = self.posts_dir / filename
            
            # 파일 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(post_content)
            
            logger.info(f"Post saved successfully: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving post '{title}': {e}")
            raise
    
    def generate_commit_message(self, title: str, post_type: str = None, 
                               category: str = None) -> str:
        """
        자동 커밋 메시지 생성
        
        Args:
            title (str): 글 제목
            post_type (str, optional): 글 유형
            category (str, optional): 카테고리
        
        Returns:
            str: 생성된 커밋 메시지
        """
        try:
            # 기본 템플릿 사용
            if '{title}' in self.commit_message_template:
                message = self.commit_message_template.format(title=title)
            else:
                message = f"feat: 새 블로그 글 발행 - {title}"
            
            # 추가 정보가 있으면 포함
            details = []
            if post_type:
                details.append(f"유형: {post_type}")
            if category:
                details.append(f"카테고리: {category}")
            
            if details:
                message += f"\n\n- {chr(10).join('- ' + detail for detail in details)}"
            
            # 자동 생성 표시
            message += "\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n"
            message += "\nCo-Authored-By: Claude <noreply@anthropic.com>"
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating commit message: {e}")
            return f"feat: 새 블로그 글 발행 - {title}"
    
    def commit_and_push(self, file_path: Path, commit_message: str, 
                       push: bool = True) -> Dict[str, Any]:
        """
        Git add, commit, push 실행
        
        Args:
            file_path (Path): 추가할 파일 경로
            commit_message (str): 커밋 메시지
            push (bool): 원격 저장소에 푸시 여부
        
        Returns:
            Dict: 실행 결과 정보
        """
        result = {
            'success': False,
            'commit_hash': None,
            'pushed': False,
            'error': None
        }
        
        try:
            # Git 상태 확인
            if self.repo.is_dirty():
                logger.info("Repository has uncommitted changes")
            
            # 파일을 staging area에 추가
            relative_path = file_path.relative_to(self.repo_path)
            self.repo.index.add([str(relative_path)])
            logger.info(f"Added to staging: {relative_path}")
            
            # 커밋 생성
            commit = self.repo.index.commit(commit_message)
            result['commit_hash'] = commit.hexsha
            result['success'] = True
            logger.info(f"Committed successfully: {commit.hexsha[:8]}")
            
            # 원격 저장소에 푸시
            if push:
                try:
                    origin = self.repo.remote('origin')
                    push_info = origin.push(self.default_branch)
                    
                    if push_info:
                        result['pushed'] = True
                        logger.info(f"Pushed to remote: {self.default_branch}")
                    else:
                        logger.warning("Push completed but no push info returned")
                        result['pushed'] = True
                        
                except git.exc.GitCommandError as e:
                    logger.error(f"Push failed: {e}")
                    result['error'] = f"Push failed: {str(e)}"
                    # 커밋은 성공했으므로 success는 True로 유지
                except Exception as e:
                    logger.error(f"Unexpected error during push: {e}")
                    result['error'] = f"Push error: {str(e)}"
            
            return result
            
        except git.exc.GitCommandError as e:
            error_msg = f"Git command failed: {e}"
            logger.error(error_msg)
            result['error'] = error_msg
            return result
        except Exception as e:
            error_msg = f"Unexpected error during Git operations: {e}"
            logger.error(error_msg)
            result['error'] = error_msg
            return result
    
    def publish_post(self, post_content: str, title: str, 
                    post_type: str = None, category: str = None,
                    date: Optional[datetime] = None, 
                    push: bool = True) -> Dict[str, Any]:
        """
        완전한 포스트 발행 프로세스: 저장 + Git 커밋 + 푸시
        
        Args:
            post_content (str): 완전한 마크다운 콘텐츠
            title (str): 글 제목
            post_type (str, optional): 글 유형
            category (str, optional): 카테고리
            date (datetime, optional): 발행 날짜
            push (bool): 원격 저장소에 푸시 여부
        
        Returns:
            Dict: 발행 결과 정보
        """
        result = {
            'success': False,
            'file_path': None,
            'commit_hash': None,
            'pushed': False,
            'error': None
        }
        
        try:
            # 1. 파일 저장
            logger.info(f"Starting post publication: {title}")
            file_path = self.save_post(post_content, title, date)
            result['file_path'] = str(file_path)
            
            # 2. 커밋 메시지 생성
            commit_message = self.generate_commit_message(title, post_type, category)
            
            # 3. Git 커밋 및 푸시
            git_result = self.commit_and_push(file_path, commit_message, push)
            
            # 결과 병합
            result.update(git_result)
            
            if result['success']:
                logger.info(f"Post published successfully: {title}")
                logger.info(f"File: {file_path}")
                logger.info(f"Commit: {result['commit_hash']}")
                if result['pushed']:
                    logger.info("Successfully pushed to remote repository")
            else:
                logger.error(f"Publication failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Publication failed for '{title}': {e}"
            logger.error(error_msg)
            result['error'] = error_msg
            return result
    
    def get_repo_status(self) -> Dict[str, Any]:
        """
        저장소 상태 정보 반환
        
        Returns:
            Dict: 저장소 상태 정보
        """
        try:
            status = {
                'branch': self.repo.active_branch.name,
                'is_dirty': self.repo.is_dirty(),
                'untracked_files': self.repo.untracked_files,
                'modified_files': [item.a_path for item in self.repo.index.diff(None)],
                'staged_files': [item.a_path for item in self.repo.index.diff('HEAD')],
                'last_commit': {
                    'hash': self.repo.head.commit.hexsha[:8],
                    'message': self.repo.head.commit.message.strip(),
                    'date': self.repo.head.commit.committed_datetime.isoformat()
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting repo status: {e}")
            return {'error': str(e)}


def test_repo_writer():
    """RepoWriter 테스트 함수"""
    try:
        # 테스트용 간단한 포스트
        test_post = """---
layout: post
title: "테스트 포스트"
date: 2025-08-10 19:20:00 +0900
categories:
- test
tags:
- test
author: AutoBot
---

# 테스트 포스트

이것은 RepoWriter 테스트용 포스트입니다.

## 내용

- 테스트 항목 1
- 테스트 항목 2
- 테스트 항목 3

테스트가 성공하면 이 파일이 _posts 디렉터리에 저장되고 Git에 커밋됩니다.
"""
        
        writer = RepoWriter()
        
        # 저장소 상태 확인
        status = writer.get_repo_status()
        print(f"Repository status: {status['branch']} branch")
        print(f"Dirty: {status['is_dirty']}")
        
        # 포스트 발행 (푸시 안함)
        result = writer.publish_post(
            test_post, 
            "테스트 포스트", 
            post_type="test",
            category="test",
            push=False  # 테스트니까 푸시 안함
        )
        
        if result['success']:
            print("✅ RepoWriter test successful!")
            print(f"File saved: {result['file_path']}")
            print(f"Commit: {result['commit_hash']}")
        else:
            print(f"❌ RepoWriter test failed: {result['error']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ RepoWriter test failed: {e}")
        return False


if __name__ == "__main__":
    # 직접 실행 시 테스트
    test_repo_writer()