# AutoBlog-Pipe 🤖✍️

> **AI가 글을 쓰고, 자동화가 발행하고, 수익은 뒤따라오게 하자.**

완전히 자동화된 AI 블로그 파이프라인 - RSS 기반 트렌드 수집부터 연구, 중복 방지, 콘텐츠 생성, 발행까지

## 🎯 핵심 아이디어

매일/격일로 **주제 선택 → GPT로 글(마크다운) 생성 → 저장소 커밋/푸시 → 호스팅 자동 배포**
- 수익화: **Google AdSense** + **제휴 링크** 중심
- 서버 제약 고려: 모델 추론은 **외부 API**(OpenAI) 사용

## 🚀 빠른 시작

```bash
# 1. 저장소 클론 및 환경 설정
git clone <your-repo-url>
cd AutoBlog-Pipe

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에 OpenAI API 키, News API 키 등 입력

# 4. 🆕 동적 콘텐츠 생성 (추천)
python app/main.py --mode dynamic

# 5. 기존 방식 (topics.yml 기반)
python app/main.py --mode once

# 6. 테스트 모드 (실제 발행 안함)
python app/main.py --mode dynamic --dry-run
```

## 📋 주요 기능

### 🆕 동적 콘텐츠 파이프라인 (완성!)
- **🔍 트렌드 아이디어 자동 수집**: 6개 주요 RSS 피드에서 실시간 기술 뉴스 수집
- **📚 자동 리서치**: Wikipedia + News API를 활용한 심층 정보 조사
- **🚫 중복 방지**: 기존 발행 글과 70% 이상 유사한 제목 자동 스킵
- **🏷️ 스마트 태그 추출**: 제목과 콘텐츠에서 기술 키워드 자동 추출

### 기존 핵심 기능
- **🤖 AI 콘텐츠 생성**: OpenAI GPT-4o-mini로 연구 기반 고품질 글 생성
- **📤 자동 발행**: Git 커밋/푸시 → Netlify 자동 배포
- **🔍 SEO 최적화**: 메타 태그, 슬러그, 키워드 자동 생성
- **💰 수익화 준비**: AdSense 플레이스홀더 내장, 제휴 링크 지원
- **⏰ 스케줄링**: cron을 통한 일일 자동 발행

## 🏗️ 아키텍처

### 기존: 정적 `topics.yml` 기반 파이프라인

```
[Topic Queue] → [Content Generator] → [SEO Meta Builder]
        ↓                         ↓
     (YAML)                   (Markdown)
                                 ↓
                         [Repo Writer] → git push → GitHub
                                                ↓
                                     Netlify CI Build & Deploy
                                                ↓
                                          Public Website + AdSense
```

### 🆕 동적 리서치 기반 파이프라인 (완성!)

완전 자동화된 지속가능한 콘텐츠 생성 시스템입니다.

```
[RSS Feeds] → [Idea Collector] → [Content Researcher] → [Deduplicator] → [Enhanced Generator]
     ↓              ↓                      ↓                    ↓                ↓
(6 Tech Feeds) (Trend Scoring)    (Wikipedia + News)    (70% Similarity)   (Research Post)
                                                                              ↓
                                                                     [Repo Writer] → GitHub → Netlify
```

**실제 작동 확인된 RSS 소스:**
- TechCrunch, Wired, The Verge, Ars Technica, Engadget, O'Reilly


## 📁 프로젝트 구조

```
AutoBlog-Pipe/
├── app/
│   ├── main.py              # CLI 엔트리포인트 (동적 파이프라인 통합)
│   ├── config.py            # 환경설정 관리
│   ├── topics/
│   │   └── topics.yml       # 레거시 주제 큐
│   ├── collectors/          # 🆕 아이디어 수집
│   │   └── idea_collector.py
│   ├── research/            # 🆕 콘텐츠 리서치
│   │   └── content_researcher.py
│   ├── utils/               # 🆕 유틸리티
│   │   ├── content_deduplicator.py
│   │   └── topic_loader.py
│   ├── generators/
│   │   ├── content_gen.py   # AI 콘텐츠 생성 (리서치 기반 강화)
│   │   └── seo_gen.py       # SEO 메타 생성
│   ├── prompts/             # AI 프롬프트 템플릿
│   │   ├── post_researched.txt  # 🆕 리서치 기반 프롬프트
│   │   └── ...
│   └── publishers/
│       └── repo_writer.py   # Git 커밋/푸시 (태그 지원 강화)
├── site/                    # Jekyll 정적 사이트
│   ├── _config.yml
│   ├── _layouts/
│   ├── _posts/              # 생성된 글들 (완벽한 Front Matter)
│   └── pages/
├── docs/
│   └── tasks.md            # 구현 진행 상황
├── requirements.txt
└── .env.example
```

