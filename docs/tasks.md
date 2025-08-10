# AutoBlog-Pipe 구현 태스크 가이드

> 6시간 내 완성을 위한 단계별 구현 가이드

## 🎯 전체 로드맵

```
Phase 0: 스캐폴딩 (30-40m) ✅ 완료
Phase 1: 사이트 골격 & 배포 (40-50m) ✅ 완료  
Phase 2: 콘텐츠 생성기 (60-80m) ✅ 완료
Phase 3: 발행 자동화 (40-50m) ✅ 완료  
Phase 4: 스케줄링 & 로깅 (30-40m) ✅ 완료
Phase 5: 초기 콘텐츠 & 런칭 (40-50m) 🚧 다음 단계
```

**🔥 지속가능한 콘텐츠 파이프라인 완성!**
```
Phase 2.5: Content Idea Collector (아이디어 수집) ✅ 완료
    ↓
Phase 2.6: Content Research Engine (리서치/검증) ✅ 완료  
    ↓
Phase 2.7: Content Deduplication (중복 체크) ✅ 완료
    ↓
Phase 2.8: Enhanced Content Generation (콘텐츠 생성) ✅ 완료
```

## 🎉 **핵심 파이프라인 완성!** (Phase 0-3)

**AutoBlog-Pipe 메인 기능 100% 작동 중:**
- ✅ AI 콘텐츠 자동 생성 (OpenAI GPT-3.5-turbo)
- ✅ SEO 최적화 자동화 (슬러그, 메타 설명, 키워드)
- ✅ Jekyll 블로그 자동 발행 (Front Matter 완벽 생성)  
- ✅ Git/GitHub 완전 자동화 (커밋, 푸시)
- ✅ Netlify 자동 배포 연동

**사용법:**
```bash
# 블로그 글 1개 자동 생성 & 발행 (기존 topics.yml 방식)
python app/main.py --mode once

# 블로그 글 5-10개 일괄 생성 (AdSense용)  
python app/main.py --mode seed

# 🆕 동적 콘텐츠 생성 (RSS/뉴스 기반, 중복 체크, 자동 리서치)
python app/main.py --mode dynamic

# 동적 모드로 여러 글 생성
python app/main.py --mode dynamic --count 3

# 테스트 모드 (실제 발행 안함)
python app/main.py --mode dynamic --dry-run
```

---
## 🚀 Phase 2.5 ~ 2.8: 지속가능한 콘텐츠 시스템 구축

> `topics.yml`의 정적 목록 방식에서 벗어나, 외부 트렌드를 반영하는 동적 콘텐츠 파이프라인을 구축합니다.

### 🎯 구현 우선순위
1. **Phase 2.5 (핵심)**: Google Trends + RSS 기반 아이디어 수집기
2. **Phase 2.7 (필수)**: 제목 유사도 기반 기본 중복 체크
3. **Phase 2.6 (고도화)**: Wikipedia + News API 기반 리서치 엔진
4. **Phase 2.8 (통합)**: 리서치 데이터를 활용한 콘텐츠 생성

---
**실제 작동 확인:**
- ✅ `2025-08-10-complete-guide-to-setting-up-a-home-office.md` 자동 생성
- ✅ Git 커밋: `dd4705c1 feat: 새 블로그 글 발행 - Complete Guide to Setting Up a Home Office`  
- ✅ GitHub 원격 푸시 성공
- ✅ Netlify 자동 배포 트리거

**핵심 컴포넌트:**
- `app/generators/content_gen.py` - AI 콘텐츠 생성기
- `app/generators/seo_gen.py` - SEO 메타데이터 생성기  
- `app/publishers/repo_writer.py` - Git 퍼블리셔
- `app/main.py` - 통합 파이프라인
- `app/utils/topic_loader.py` - 주제 관리

---

## Phase 0: 스캐폴딩 & 환경 세팅 ✅ 완료 (30-40m)

### 완료된 작업
- [x] requirements.txt 생성
- [x] .env.example 템플릿 생성
- [x] Makefile 구성 (setup, run-once, run-seed, cron-install)
- [x] 프로젝트 디렉터리 구조 생성
- [x] 기본 config.py 모듈 생성
- [x] topics.yml 샘플 주제 8개 추가
- [x] .gitignore 설정

### DoD 확인
- ✅ `pip install -r requirements.txt` 성공
- ✅ `python -c "import openai, yaml"` 성공

---

