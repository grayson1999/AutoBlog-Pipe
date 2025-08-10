# AutoBlog-Pipe 기능 명세서

## 🎯 시스템 개요

AutoBlog-Pipe는 AI 기반 자동 블로그 운영 시스템으로, 최소한의 개입으로 지속적인 콘텐츠 생성과 수익화를 목표로 합니다.

### 핵심 가치 제안
- **자동화**: 주제 선택부터 발행까지 무인 파이프라인
- **저비용**: 외부 API 활용으로 인프라 비용 최소화  
- **확장성**: 성공 시 멀티 사이트/채널로 복제 가능
- **수익화**: AdSense + 제휴 마케팅 통한 패시브 인컴

---

## 🏗️ 시스템 아키텍처

### 전체 데이터 플로우
```
Topic Queue (YAML) 
    ↓ (주제 선택)
Content Generator (OpenAI API)
    ↓ (마크다운 + Front Matter)  
SEO Meta Builder
    ↓ (슬러그, 키워드, 설명)
Repository Writer (GitPython)
    ↓ (Git commit & push)
Netlify CI/CD
    ↓ (Jekyll build & deploy)
Live Website + Analytics
```

### 컴포넌트 관계도
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Scheduler │───▶│    Main     │───▶│   Logger    │
│   (cron)    │    │  Pipeline   │    │             │
└─────────────┘    └─────┬───────┘    └─────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Topic Manager     │
              │  (YAML Queue)       │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │  Content Generator  │
              │   (OpenAI API)      │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   SEO Generator     │
              │ (Meta, Slug, etc)   │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │  Repository Writer  │
              │   (Git Operations)  │
              └─────────────────────┘
```

---

## 📋 기능 상세 명세

### 1. 주제 관리 (Topic Management)

#### 1.1 주제 큐 시스템
**파일**: `app/topics/topics.yml`

**구조**:
```yaml
topics:
  - title: "글 제목"
    category: "카테고리" 
    keywords: ["키워드1", "키워드2"]
    post_type: "listicle|guide|summary"
    priority: 1-10 (옵션)
    scheduled_date: "2024-01-01" (옵션)
