# 📘 README.md — 집착(Jibchack)  
공공임대 검색 통합 플랫폼
<img src="logo.png" width="220">

---

## 🏠 프로젝트 개요

**집착(Jibchack)**은 공공임대 정보를 직관적으로 탐색할 수 있는  
**Streamlit 기반 웹 애플리케이션**입니다.

- 좌측 사이드바에서  
  ✔ **채팅(Chat)** – 공공임대 관련 질문에 AI가 답변  
  ✔ **공고 검색(Search)** – 지도 기반 공공임대 공고 조회  
  를 자유롭게 전환할 수 있습니다.

- 백엔드 API와 연동되어  
  ✔ 대화 스트리밍  
  ✔ 공고 데이터 fetch  
  ✔ 지도 표시용 좌표 기반 렌더링  
  을 제공합니다.
---

## ✨ 주요 기능 (Features)

### 🔍 **1. 채팅 기반 공고 추천**
- Streamlit Chat UI 기반
- 사용자의 질문(지역/예산/조건)에 맞는 공고 정보 출력
- 추후 LLM 연결 가능 구조

### 🗺️ **2. 지도 기반 공고 시각화**
- Folium + Leaflet 기반 인터랙티브 지도
- 지역별 공고 수를 **클러스터형 박스 아이콘**으로 표시
- 박스를 클릭하면 해당 지역으로 지도 이동 및 개별 공고 활성화

### 📌 **3. 개별 공고 상세 패널**
- 클릭 시 우측 패널에 상세 정보 표시  
  (공급대상, 임대조건, 일정, 단지 정보 등)
- '공고 원문보기' 버튼 포함

### 🔎 **4. 공고 검색/필터**
- 지역 필터, 유형 필터(행복주택/청년/공공임대 등)
- 가격 범위 슬라이더
- 면적 필터
- 페이지네이션 적용

---

## 🛠️ 기술 스택 (Tech Stack)

- **Frontend**: Streamlit, HTML/CSS Custom Styling  
- **Map**: Folium, Leaflet.js  
- **API**: Kakao Local API (주소 → 좌표 변환)  
- **Language**: Python 3.x  

---
---

## 📂 프로젝트 구조

project/
├── .streamlit/ # Streamlit 환경 설정
├── pages/ # Streamlit 페이지 구성
│ ├── chat_page.py # 채팅 UI 및 AI 스트리밍 처리
│ └── search_page.py # 공공임대 필터 + 지도 검색 페이지
├── api.py # 백엔드 API 호출 래퍼
├── app.py # 앱 엔트리포인트 (사이드바 + 라우팅)
├── config.py # 환경 변수, 옵션 상수 설정
├── homepage.py # (구버전 또는 예비 UI)
├── styles.py # 전체 CSS 관리
├── utils.py # HTML 변환, formatting, 지역 처리 함수
├── logo.png # 프로젝트 로고
└── README.md # 설명 문서

## 🔧 주요 구성 요소 설명

### ■ 1. `app.py` – 메인 엔트리포인트  
✔ 페이지 설정  
✔ 사이드바 구성  
✔ Query Parameter 기반 라우팅 (`?page=home`, `?page=search`)  
✔ CSS 로딩  
✔ 해당 페이지 렌더링 호출  

### ■ 2. `pages/chat_page.py` – 채팅 페이지  
✔ Streamlit session_state 기반 메시지 관리  
✔ AI 백엔드와의 스트리밍 통신(`/chat/stream`)  
✔ 사용자/AI 말풍선 형태 UI 렌더링  
✔ 로딩 상태 처리 및 자동 rerun  

### ■ 3. `pages/search_page.py` – 검색 + 지도 페이지  
✔ 검색 필터 (지역/기관/주택유형/가격/면적)  
✔ 전체 공고 데이터 로딩 후 프론트 단 필터링  
✔ folium 지도 렌더링  
✔ 줌 레벨 변화에 따른  
   - 지역 마커  
   - 개별 공고 마커  
  토글 표시  
✔ 페이지네이션 구현  
✔ 마커 클릭 시 우측 상세 패널 표시  

### ■ 4. `styles.py` – 전체 CSS 스타일  
✔ Streamlit 기본 UI 요소 숨김  
✔ 커스텀 사이드바 스타일  
✔ 검색 페이지 전용 스타일  
✔ 상세 패널 스타일  
✔ 반응형 레이아웃 일부 지원  

### ■ 5. `api.py`  
✔ 백엔드로 HTTP 요청을 보내는 래퍼  
✔ `fetch_all_listings()` 등 데이터 호출 기능 제공  

### ■ 6. `config.py`  
✔ 지역 좌표  
✔ 선택 옵션 리스트 (지역/기관/유형 등)  
✔ 페이지네이션 상수  
✔ 백엔드 URL  

### ■ 7. `utils.py`  
✔ 공고 HTML 변환 함수  
✔ 임대료 formatting  
✔ 주소에서 지역 추출  
✔ 지도 라벨 처리  

---

## 🎮 작동 방식(Flow)

### 1. 앱 시작
`streamlit run app.py` 실행 → Streamlit이 UI 생성

### 2. 현재 페이지 결정
URL Query Parameter 읽기  
→ `"home"` 또는 `"search"`

### 3. 사이드바 클릭 시 페이지 이동
버튼 클릭 → Query Parameter 변경 → `st.rerun()`

### 4. 채팅 페이지
입력 → session_state에 저장 →  
백엔드로 스트리밍 요청 →  
문자 단위로 응답 표시

### 5. 검색 페이지
1) 공고 데이터 fetch  
2) 필터 적용  
3) 리스트 + 지도 렌더링  
4) 좌측 리스트 클릭하면 우측 상세 패널 표시  
5) 지도 줌에 따라 마커 자동 전환  

---

## ▶ 실행 방법

### **1. 설치**
```bash
pip install -r requirements.txt
```

### **2. 실행**
```bash
streamlit run app.py
```

### **3. 접속**
```
http://localhost:8501/
```

---

## 🔌 백엔드 API 개요

### 채팅 API
```bash
POST /chat/stream
```

### 공고 리스트 API
```bash
GET /listings
```