## Phase 1: 사이트 골격 & 배포 연결 ✅ 완료 (40-50m)

### 1.1 Jekyll 레이아웃 완성 (15m)
- [x] `site/_config.yml` 업데이트 
- [x] `site/_layouts/default.html` (헤더/푸터, AdSense 플레이스홀더)
- [x] `site/_layouts/post.html` (블로그 글 레이아웃)
- [x] `site/_layouts/page.html` (고정 페이지 레이아웃)
- [x] `site/index.html` (최근 글 목록 루프)

### 1.2 기본 페이지 생성 (10m)
- [x] `site/pages/about.md` (소개 페이지 초안)
- [x] `site/pages/privacy.md` (개인정보처리방침)

### 1.3 Netlify 배포 설정 (15m)
- [x] GitHub 리포지토리 원격 연결
- [x] Netlify에서 GitHub 리포 연결
- [x] 빌드 설정 확인 (Jekyll)
- [x] 도메인 설정 (auto-comgong.netlify.app)

### DoD
- [x] 리포 main 푸시 → Netlify 빌드 성공 & URL 공개
- [x] 인덱스/페이지가 기본 레이아웃으로 보임
- [x] 레이아웃에 `<!-- adsense-slot-1 -->` 플레이스홀더 존재

---

## Phase 2: 콘텐츠 생성기 구현 ✅ 완료 (60-80m)

### 2.1 프롬프트 템플릿 작성 (15m)
- [x] `app/prompts/post_listicle.txt` (리스트형 글)
- [x] `app/prompts/post_guide.txt` (가이드형 글)  
- [x] `app/prompts/post_summary.txt` (요약형 글)
- [x] `app/prompts/post_seo_meta.txt` (SEO 메타데이터)

### 2.2 콘텐츠 생성기 코어 (35m)
- [x] `app/generators/content_gen.py`
  - [x] OpenAI API 클라이언트 설정 (httpx 0.27.2 호환)
  - [x] 프롬프트 로딩 함수
  - [x] 주제 → 마크다운 글 생성 함수  
  - [x] 에러 핸들링 & 재시도 로직 (3회 재시도)
  - [x] 콘텐츠 품질 검증 (길이, 헤딩 구조 확인)

### 2.3 SEO 메타 생성기 (15m)  
- [x] `app/generators/seo_gen.py`
  - [x] 제목 → SEO 친화적 슬러그 생성 (unidecode 활용)
  - [x] AI 기반 메타 설명, 키워드 자동 생성
  - [x] 카테고리 자동 분류 시스템
  - [x] Jekyll Front matter YAML 완벽 생성
  - [x] 완전한 포스트 생성 (콘텐츠 + SEO 통합)

### 2.4 통합 테스트 (15m)
- [x] `test_integration.py` - 완전한 파이프라인 테스트
- [x] 단일 주제로 전체 플로우 테스트
- [x] 생성된 마크다운 파일 구조 검증
- [x] Front Matter 파싱 및 검증
- [x] 에러 케이스 테스트 (짧은 콘텐츠, 잘못된 토픽)

### DoD
- [x] `python test_content_gen.py` 성공 (개별 콘텐츠 생성)
- [x] `python test_seo_gen.py` 성공 (SEO 메타데이터 생성)
- [x] `python test_integration.py` 성공 (통합 테스트)
- [x] 생성된 MD 파일이 올바른 front matter + 본문 구조
- [x] API 실패 시 적절한 에러 메시지 및 재시도
- [x] OpenAI 종속성 문제 해결 (httpx 0.27.2 고정)

### Phase 2.5: Content Idea Collector ✅ 완료 (30분)

**목표**: 외부 소스에서 트렌디한 주제를 자동으로 수집하고 필터링합니다.

- [x] `app/collectors/idea_collector.py` 클래스 생성
- [x] **RSS Feeds 수집**: `feedparser` 라이브러리 활용, 여러 기술/뉴스 블로그 피드 파싱
- [x] **필터링 및 중복 제거**: 기본적인 중복 아이디어 제거 로직 구현
- [x] **아이디어 스코어링**: 트렌드 지수, 검색량, 관련성을 기반으로 아이디어 점수화 (기본 점수 구현)
- [x] 6개 주요 RSS 피드 연동: TechCrunch, Wired, The Verge, Ars Technica, Engadget, O'Reilly
- [⚠️] **Google Trends 연동**: `pytrends` 라이브러리 연동 완료했으나, 현재 API 404 오류로 임시 비활성화됨.

