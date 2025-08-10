# AutoBlog-Pipe 🤖✍️

> **AI가 글을 쓰고, 자동화가 발행하고, 수익은 뒤따라오게 하자.**

저사양 개인 서버(RAM 4GB)에서 6시간 이내 구축 가능한 AI 자동 블로그 파이프라인

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
# .env 파일에 API 키와 설정값 입력

# 4. 한 번 실행해보기
python app/main.py --mode once

# 5. 초기 시드 콘텐츠 생성 (5-10개)
python app/main.py --mode seed
```

## 📋 주요 기능

- **AI 콘텐츠 생성**: OpenAI GPT를 활용한 고품질 블로그 글 자동 생성
- **자동 발행**: Git 커밋/푸시 → Netlify 자동 배포
- **SEO 최적화**: 메타 태그, 슬러그, 키워드 자동 생성
- **수익화 준비**: AdSense 플레이스홀더 내장, 제휴 링크 지원
- **스케줄링**: cron을 통한 일일 자동 발행
- **반응형 디자인**: 모바일 친화적 Jekyll 테마

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

### 신규: 동적 리서치 기반 파이프라인

`topics.yml`의 한계를 넘어, 외부 소스에서 아이디어를 얻고, 리서치를 통해 깊이를 더하며, 중복을 방지하여 지속가능한 콘텐츠를 생성합니다.

```
[Idea Collector] → [Content Researcher] → [Content Deduplicator] → [Enhanced Generator]
      ↓                      ↓                        ↓                       ↓
(Trends, RSS)       (Wikipedia, News)         (Similarity Check)       (Research-based Post)
                                                                          ↓
                                                                   [Repo Writer] → ...
```


## 📁 프로젝트 구조

```
AutoBlog-Pipe/
├── app/
│   ├── main.py              # CLI 엔트리포인트
│   ├── config.py            # 환경설정 관리
│   ├── topics/
│   │   └── topics.yml       # 주제 큐
│   ├── generators/
│   │   ├── content_gen.py   # AI 콘텐츠 생성
│   │   └── seo_gen.py       # SEO 메타 생성
│   └── publishers/
│       └── repo_writer.py   # Git 커밋/푸시
├── site/                    # Jekyll 정적 사이트
│   ├── _config.yml
│   ├── _layouts/
│   ├── _posts/              # 생성된 글들
│   └── pages/               # 고정 페이지
├── docs/                    # 문서화
├── requirements.txt
├── Makefile
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

### 일회성 실행
```bash
make run-once
# 또는
python app/main.py --mode once
```

### 초기 시드 생성
```bash
make run-seed
# 또는
python app/main.py --mode seed
```

### 크론 등록
```bash
make cron-install
```

### 의존성 확인
```bash
make check
```

## 📚 문서

- [기능 명세서](docs/features.md)
- [구현 태스크](docs/tasks.md)
- [API 문서](docs/api.md)

## 🚦 주의사항

- **콘텐츠 품질**: AI 생성 글은 1차 검토 후 발행 권장
- **저작권**: 요약 시 출처 명시, 원본 내용 직접 복사 금지
- **API 비용**: OpenAI 사용량 모니터링, 일일 한도 설정
- **SEO**: 키워드 스터핑 금지, 자연스러운 문맥 유지

## 🛠️ 기술 스택

- **Runtime**: Python 3.11+
- **AI API**: OpenAI GPT-3.5/4
- **호스팅**: GitHub + Netlify
- **정적 생성**: Jekyll
- **스케줄링**: cron
- **로깅**: 파일 로그 + Netlify 빌드 로그

## 📄 라이선스

MIT License - 상업적 이용 가능

## 🤝 기여하기

이슈 제보, 기능 제안, PR 환영합니다!

---

**💡 팁**: 처음에는 하루 1개씩 안정적으로 발행하며 품질을 확인한 후, 점진적으로 빈도를 늘려가세요.