```

**기능**:
- ✅ **정적 큐**: YAML 파일 기반 주제 목록 관리
- 🔄 **순차/랜덤 선택**: 발행 모드에 따른 주제 선택 전략
- 📊 **우선순위**: priority 필드를 통한 중요 주제 우선 처리
- 📅 **스케줄링**: scheduled_date로 특정 날짜 발행 예약

#### 1.2 동적 주제 생성 (향후 확장)
- 🔍 **트렌드 분석**: Google Trends, Reddit API 연동
- 📈 **SEO 점수**: 검색량 vs 경쟁도 분석
- 🎯 **니치 타겟팅**: 카테고리별 최적 주제 추천

### 2. AI 콘텐츠 생성 (Content Generation)

#### 2.1 프롬프트 엔진
**파일**: `app/prompts/*.txt`

**프롬프트 템플릿**:
- `post_listicle.txt`: "10가지 방법", "Top 15" 등 리스트형
- `post_guide.txt`: "완벽 가이드", "단계별 설명" 등 튜토리얼
- `post_summary.txt`: "2024년 트렌드 요약" 등 정보 압축형
- `seo_meta.txt`: 메타 설명, 키워드 추출용

**변수 시스템**:
```
{{title}} - 주제 제목
{{category}} - 카테고리  
{{keywords}} - 키워드 리스트
{{word_count}} - 목표 단어 수
{{tone}} - 어조 (formal/casual/expert)
```

#### 2.2 콘텐츠 생성기
**파일**: `app/generators/content_gen.py`

**핵심 함수**:
```python
def generate_post(topic: dict) -> str:
    """주제 딕셔너리를 받아 완성된 마크다운 반환"""
    
def load_prompt_template(post_type: str) -> str:
    """글 유형별 프롬프트 템플릿 로딩"""
    
def call_openai_api(prompt: str, max_tokens: int) -> str:
    """OpenAI API 호출 및 에러 핸들링"""
```

**품질 보장**:
- 📏 **길이 검증**: 최소 400자, 최대 2000자
- 🔍 **구조 검증**: H1, H2 헤딩 존재 확인
- 🚫 **필터링**: 부적절한 내용 감지 및 재생성
- 🔄 **재시도 로직**: API 실패 시 3회 재시도

#### 2.3 품질 관리
- **일관성**: 동일한 어조와 스타일 유지
- **원창성**: 표절 방지를 위한 유니크 콘텐츠 생성
- **정확성**: 팩트 체크 프롬프트 단계 포함 (선택적)

### 3. SEO 최적화 (SEO Optimization)

#### 3.1 메타데이터 생성
**파일**: `app/generators/seo_gen.py`

**생성 항목**:
- 📝 **슬러그**: URL 친화적 slug (영문, 하이픈)
- 📄 **메타 설명**: 150-160자 요약문  
- 🏷️ **태그**: 콘텐츠에서 추출한 관련 키워드
- 🎯 **카테고리**: 주제 분류 및 사이트 네비게이션

**Front Matter 생성**:
```yaml
---
layout: post
title: "글 제목"
date: 2024-01-15 09:00:00 +0900
categories: [category]
tags: [tag1, tag2, tag3]
excerpt: "메타 설명 (150-160자)"
slug: "seo-friendly-url-slug"
author: "AutoBot"
---
```

#### 3.2 검색 최적화 전략
- 🎯 **키워드 밀도**: 자연스러운 키워드 포함 (2-3%)
- 📊 **내부 링크**: 관련 이전 글 자동 연결
- 🖼️ **이미지 SEO**: alt 텍스트 자동 생성 (향후)
- 📱 **모바일 최적화**: 반응형 레이아웃

### 4. 발행 자동화 (Publishing Automation)

#### 4.1 저장소 관리
**파일**: `app/publishers/repo_writer.py`

**핵심 기능**:
```python
def save_post(content: str, metadata: dict) -> str:
    """마크다운 파일을 site/_posts/에 저장"""
    
def commit_and_push(file_path: str, message: str) -> bool:
    """Git 커밋 및 푸시 실행"""
    
def generate_commit_message(title: str) -> str:
    """일관된 커밋 메시지 생성"""
```

**파일 명명 규칙**:
```
site/_posts/YYYY-MM-DD-slug-name.md
예: site/_posts/2024-01-15-best-productivity-apps.md
```

#### 4.2 배포 파이프라인
1. **로컬 저장**: `site/_posts/`에 마크다운 파일 생성
2. **Git 작업**: add → commit → push to GitHub
3. **Netlify 트리거**: GitHub webhook으로 자동 빌드
4. **Jekyll 빌드**: 정적 사이트 생성 및 배포
5. **캐시 무효화**: CDN 캐시 업데이트

#### 4.3 에러 핸들링
- 🔄 **Git 충돌 해결**: pull → merge → push 재시도
- 🌐 **네트워크 오류**: 지수 백오프 재시도 전략
- 📁 **파일 권한**: 디렉터리 생성 및 권한 확인
- 🚨 **빌드 실패**: Netlify 빌드 상태 모니터링

### 5. 스케줄링 시스템 (Scheduling System)

#### 5.1 크론 작업 관리
**파일**: `Makefile` (cron-install 타겟)

**기본 스케줄**:
```bash
# 매일 오전 9시 실행
0 9 * * * cd /path/to/project && make run-once

# 주말 시드 생성 (선택)  
0 10 * * 6 cd /path/to/project && make run-seed
```

**동적 스케줄링** (향후):
- 📊 **성과 기반**: 높은 트래픽 시간대 우선 발행
- 🎯 **타겟팅**: 요일/시간별 최적화된 주제 선택
- 🔄 **빈도 조절**: AdSense 승인 전후 발행 빈도 변경

#### 5.2 실행 모드
- `--mode once`: 1개 글 생성 및 발행
- `--mode seed`: 5-10개 글 일괄 생성 (초기 시드용)
- `--mode test`: 발행 없이 생성만 테스트

### 6. 모니터링 & 로깅 (Monitoring & Logging)

#### 6.1 로그 시스템
**파일**: `app/utils/logger.py`

**로그 레벨**:
- 🟢 **INFO**: 정상 실행 상태
- 🟡 **WARNING**: 재시도 성공, 품질 이슈
- 🔴 **ERROR**: 실행 실패, API 오류
- 🔍 **DEBUG**: 상세 디버깅 정보

**로그 형식**:
```
2024-01-15 09:00:01 [INFO] 주제 선택: "10 Best Productivity Apps"
2024-01-15 09:00:15 [INFO] 콘텐츠 생성 완료 (847 단어)  
2024-01-15 09:00:18 [INFO] Git 푸시 성공: best-productivity-apps.md
2024-01-15 09:02:30 [INFO] Netlify 빌드 완료: https://site.netlify.app
```

#### 6.2 성과 추적 (향후)
- 📈 **트래픽 분석**: Google Analytics 연동
- 💰 **수익 추적**: AdSense 수익 API 연동  
- 🔍 **SEO 성과**: Search Console 순위 추적
- 📊 **콘텐츠 성과**: 글별 조회수/체류시간 분석

### 7. 수익화 시스템 (Monetization System)

#### 7.1 Google AdSense 통합
**파일**: `site/_layouts/default.html`

**광고 배치**:
- 🔝 **상단 배너**: 헤더 아래 728x90 또는 반응형
- 📱 **사이드바**: 데스크톱 우측 300x250  
- 📄 **본문 내**: 글 중간/끝 삽입
- 📱 **모바일 최적화**: 320x50 배너

**플레이스홀더**:
```html
<!-- adsense-slot-1: 상단 배너 -->
<div class="ad-placeholder" id="adsense-top">
    <!-- AdSense 승인 후 코드 삽입 -->
</div>
```

#### 7.2 제휴 마케팅
- 🛒 **제품 리뷰**: Amazon Associates, 쿠팡 파트너스
- 💼 **서비스 추천**: SaaS 제품 제휴 링크  
- 📚 **교육 콘텐츠**: Udemy, Coursera 등 코스 추천

#### 7.3 수익 최적화 전략
- 🎯 **A/B 테스트**: 광고 배치/크기 최적화
- 📊 **성과 분석**: CTR, CPC 기반 콘텐츠 전략 조정
- 🔄 **콘텐츠 최적화**: 높은 수익 주제 비중 증가

---

## 🔧 기술 명세

### 프로그래밍 언어 & 프레임워크
- **Python 3.11+**: 메인 런타임
- **Jekyll**: 정적 사이트 생성기  
- **YAML**: 설정 및 데이터 포맷
- **Markdown**: 콘텐츠 포맷

### 외부 API & 서비스  
- **OpenAI API**: GPT-3.5/4 텍스트 생성
- **GitHub API**: 저장소 관리 (GitPython)
- **Netlify**: 호스팅 및 CI/CD
- **Google Analytics**: 트래픽 분석 (선택)

### 개발 도구
- **GitPython**: Git 자동화
- **python-dotenv**: 환경변수 관리
- **Jinja2**: 템플릿 엔진  
- **unidecode**: 한글 → 영문 슬러그 변환

---

## 📊 성능 & 확장성

### 시스템 요구사항
- **최소 사양**: RAM 4GB, 저장 공간 10GB
- **권장 사양**: RAM 8GB, SSD 20GB
- **네트워크**: 안정적인 인터넷 연결 (API 호출)

### 확장성 고려사항
- **수평 확장**: 멀티 사이트 운영 (다른 니치)
- **수직 확장**: 발행 빈도 증가 (일 3-5회)  
- **채널 확장**: YouTube, 뉴스레터, 소셜미디어
- **지역화**: 다국어 콘텐츠 지원

### 성능 최적화
- **API 비용 관리**: 글자 수 제한, 캐싱 활용
- **빌드 시간 단축**: 증분 빌드, 이미지 최적화
- **SEO 성능**: 사이트맵, robots.txt 자동 생성

---

## 🚨 리스크 & 대응 전략

### 기술적 리스크
- **API 장애**: 대체 API 준비, 로컬 백업
- **빌드 실패**: 롤백 메커니즘, 상태 복구
- **컨텐츠 품질**: 품질 검증 체크포인트

### 사업적 리스크  
- **AdSense 정책**: 콘텐츠 품질 기준 준수
- **저작권**: AI 생성 콘텐츠 원창성 확보
- **SEO 패널티**: 과도한 자동화 방지

### 운영 리스크
- **서버 장애**: 클라우드 백업, 모니터링
- **비용 관리**: API 사용량 제한, 예산 알림  
- **유지보수**: 자동화된 모니터링 & 알림

---

## 🎯 성공 지표 (KPI)

### 기술적 성공 지표
- ✅ **가동 시간**: 99%+ 정상 실행률
- 📊 **콘텐츠 품질**: 평균 글자 수 800+, 구조화된 포맷
- ⚡ **빌드 시간**: 5분 이내 배포 완료

### 사업적 성공 지표  
- 📈 **트래픽**: 월 10,000 PV 이상
- 💰 **수익**: AdSense 월 $50+ (3개월 내)
- 🔍 **SEO**: 타겟 키워드 구글 1-3 페이지 랭킹

### 운영적 성공 지표
- 🤖 **자동화 비율**: 95%+ 무인 운영
- 📝 **콘텐츠 볼륨**: 월 30개 이상 발행
- 🎯 **확장성**: 6개월 내 2번째 사이트 런칭

**최종 목표**: 개입 없이 연간 $1,000+ 패시브 인컴 달성 🎉