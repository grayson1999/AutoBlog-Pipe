# AutoBlog-Pipe 구현 태스크 가이드

> 6시간 내 완성을 위한 단계별 구현 가이드

## 🎯 전체 로드맵

```
Phase 0: 스캐폴딩 (30-40m) ✅ 완료
Phase 1: 사이트 골격 & 배포 (40-50m) ✅ 완료  
Phase 2: 콘텐츠 생성기 (60-80m) ✅ 완료
Phase 3: 발행 자동화 (40-50m) ✅ 완료  
Phase 4: 스케줄링 & 로깅 (30-40m) 🚧 다음 단계
Phase 5: 초기 콘텐츠 & 런칭 (40-50m) ⏳ 대기
```

**🔥 신규 로드맵: 지속가능한 콘텐츠 파이프라인 구축**
```
Phase 2.5: Content Idea Collector (아이디어 수집)
    ↓
Phase 2.6: Content Research Engine (리서치/검증)
    ↓
Phase 2.7: Content Deduplication (중복 체크)
    ↓
Phase 2.8: Enhanced Content Generation (콘텐츠 생성)
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
# 블로그 글 1개 자동 생성 & 발행
python app/main.py --mode once

# 블로그 글 5-10개 일괄 생성 (AdSense용)
python app/main.py --mode seed

# 테스트 모드 (실제 발행 안함)
python app/main.py --mode once --dry-run
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

### Phase 2.5: Content Idea Collector (30분)

**목표**: 외부 소스에서 트렌디한 주제를 자동으로 수집하고 필터링합니다.

- [ ] `app/collectors/idea_collector.py` 클래스 생성
- [ ] **Google Trends 연동**: `pytrends` 라이브러리 활용, 실시간 트렌드 수집 기능 구현
- [ ] **RSS Feeds 수집**: `feedparser` 라이브러리 활용, 여러 기술/뉴스 블로그 피드 파싱
- [ ] (Optional) Reddit, Hacker News API 연동
- [ ] **아이디어 스코어링**: 트렌드 지수, 검색량, 관련성을 기반으로 아이디어 점수화
- [ ] **필터링 및 중복 제거**: 기존 주제와 중복되거나 관련 없는 아이디어 제거

### Phase 2.6: Content Research Engine (45분)

**목표**: 선정된 주제에 대해 깊이 있는 정보를 자동으로 리서치하고 검증합니다.

- [ ] `app/research/content_researcher.py` 클래스 생성
- [ ] **Wikipedia API 연동**: `wikipedia` 라이브러리 활용, 주제의 핵심 정보 및 요약 수집
- [ ] **News API 연동**: `newsapi-python` 등 활용, 최신 뉴스 및 동향 수집
- [ ] (Optional) 웹 스크래핑: `BeautifulSoup`, `requests` 활용, 특정 사이트에서 통계/인용문 수집
- [ ] **팩트 체크 및 검증**:
  - [ ] 여러 소스 정보 교차 확인
  - [ ] 정보의 최신성 검증 (e.g., 6개월 이내 정보 우선)
  - [ ] 신뢰도 점수 계산 로직

### Phase 2.7: Content Deduplication (30분)

**목표**: 발행될 콘텐츠가 기존 콘텐츠와 중복되지 않도록 방지합니다.

- [ ] `app/utils/content_deduplicator.py` 클래스 생성
- [ ] **기존 발행 글 로드**: `site/_posts` 디렉터리에서 모든 글의 제목과 메타데이터 로드
- [ ] **유사도 체크**: `scikit-learn` 또는 `difflib` 활용, 신규 주제와 기존 글 제목 간의 유사도 측정 (e.g., 70% 이상 시 중복 간주)
- [ ] **카테고리별 발행 주기 체크**: 동일 카테고리 글이 너무 짧은 기간 내에 발행되지 않도록 제어 (e.g., 7일 이내 발행 이력 체크)

### Phase 2.8: Enhanced Content Generation (30분)

**목표**: 리서치된 데이터를 활용하여 더 풍부하고 정확한 콘텐츠를 생성합니다.

- [ ] `app/generators/content_gen.py` 개선
  - [ ] `generate_post_with_research` 함수 추가
  - [ ] **동적 프롬프트 생성**: 리서치 데이터(핵심 정보, 통계, 뉴스 등)를 프롬프트 템플릿에 동적으로 주입
- [ ] **품질 검증 시스템**:
  - [ ] 생성된 콘텐츠가 리서치 데이터와 사실관계가 일치하는지 확인
  - [ ] 원본 소스 인용 또는 링크가 적절히 포함되었는지 확인

---
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

### DoD  
- [x] `python app/main.py --mode once` 실행 성공
- [x] 새 글이 `site/_posts/`에 올바른 Jekyll 형식으로 생성
- [x] Git 커밋 및 GitHub 원격 푸시 자동화
- [x] Netlify 자동 빌드 트리거 확인
- [x] 완전한 Front Matter + SEO 메타데이터 포함
- [x] 실제 AI 블로그 글 발행 성공 확인
- [x] 에러 처리 및 상태 추적 시스템



## Phase 4: 스케줄링 & 로깅 🚧 다음 단계 (30-40m)

### 4.1 로깅 시스템 (15m)
- [ ] `app/utils/logger.py`
  - [ ] 파일 로깅 설정 (`logs/autoblog.log`)
  - [ ] 성공/실패/경고 레벨 구분
  - [ ] 로그 로테이션 설정

### 4.2 크론 설정 자동화 (10m)
- [ ] `make cron-install` 구현 완성
- [ ] 크론 작업 등록 스크립트
- [ ] 시간대 설정 (TIMEZONE 환경변수)

### 4.3 예외 처리 강화 (15m)
- [ ] API 한도 초과 시 처리
- [ ] 네트워크 장애 시 재시도
- [ ] 빌드 실패 시 알림/복구

### DoD
- [ ] `make cron-install` 실행 → 크론탭에 작업 등록됨
- [ ] 로그 파일에서 실행 히스토리 확인 가능
- [ ] 일일 자동 실행 시뮬레이션 성공

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
