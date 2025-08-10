#!/usr/bin/env python3
"""
크론 설정 자동화 스크립트
Windows Task Scheduler와 Unix Cron 모두 지원
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from datetime import datetime
import json

# 프로젝트 루트를 파이썬 패스에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.config import Config
    from app.utils.logger import get_logger
except ImportError:
    print("[ERROR] Failed to import AutoBlog modules. Run from project root.")
    sys.exit(1)


class CronSetup:
    """크론/스케줄러 설정 클래스"""
    
    def __init__(self):
        self.logger = get_logger()
        self.project_root = project_root
        self.python_path = sys.executable
        self.main_script = self.project_root / "app" / "main.py"
        
        # 기본 스케줄 설정
        self.schedules = {
            "daily": {
                "time": "09:00",
                "description": "Daily blog post generation"
            },
            "twice_daily": {
                "time": ["09:00", "21:00"], 
                "description": "Blog post generation twice daily"
            },
            "hourly": {
                "time": "*/1 * * * *",  # Unix cron format
                "description": "Hourly blog post generation (testing)"
            }
        }
        
        self.logger.info("[CRON] CronSetup initialized")
    
    def detect_platform(self) -> str:
        """플랫폼 감지"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system in ["linux", "darwin"]:  # Darwin = macOS
            return "unix"
        else:
            self.logger.warning(f"[CRON] Unsupported platform: {system}")
            return "unknown"
    
    def create_windows_task(self, schedule_type: str = "daily") -> bool:
        """Windows Task Scheduler 작업 생성"""
        try:
            schedule = self.schedules.get(schedule_type, self.schedules["daily"])
            task_name = f"AutoBlog-Pipe-{schedule_type}"
            
            # 배치 파일 생성
            batch_file = self.create_batch_file()
            
            # Task Scheduler XML 생성
            xml_file = self.create_task_xml(task_name, batch_file, schedule)
            
            # schtasks 명령으로 작업 등록
            cmd = [
                "schtasks", "/create",
                "/tn", task_name,
                "/xml", str(xml_file),
                "/f"  # 기존 작업이 있으면 덮어쓰기
            ]
            
            self.logger.info(f"[CRON] Creating Windows task: {task_name}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self.logger.info(f"[CRON] Windows task created successfully: {task_name}")
            self.logger.debug(f"[CRON] schtasks output: {result.stdout}")
            
            # XML 파일 정리
            xml_file.unlink()
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"[CRON] Failed to create Windows task: {e.stderr}", exception=e)
            return False
        except Exception as e:
            self.logger.error(f"[CRON] Error creating Windows task", exception=e)
            return False
    
    def create_batch_file(self) -> Path:
        """AutoBlog 실행용 배치 파일 생성"""
        batch_content = f'''@echo off
REM AutoBlog-Pipe Execution Script
REM Generated on {datetime.now()}

cd /d "{self.project_root}"

REM Set environment variables if .env exists
if exist ".env" (
    echo [INFO] Loading environment from .env
)

REM Run AutoBlog in dynamic mode
echo [INFO] Starting AutoBlog-Pipe in dynamic mode...
"{self.python_path}" app/main.py --mode dynamic

REM Log completion
echo [INFO] AutoBlog-Pipe execution completed at %date% %time%
'''
        
        batch_file = self.project_root / "scripts" / "run_autoblog.bat"
        batch_file.parent.mkdir(exist_ok=True)
        
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        self.logger.info(f"[CRON] Batch file created: {batch_file}")
        return batch_file
    
    def create_task_xml(self, task_name: str, batch_file: Path, schedule: dict) -> Path:
        """Windows Task Scheduler XML 생성"""
        time_str = schedule["time"] if isinstance(schedule["time"], str) else schedule["time"][0]
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
    <RegistrationInfo>
        <Date>{datetime.now().isoformat()}</Date>
        <Author>AutoBlog-Pipe</Author>
        <Description>{schedule["description"]}</Description>
    </RegistrationInfo>
    <Triggers>
        <CalendarTrigger>
            <StartBoundary>{datetime.now().strftime('%Y-%m-%d')}T{time_str}:00</StartBoundary>
            <Enabled>true</Enabled>
            <ScheduleByDay>
                <DaysInterval>1</DaysInterval>
            </ScheduleByDay>
        </CalendarTrigger>
    </Triggers>
    <Principals>
        <Principal id="Author">
            <UserId>S-1-5-32-545</UserId>
            <LogonType>InteractiveToken</LogonType>
            <RunLevel>LeastPrivilege</RunLevel>
        </Principal>
    </Principals>
    <Settings>
        <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
        <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
        <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
        <AllowHardTerminate>true</AllowHardTerminate>
        <StartWhenAvailable>true</StartWhenAvailable>
        <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
        <IdleSettings>
            <StopOnIdleEnd>true</StopOnIdleEnd>
            <RestartOnIdle>false</RestartOnIdle>
        </IdleSettings>
        <AllowStartOnDemand>true</AllowStartOnDemand>
        <Enabled>true</Enabled>
        <Hidden>false</Hidden>
        <RunOnlyIfIdle>false</RunOnlyIfIdle>
        <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
        <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
        <WakeToRun>false</WakeToRun>
        <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
        <Priority>7</Priority>
    </Settings>
    <Actions Context="Author">
        <Exec>
            <Command>cmd</Command>
            <Arguments>/c "{batch_file}"</Arguments>
            <WorkingDirectory>{self.project_root}</WorkingDirectory>
        </Exec>
    </Actions>