### Phase 2.6: Content Research Engine ✅ 완료 (45분)

**목표**: 선정된 주제에 대해 깊이 있는 정보를 자동으로 리서치하고 검증합니다.

- [x] `app/research/content_researcher.py` 클래스 생성
- [x] **Wikipedia API 연동**: `wikipedia` 라이브러리 활용, 주제의 핵심 정보 및 요약 수집
- [x] **News API 연동**: `newsapi-python` 활용, 최신 뉴스 및 동향 수집
- [x] **리서치 데이터 구조화**: 핵심 정보, 최신 뉴스, 관련 용어, 소스 정보를 체계적으로 정리
- [x] **에러 핸들링**: Wikipedia 모호성, News API 한도 등 다양한 예외 상황 처리
- [ ] (Optional) 웹 스크래핑: `BeautifulSoup`, `requests` 활용, 특정 사이트에서 통계/인용문 수집

### Phase 2.7: Content Deduplication ✅ 완료 (30분)

**목표**: 발행될 콘텐츠가 기존 콘텐츠와 중복되지 않도록 방지합니다.

- [x] `app/utils/content_deduplicator.py` 클래스 생성
- [x] **기존 발행 글 로드**: `site/_posts` 디렉터리에서 모든 글의 제목과 메타데이터 로드
- [x] **유사도 체크**: `difflib` 활용, 신규 주제와 기존 글 제목 간의 유사도 측정 (70% 임계값)
- [x] **키워드 중복 체크**: 제목에서 키워드를 추출하여 60% 이상 겹치는 경우 중복으로 판단
- [x] **Jekyll Front Matter 파싱**: YAML 형식의 메타데이터를 정확히 추출하여 중복 검사 수행

### Phase 2.8: Enhanced Content Generation ✅ 완료 (30분)

**목표**: 리서치된 데이터를 활용하여 더 풍부하고 정확한 콘텐츠를 생성합니다.

- [x] `app/generators/content_gen.py` 개선
  - [x] `generate_post_with_research` 함수 추가
  - [x] **동적 프롬프트 생성**: 리서치 데이터(핵심 정보, 통계, 뉴스 등)를 프롬프트 템플릿에 동적으로 주입
  - [x] **리서치 데이터 요약**: Wikipedia 정보와 뉴스 정보를 자연어로 요약하여 AI가 활용하기 쉽게 변환
- [x] `app/prompts/post_researched.txt` 템플릿 생성: 리서치 기반 콘텐츠 생성을 위한 전용 프롬프트
- [x] **품질 검증 시스템**: 기본적인 길이, 구조, 헤딩 검증 수행

## 🔧 **시스템 복구 및 완성** ✅ 완료 (2025-08-10)

### 주요 버그 수정 및 기능 완성
- [x] **태그 기능 완전 수정**: `main.py`에서 `tags` 파라미터가 `publish_post`에 누락되어 Front Matter에 빈 태그가 생성되던 문제 해결
- [x] **동적 파이프라인 통합**: `--mode dynamic` 완전 작동, RSS 피드 수집 → 리서치 → 중복 체크 → 콘텐츠 생성 → 발행까지 전체 플로우 완성
- [x] **태그 추출 로직 강화**: `_extract_tags_from_content()` 함수로 제목과 콘텐츠에서 기술 키워드 자동 추출
- [x] **중복 방지 시스템**: 기존 발행 글과 70% 이상 유사한 제목은 자동으로 스킵하는 시스템 완성
- [x] **에러 복구**: 누락된 모듈들(`content_researcher.py`, `content_deduplicator.py`, `idea_collector.py`) 재생성 및 통합

### 실제 테스트 결과
```bash
# 성공적으로 작동하는 명령어들
python app/main.py --mode dynamic --dry-run  # ✅ 테스트 성공
python app/main.py --mode dynamic             # ✅ 실제 발행 성공

# 생성된 실제 포스트 예시
- RIP, Microsoft Lens, a simple little app that's getting replaced by AI
- The next big AI model is here
```

### 시스템 현재 상태
- ✅ **100% 작동**: RSS 기반 동적 콘텐츠 생성 파이프라인
- ✅ **완벽한 태그 시스템**: Jekyll Front Matter에 정확한 태그 배열 생성
- ✅ **중복 방지**: 기존 글과의 중복 자동 감지 및 스킵
- ✅ **Git 자동화**: 커밋 메시지 자동 생성 및 원격 푸시
- ✅ **연구 기반 콘텐츠**: Wikipedia + News API 연동으로 정확한 정보 기반 글 생성

