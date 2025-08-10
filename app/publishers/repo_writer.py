"""
Git 리포지토리 퍼블리셔 모듈
마크다운 파일 저장, Git 커밋/푸시 자동화
"""

import os
import git
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List
import yaml

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
        self.commit_message_template = Config.GIT_COMMIT_MESSAGE_TEMPLATE or "feat: 새 블로그 글 발행 - {title}"
        
        logger.info(f"RepoWriter initialized - repo: {self.repo_path}, posts: {self.posts_dir}")
    
    def _init_repo(self):
        """
        Git 저장소 초기화 및 검증
        """
        try:
            self.repo = git.Repo(self.repo_path)
            logger.info(f"Git repository detected: {self.repo_path}")
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
        """
        if not date:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        
        from ..generators.seo_gen import SEOGenerator
        seo_gen = SEOGenerator()
        slug = seo_gen.generate_slug(title)
        
        filename = f"{date_str}-{slug}.md"
        
        logger.info(f"Generated filename: '{title}' -> '{filename}'")
        return filename
    
    def save_post(self, post_content: str, title: str, 
                  date: Optional[datetime] = None, 
                  category: str = 'general', tags: Optional[List[str]] = None) -> Path:
        """
        블로그 포스트를 Jekyll _posts 디렉터리에 저장
        """
        if not date:
            date = datetime.now()

        # Front Matter 생성
        front_matter = {
            'layout': 'post',
            'title': title,
            'date': date.strftime('%Y-%m-%d %H:%M:%S +0900'), # KST 기준
            'categories': [category],
            'tags': tags if tags is not None else [],
            'author': 'AutoBot'
        }
        
        front_matter_str = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False)
        
        full_content = f"---\n{front_matter_str}---\n\n{post_content}"

        try:
            filename = self.generate_post_filename(title, date)
            file_path = self.posts_dir / filename
            
            if file_path.exists():
                logger.warning(f"File already exists: {filename}")
                timestamp = datetime.now().strftime('%H%M%S')
                name_parts = filename.rsplit('.', 1)
                filename = f"{name_parts[0]}-{timestamp}.{name_parts[1]}"
                file_path = self.posts_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Post saved successfully: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving post '{title}': {e}")
            raise
    
    def generate_commit_message(self, title: str, post_type: str = None, 
                               category: str = None, tags: Optional[List[str]] = None) -> str:
        """
        자동 커밋 메시지 생성
        """
        try:
            message = self.commit_message_template.format(title=title)
            
            details = []
            if post_type:
                details.append(f"유형: {post_type}")
            if category:
                details.append(f"카테고리: {category}")
            if tags:
                details.append(f"태그: {', '.join(tags)}")
            
            if details:
                message += f"\n\n- {chr(10).join('- ' + detail for detail in details)}"
            
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
        """
        result = {
            'success': False,
            'commit_hash': None,
            'pushed': False,
            'error': None
        }
        
        try:
            if self.repo.is_dirty():
                logger.info("Repository has uncommitted changes")
            
            relative_path = file_path.relative_to(self.repo_path)
            self.repo.index.add([str(relative_path)])
            logger.info(f"Added to staging: {relative_path}")
            
            commit = self.repo.index.commit(commit_message)
            result['commit_hash'] = commit.hexsha
            result['success'] = True
            logger.info(f"Committed successfully: {commit.hexsha[:8]}")
            
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
            return result
    
    def publish_post(self, post_content: str, title: str, 
                    post_type: str = None, category: str = 'general', tags: Optional[List[str]] = None,
                    date: Optional[datetime] = None, 
                    push: bool = True) -> Dict[str, Any]:
        """
        완전한 포스트 발행 프로세스: 저장 + Git 커밋 + 푸시
        """
        result = {
            'success': False,
            'file_path': None,
            'commit_hash': None,
            'pushed': False,
            'error': None
        }
        
        try:
            logger.info(f"Starting post publication: {title}")
            file_path = self.save_post(post_content, title, date, category, tags)
            result['file_path'] = str(file_path)
            
            commit_message = self.generate_commit_message(title, post_type, category, tags)
            
            git_result = self.commit_and_push(file_path, commit_message, push)
            
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
        test_post_content = """# 테스트 포스트\n\n이것은 RepoWriter 테스트용 포스트입니다.\n\n## 내용\n\n- 테스트 항목 1\n- 테스트 항목 2\n- 테스트 항목 3\n\n테스트가 성공하면 이 파일이 _posts 디렉터리에 저장되고 Git에 커밋됩니다.\nTags: [test, repo, writer]\n"""
        
        writer = RepoWriter()
        
        status = writer.get_repo_status()
        print(f"Repository status: {status['branch']} branch")
        print(f"Dirty: {status['is_dirty']}")
        
        result = writer.publish_post(
            test_post_content, 
            "테스트 포스트", 
            post_type="test",
            category="test",
            tags=["test", "repo", "writer"],
            push=False
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
    test_repo_writer()
