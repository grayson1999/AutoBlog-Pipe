# AutoBlog-Pipe 지속가능한 콘텐츠 생성 계획

## 🎯 목표
정적 topics.yml 방식에서 벗어나 외부 소스 기반의 지속가능한 콘텐츠 자동 생성

## 🔄 새로운 콘텐츠 파이프라인

```
외부 아이디어 수집 → 리서치 & 검증 → 중복 체크 → 콘텐츠 생성 → 품질 검증 → 발행
```

## 📡 Phase 2.5: Content Idea Collector

### 2.5.1 외부 아이디어 소스 (30분)
```python
# app/collectors/idea_collector.py
class IdeaCollector:
    def collect_trending_topics(self) -> List[Dict]:
        ideas = []
        
        # Google Trends (무료)
        ideas.extend(self.get_google_trends())
        
        # RSS Feeds (tech blogs, news)
        ideas.extend(self.get_rss_feeds([
            'https://feeds.feedburner.com/oreilly/radar',
            'https://www.wired.com/feed/',
            'https://techcrunch.com/feed/',
            'https://www.theverge.com/rss/index.xml'
        ]))
        
        # Reddit API (r/programming, r/technology)
        ideas.extend(self.get_reddit_hot_topics())
        
        # Hacker News API
        ideas.extend(self.get_hackernews_trends())
        
        return self.deduplicate_and_score(ideas)
```

### 2.5.2 아이디어 스코어링 & 필터링 (15분)
- 트렌드 지수, 검색량, 관련성 점수 계산
- 우리 사이트에 맞는 주제만 필터링
- 이미 다룬 주제 제외

## 🔍 Phase 2.6: Content Research Engine

### 2.6.1 자동 리서치 시스템 (45분)
```python
# app/research/content_researcher.py
class ContentResearcher:
    def research_topic(self, topic: str) -> Dict:
        research_data = {
            'topic': topic,
            'key_facts': [],
            'statistics': [],
            'recent_developments': [],
            'expert_quotes': [],
            'related_tools': [],
            'sources': []
        }
        
        # Wikipedia API로 기본 정보
        research_data['key_facts'] = self.get_wikipedia_summary(topic)
        
        # 뉴스 API로 최신 동향
        research_data['recent_developments'] = self.get_news_articles(topic)
        
        # Web scraping으로 통계 수집
        research_data['statistics'] = self.scrape_statistics(topic)
        
        # Product Hunt, GitHub에서 관련 도구
        research_data['related_tools'] = self.get_related_tools(topic)
        
        return research_data
```

### 2.6.2 팩트 체크 & 검증 (15분)
- 여러 소스 간 정보 일치 여부 확인
- 최신성 검증 (6개월 이내 정보 우선)
- 신뢰성 점수 계산

## 🚫 Phase 2.7: Content Deduplication

### 2.7.1 중복 방지 시스템 (30분)
```python
# app/utils/content_deduplicator.py
class ContentDeduplicator:
    def check_duplicates(self, new_topic: str) -> bool:
        # 기존 발행글 제목과 유사도 체크
        published_posts = self.get_published_posts()
        
        for post in published_posts:
            similarity = self.calculate_similarity(new_topic, post['title'])
            if similarity > 0.7:  # 70% 이상 유사하면 중복
                return True
        
        # 카테고리별 발행 주기 체크
        category_posts = self.get_posts_by_category(new_topic)
        if self.published_recently(category_posts, days=7):
            return True
            
        return False
```

## 🔄 Phase 2.8: Enhanced Content Generation

### 2.8.1 리서치 기반 콘텐츠 생성 (30분)
```python
# 기존 content_gen.py 개선
def generate_post_with_research(self, topic: Dict, research_data: Dict) -> str:
    # 리서치 데이터를 프롬프트에 포함
    enhanced_prompt = self.create_enhanced_prompt(
        topic=topic,
        key_facts=research_data['key_facts'],
        statistics=research_data['statistics'],
        recent_news=research_data['recent_developments'],
        tools=research_data['related_tools']
    )
    
    return self.call_openai_api(enhanced_prompt)
```

### 2.8.2 품질 검증 시스템 (15분)
- 팩트 체크 (리서치 데이터와 일치 여부)
- 원본 소스 인용 여부 확인
- 정보의 최신성 검증

## 📊 예상 효과

### 지속가능성
- ♾️ **무한 콘텐츠**: 외부 트렌드 기반으로 끊임없는 아이디어
- 📈 **트렌드 반영**: 실시간 이슈와 검색 트렌드 반영
- 🎯 **타겟팅**: 실제 사용자 관심사 기반 주제 선정

### 품질 향상
- 📚 **풍부한 정보**: 구체적 데이터와 통계 기반 글 작성
- ✅ **팩트 체크**: 여러 소스 검증을 통한 정확성 보장
- 🔗 **신뢰성**: 원본 소스 링크와 인용 포함

### 중복 방지
- 🚫 **제목 중복**: 유사도 기반 중복 주제 필터링
- ⏰ **발행 주기**: 카테고리별 적절한 간격 유지
- 📝 **콘텐츠 다양성**: 다양한 각도와 접근 방식

## 🛠 구현 우선순위

1. **Phase 2.5**: Content Idea Collector (Google Trends + RSS)
2. **Phase 2.7**: 기본 중복 체크 (제목 유사도)
3. **Phase 2.6**: 간단한 리서치 엔진 (Wikipedia + News API)
4. **Phase 2.8**: 리서치 기반 콘텐츠 생성

## 💰 비용 고려사항

### 무료/저비용 APIs
- Google Trends: 무료
- RSS Feeds: 무료
- Reddit API: 무료 (제한적)
- Wikipedia API: 무료
- Hacker News API: 무료

### 유료 APIs (옵션)
- News API: $449/월 (더 많은 소스)
- Twitter API: $100/월 (트렌드 분석)
- Google Search API: $5/1000 쿼리

## 🎯 성공 지표
- 📊 중복 글 0% 달성
- 🔄 월 100개 이상 유니크 주제 생성
- 📈 트렌딩 키워드 70% 이상 반영
- ⭐ 생성 콘텐츠 품질 점수 8.0+ 유지

---

이 계획으로 AutoBlog-Pipe가 진정한 **지속가능한 AI 블로그 생성 시스템**이 될 수 있습니다!