</Task>'''
        
        xml_file = self.project_root / "scripts" / f"{task_name}.xml"
        xml_file.parent.mkdir(exist_ok=True)
        
        with open(xml_file, 'w', encoding='utf-16') as f:
            f.write(xml_content)
        
        return xml_file
    
    def create_unix_cron(self, schedule_type: str = "daily") -> bool:
        """Unix/Linux 크론잡 생성"""
        try:
            schedule = self.schedules.get(schedule_type, self.schedules["daily"])
            
            # 셸 스크립트 생성
            shell_script = self.create_shell_script()
            
            # 크론 시간 형식 변환
            if schedule_type == "daily":
                cron_time = f"0 9 * * *"  # 매일 오전 9시
            elif schedule_type == "twice_daily":
                # 두 개의 크론잡 생성
                cron_jobs = [
                    f"0 9 * * * {shell_script}  # AutoBlog morning",
                    f"0 21 * * * {shell_script}  # AutoBlog evening"
                ]
            elif schedule_type == "hourly":
                cron_time = f"0 * * * *"  # 매시간
            else:
                cron_time = f"0 9 * * *"  # 기본값
            
            # 단일 크론잡인 경우
            if schedule_type != "twice_daily":
                cron_jobs = [f"{cron_time} {shell_script}  # AutoBlog-Pipe {schedule_type}"]
            
            # 기존 crontab 백업 및 새 잡 추가
            return self.install_cron_jobs(cron_jobs)
            
        except Exception as e:
            self.logger.error(f"[CRON] Error creating Unix cron", exception=e)
            return False
    
    def create_shell_script(self) -> Path:
        """Unix용 셸 스크립트 생성"""
        script_content = f'''#!/bin/bash
# AutoBlog-Pipe Execution Script
# Generated on {datetime.now()}

cd "{self.project_root}"

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "[INFO] Loading environment from .env"
    source .env
fi

# Run AutoBlog in dynamic mode
echo "[INFO] Starting AutoBlog-Pipe in dynamic mode..."
"{self.python_path}" app/main.py --mode dynamic

