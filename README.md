# 🏡 공공임대 지도 탐색 서비스 (집착이에요!)

Streamlit + Folium 기반의 **전국 공공임대 공고 지도 탐색 서비스**입니다.  
사용자는 채팅 인터페이스 또는 지도 기반 UI를 통해  
지역별 공고 수 확인, 상세 공고 조회, 검색/필터링 등을 직관적으로 수행할 수 있습니다.

<img src="logo.png" width="220">

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

## 📦 설치 및 실행

### 1. 저장소 클론  
```sh
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