---

## Phase 3: 발행 자동화 구현 ✅ 완료 (40-50m)

### 3.1 Git 퍼블리셔 구현 (25m)
- [x] `app/publishers/repo_writer.py` - 완전한 Git 퍼블리셔
  - [x] 마크다운 파일 저장 (`site/_posts/`) - Jekyll 파일명 규칙
  - [x] SEO 친화적 파일명 자동 생성 (날짜-슬러그.md)
  - [x] Git 커밋 메시지 자동 생성 (템플릿 지원)
  - [x] Git add, commit, push 완전 자동화
  - [x] 에러 핸들링 (충돌, 네트워크 오류, 중복 파일명)
  - [x] 저장소 상태 추적 및 검증

### 3.2 메인 파이프라인 완성 (15m)
- [x] `app/main.py` 완전한 AutoBlogPipeline 클래스
  - [x] `app/utils/topic_loader.py` - topics.yml 로더 및 검증  
  - [x] 주제 선택 로직 (랜덤 선택, 카테고리별 필터)
  - [x] 생성 → 발행 전체 플로우 완전 자동화
  - [x] `--mode once` vs `--mode seed` 로직 (1개 vs 5-10개)
  - [x] `--dry-run` 테스트 모드 지원
  - [x] 상세한 로깅 및 결과 리포트

### 3.3 동적 파이프라인 통합 ✅ 완료 (30분)
- [x] `app/main.py`에 `IdeaCollector`, `ContentResearcher`, `ContentDeduplicator` 통합
- [x] `--mode dynamic` 옵션 추가 및 동적 파이프라인 실행 로직 구현
- [x] `generate_and_publish_post` 함수 개선 (생성된 콘텐츠를 인자로 받을 수 있도록)
- [x] `dynamic` 모드에서 `count` 인자 지원 및 중복 시 다른 아이디어 시도 로직 구현

### DoD  
- [x] `python app/main.py --mode once` 실행 성공
- [x] 새 글이 `site/_posts/`에 올바른 Jekyll 형식으로 생성
- [x] Git 커밋 및 GitHub 원격 푸시 자동화
- [x] Netlify 자동 빌드 트리거 확인
- [x] 완전한 Front Matter + SEO 메타데이터 포함
- [x] 실제 AI 블로그 글 발행 성공 확인
- [x] 에러 처리 및 상태 추적 시스템



## Phase 4: 스케줄링 & 로깅 ✅ 완료 (30-40m)

### 4.1 고급 로깅 시스템 ✅ 완료 (20m)
- [x] `app/utils/logger.py` - 완전한 로깅 시스템 구현
  - [x] **다중 로그 핸들러**: 파일 로깅 + 콘솔 로깅 + 에러 전용 로깅
  - [x] **로그 로테이션**: 자동 파일 회전 (5MB 제한, 5개 백업)
  - [x] **성능 모니터링**: API 호출 시간, 파이프라인 실행 시간 추적
  - [x] **파이프라인 전용 로깅**: 시작/완료, 성공률, 중복 스킵, Git 작업 등
  - [x] **구조화된 로그**: JSON 형태의 추가 데이터와 함께 저장

### 4.2 스케줄링 자동화 ✅ 완료 (25m)
- [x] `scripts/cron_setup.py` - 크로스 플랫폼 스케줄러 관리
  - [x] **Windows Task Scheduler** 지원 (XML 기반 작업 생성)
  - [x] **Unix/Linux Cron** 지원 (crontab 자동 관리)
  - [x] **플랫폼 자동 감지** 및 적절한 스케줄러 선택
  - [x] **배치/셸 스크립트 자동 생성** (환경변수 로딩 포함)
  - [x] **스케줄 관리**: 일일, 2회/일, 시간별 옵션 지원
- [x] **Makefile 통합**: `make cron-install/list/remove` 명령어
- [x] **동적 파이프라인 기본값**: 크론 실행 시 자동으로 `--mode dynamic` 사용