# Log completion
echo "[INFO] AutoBlog-Pipe execution completed at $(date)"
'''
        
        script_file = self.project_root / "scripts" / "run_autoblog.sh"
        script_file.parent.mkdir(exist_ok=True)
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 실행 권한 부여
        script_file.chmod(0o755)
        
        self.logger.info(f"[CRON] Shell script created: {script_file}")
        return script_file
    
    def install_cron_jobs(self, cron_jobs: list) -> bool:
        """크론잡 설치"""
        try:
            # 현재 crontab 백업
            current_cron = subprocess.run(
                ["crontab", "-l"], 
                capture_output=True, text=True
            )
            
            existing_jobs = []
            if current_cron.returncode == 0:
                existing_jobs = current_cron.stdout.strip().split('\n')
            
            # AutoBlog 관련 기존 잡 제거
            filtered_jobs = [job for job in existing_jobs 
                           if "AutoBlog" not in job and job.strip()]
            
            # 새 잡 추가
            all_jobs = filtered_jobs + cron_jobs
            
            # 임시 크론 파일 생성
            temp_cron = self.project_root / "scripts" / "temp_cron.txt"
            with open(temp_cron, 'w') as f:
                f.write('\n'.join(all_jobs) + '\n')
            
            # 크론탭 업데이트
            result = subprocess.run(
                ["crontab", str(temp_cron)],
                capture_output=True, text=True, check=True
            )
            
            # 임시 파일 삭제
            temp_cron.unlink()
            
            self.logger.info(f"[CRON] Successfully installed {len(cron_jobs)} cron jobs")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"[CRON] Failed to install cron jobs: {e.stderr}", exception=e)
            return False
        except Exception as e:
            self.logger.error(f"[CRON] Error installing cron jobs", exception=e)
            return False
    
    def list_scheduled_jobs(self):
        """현재 설정된 스케줄 작업 목록"""
        platform_type = self.detect_platform()
        
        if platform_type == "windows":
            return self.list_windows_tasks()
        elif platform_type == "unix":
            return self.list_unix_crons()
        else:
            self.logger.error("[CRON] Cannot list jobs on unsupported platform")
            return []
    
    def list_windows_tasks(self) -> list:
        """Windows 예약된 작업 목록"""
        try:
            result = subprocess.run(
                ["schtasks", "/query", "/fo", "csv"],
                capture_output=True, text=True, check=True
            )
            
            tasks = []
            for line in result.stdout.strip().split('\n')[1:]:  # 헤더 제외
                if "AutoBlog" in line:
                    tasks.append(line.strip().split('","')[0].strip('"'))
            
            return tasks
            
        except subprocess.CalledProcessError:
            return []
    
    def list_unix_crons(self) -> list:
        """Unix 크론잡 목록"""
        try:
            result = subprocess.run(
                ["crontab", "-l"], 
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                return []
            
            crons = []
            for line in result.stdout.strip().split('\n'):
                if "AutoBlog" in line:
                    crons.append(line.strip())
            
            return crons
            
        except Exception:
            return []
    
    def remove_scheduled_jobs(self) -> bool:
        """스케줄된 작업 제거"""
        platform_type = self.detect_platform()
        
        if platform_type == "windows":
            return self.remove_windows_tasks()
        elif platform_type == "unix":
            return self.remove_unix_crons()
        else:
            self.logger.error("[CRON] Cannot remove jobs on unsupported platform")
            return False
    
    def remove_windows_tasks(self) -> bool:
        """Windows 예약 작업 제거"""
        try:
            tasks = self.list_windows_tasks()
            success = True
            
            for task in tasks:
                try:
                    subprocess.run(
                        ["schtasks", "/delete", "/tn", task, "/f"],
                        capture_output=True, text=True, check=True
                    )
                    self.logger.info(f"[CRON] Removed Windows task: {task}")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"[CRON] Failed to remove task {task}: {e.stderr}")
                    success = False
            
            return success
            
        except Exception as e:
            self.logger.error("[CRON] Error removing Windows tasks", exception=e)
            return False
    
    def remove_unix_crons(self) -> bool:
        """Unix 크론잡 제거"""
        try:
            current_cron = subprocess.run(
                ["crontab", "-l"], 
                capture_output=True, text=True
            )
            
            if current_cron.returncode != 0:
                return True  # 크론잡이 없으면 성공으로 간주
            
            # AutoBlog 관련 잡 제외한 나머지만 유지
            filtered_jobs = [job for job in current_cron.stdout.strip().split('\n') 
                           if "AutoBlog" not in job and job.strip()]
            
            # 임시 크론 파일 생성 및 업데이트
            temp_cron = self.project_root / "scripts" / "temp_cron.txt"
            with open(temp_cron, 'w') as f:
                f.write('\n'.join(filtered_jobs) + '\n')
            
            subprocess.run(
                ["crontab", str(temp_cron)],
                capture_output=True, text=True, check=True
            )
            
            temp_cron.unlink()
            
            self.logger.info("[CRON] Removed all AutoBlog cron jobs")
            return True
            
        except Exception as e:
            self.logger.error("[CRON] Error removing Unix cron jobs", exception=e)
            return False


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AutoBlog-Pipe 크론 설정 관리')
    parser.add_argument('action', choices=['install', 'list', 'remove'], 
                       help='수행할 작업')
    parser.add_argument('--schedule', choices=['daily', 'twice_daily', 'hourly'],
                       default='daily', help='스케줄 유형 (설치 시)')
    
    args = parser.parse_args()
    
    cron_setup = CronSetup()
    platform_type = cron_setup.detect_platform()
    
    if platform_type == "unknown":
        print("[ERROR] Unsupported platform")
        return 1
    
    if args.action == "install":
        print(f"[INFO] Installing {args.schedule} schedule on {platform_type}...")
        
        if platform_type == "windows":
            success = cron_setup.create_windows_task(args.schedule)
        else:
            success = cron_setup.create_unix_cron(args.schedule)
        
        if success:
            print(f"[SUCCESS] {args.schedule} schedule installed successfully!")
            print(f"[INFO] AutoBlog will run automatically according to schedule")
        else:
            print("[ERROR] Failed to install schedule")
            return 1
    
    elif args.action == "list":
        jobs = cron_setup.list_scheduled_jobs()
        
        if jobs:
            print(f"[INFO] Found {len(jobs)} AutoBlog scheduled jobs:")
            for job in jobs:
                print(f"  - {job}")
        else:
            print("[INFO] No AutoBlog scheduled jobs found")
    
    elif args.action == "remove":
        print("[INFO] Removing all AutoBlog scheduled jobs...")
        
        success = cron_setup.remove_scheduled_jobs()
        
        if success:
            print("[SUCCESS] All AutoBlog scheduled jobs removed")
        else:
            print("[ERROR] Failed to remove some scheduled jobs")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())