## 🎯 니치 선택 예시

- **AI/테크 뉴스 요약**: 일일 트렌드 요약, 해외 뉴스 번역
- **How-to/코딩 팁**: 개발 팁, 튜토리얼, 문제 해결법
- **생산성 도구 리뷰**: 앱 리뷰, 업무 효율성 팁
- **트렌드 분석**: 소셜미디어 트렌드, 마케팅 인사이트

## 💰 수익화 전략

### Phase 1: AdSense 기반
- 콘텐츠 10-15개 누적 후 AdSense 신청
- 레이아웃에 광고 플레이스홀더 사전 배치
- 클릭당 소액이지만 발행 빈도로 누적 수익

### Phase 2: 제휴 마케팅
- 제품/서비스 추천 글에 제휴 링크 삽입
- 아마존, 쿠팡 등 제휴 프로그램 활용

### Phase 3: 확장
- 성과 있는 니치 복제 (멀티 사이트)
- YouTube 쇼츠 자동 생성
- 뉴스레터 자동 발송

## 📈 6시간 구축 로드맵

| 시간 | 단계 | 작업 내용 |
|------|------|-----------|
| 0-1h | 환경 설정 | GitHub 리포, Netlify 연결, API 키 설정 |
| 1-3h | 코어 개발 | 생성기, 퍼블리셔 구현, 1회 발행 성공 |
| 3-4h | 사이트 구성 | 레이아웃, 페이지, 메타데이터 정리 |
| 4-5h | 자동화 | cron 등록, 로깅, 예외 처리 |
| 5-6h | 런칭 | 초기 5-10개 글 일괄 생성, 검수 |

## 🔧 사용법

### 🆕 동적 콘텐츠 생성 (추천)
```bash
# 하나의 트렌드 기반 글 자동 생성 및 발행
python app/main.py --mode dynamic

# 여러 개 글 생성 (중복은 자동 스킵)
python app/main.py --mode dynamic --count 3

# 테스트 모드 (실제 발행 안함)
python app/main.py --mode dynamic --dry-run
```

### 기존 방식 (topics.yml 기반)
```bash
# 일회성 실행
python app/main.py --mode once

# 초기 시드 생성 (5-10개)
python app/main.py --mode seed

# 테스트 모드
python app/main.py --mode once --dry-run
```

### 크론 등록 (자동화)
```bash
make cron-install
```

## 📚 문서

- [기능 명세서](docs/features.md)
- [구현 태스크](docs/tasks.md)
- [API 문서](docs/api.md)

## 📊 실제 성과

### 2025-08-10 시스템 완성 및 테스트
```bash
✅ 동적 파이프라인 100% 작동 확인
✅ 실제 발행된 포스트:
   - "RIP, Microsoft Lens, a simple little app that's getting replaced by AI" 
   - "The next big AI model is here"
✅ 완벽한 Jekyll Front Matter (제목, 태그, 카테고리, 날짜)  
✅ Git 자동 커밋 및 GitHub 푸시
✅ 중복 방지 시스템 작동 (70% 유사도로 자동 스킵)
```

### 시스템 검증 완료
- **RSS 피드 수집**: 50+ 아이디어 자동 수집 성공
- **리서치 품질**: Wikipedia + News API 연동으로 정확한 정보 기반 글 생성
- **태그 추출**: 콘텐츠에서 자동으로 관련 태그 추출 및 Front Matter 삽입
- **발행 자동화**: Git 커밋부터 Netlify 배포까지 완전 자동화

## 🚦 주의사항

- **콘텐츠 품질**: AI 생성 글은 1차 검토 후 발행 권장
- **저작권**: 요약 시 출처 명시, 원본 내용 직접 복사 금지
- **API 비용**: OpenAI 사용량 모니터링, 일일 한도 설정
- **SEO**: 키워드 스터핑 금지, 자연스러운 문맥 유지

## 🛠️ 기술 스택

- **Runtime**: Python 3.11+
- **AI API**: OpenAI GPT-4o-mini
- **콘텐츠 소스**: RSS Feeds, Wikipedia API, News API
- **중복 검사**: difflib (70% 유사도 임계값)
- **호스팅**: GitHub + Netlify
- **정적 생성**: Jekyll (Front Matter 완벽 지원)
- **스케줄링**: cron
- **주요 라이브러리**: `feedparser`, `wikipedia`, `newsapi-python`, `unidecode`

## 📄 라이선스

MIT License - 상업적 이용 가능

## 🤝 기여하기

이슈 제보, 기능 제안, PR 환영합니다!

---

**💡 팁**: 처음에는 하루 1개씩 안정적으로 발행하며 품질을 확인한 후, 점진적으로 빈도를 늘려가세요.