### 4.3 고급 예외 처리 ✅ 완료 (15m)
- [x] `app/utils/error_handler.py` - 종합적인 에러 복구 시스템
  - [x] **OpenAI API 에러**: Rate Limit, Timeout, Connection 에러 처리
  - [x] **네트워크 에러**: 지수 백오프 재시도, HTTP 세션 관리
  - [x] **Git 작업 에러**: 네트워크 장애, 인증 오류 구분 처리
  - [x] **시스템 건강도 체크**: 디스크 공간, 네트워크 연결, 로그 디렉터리
  - [x] **우아한 종료**: KeyboardInterrupt, SystemExit 처리
- [x] **main.py 통합**: 모든 예외 타입별 맞춤 처리 및 복구 로직

### 4.4 메인 파이프라인 강화 ✅ 완료 (10m)  
- [x] `app/main.py` 고급 기능 추가
  - [x] **시스템 상태 확인**: 시작 시 자동 건강도 체크
  - [x] **로그 레벨 조정**: `--log-level DEBUG/INFO/WARNING/ERROR`
  - [x] **상세한 에러 분석**: 실패 원인별 구분된 메시지
  - [x] **성능 추적**: 파이프라인 실행 시간 및 성공률 로깅

### DoD ✅ 모든 항목 완료
- [x] `make cron-install` 실행 → Windows/Unix 환경에 스케줄 작업 등록
- [x] 로그 파일에서 실행 히스토리 확인 가능 (`logs/autoblog.log`)
- [x] 에러 전용 로그 분리 (`logs/errors.log`)
- [x] 크론 실행 시 동적 파이프라인 자동 실행 확인

---

## Phase 5: 초기 콘텐츠 & 런칭 ⏳ 대기 (40-50m)

### 5.1 초기 시드 콘텐츠 생성 (20m)
- [ ] `make run-seed` 구현 (5-10개 글 일괄 생성)
- [ ] 생성된 글들 품질 1차 검토
- [ ] 문제 있는 글 수동 수정/재생성

### 5.2 사이트 최종 점검 (15m)  
- [ ] 모든 페이지 정상 작동 확인
- [ ] 반응형 디자인 테스트 (모바일/데스크톱)
- [ ] SEO 메타태그, sitemap 확인
- [ ] AdSense 플레이스홀더 위치 확인

### 5.3 모니터링 설정 (15m)
- [ ] Google Analytics 연결 (선택사항)
- [ ] Search Console 등록
- [ ] 백업 스크립트 준비

### DoD
- [ ] 사이트에 5-10개 고품질 글 발행됨  
- [ ] 모든 링크/네비게이션 정상 작동
- [ ] AdSense 신청 준비 완료 (콘텐츠 기준 충족)
- [ ] 일일 자동화 파이프라인 가동 중

---

## 🚀 바이브 코딩 팁

### 각 Phase별 집중 포인트
1. **Phase 1**: UI/UX는 나중에, 일단 작동하는 골격 우선
2. **Phase 2**: 프롬프트 품질이 콘텐츠 품질 결정 → 신중하게
3. **Phase 3**: Git 에러 핸들링 중요 → 커밋 실패 시 복구 로직 필수  
4. **Phase 4**: 로깅 없으면 디버깅 지옥 → 상세한 로그 남기기
5. **Phase 5**: 완벽한 글보다 일관성 있는 품질 + 꾸준한 발행

### 시간 관리 전략
- ⏰ **각 Phase마다 타이머 설정**
- 🎯 **DoD 체크리스트 엄격하게 확인**  
- 🔄 **막히면 다음 Phase로 넘어가고 나중에 돌아오기**
- 📝 **중요한 결정은 문서화해서 나중에 기억하기**

### 디버깅 우선순위
1. **API 연결 확인** (OpenAI, GitHub)
2. **파일 권한 확인** (Git 쓰기, 로그 디렉터리)
3. **환경변수 확인** (.env 파일 로딩)
4. **네트워크 확인** (Netlify 빌드 상태)

---

## ✅ 체크포인트

### 2시간 후 확인사항
- [x] 첫 번째 글이 사이트에 정상 발행되었나?
- [x] 에러 없이 전체 파이프라인이 한 번 실행되었나?

### 4시간 후 확인사항  
- [ ] 크론 등록이 완료되어 자동화가 준비되었나?
- [ ] 로그에서 실행 상태를 모니터링할 수 있나?

### 6시간 후 최종 확인
- [ ] 5개 이상의 글이 발행되어 AdSense 신청이 가능한가?
- [ ] 하루 뒤에도 자동으로 새 글이 발행될 예정인가?

**💡 성공 기준**: 개입 없이 48시간 연속으로 매일 새 글이 발행되면 성공!
