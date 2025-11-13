# 공공임대주택 검색 서비스

공공임대주택 공고를 쉽게 검색하고 지도에서 확인할 수 있는 Streamlit 기반 웹 애플리케이션입니다.

## 주요 기능

- **실시간 스트리밍 채팅**: AI 챗봇과 실시간 대화를 통해 원하는 조건의 공공임대주택 공고를 검색
  - 질문 즉시 화면 표시
  - 답변 실시간 스트리밍 출력
  - 세션 기반 대화 이력 관리
- **공고 검색**: 지역, 주택 유형, 가격, 면적 등 다양한 필터로 공고 검색
- **지도 시각화**: Folium 지도를 활용한 공고 위치 확인 및 상세 정보 조회
  - 지역별 공고 수 표시
  - 줌 레벨에 따른 마커 자동 전환
  - 개별 공고 상세 정보 패널

## 설치 방법

### 1. 필수 패키지 설치

```bash
pip install streamlit streamlit-folium folium requests python-dotenv
```

### 2. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하세요:

```bash
cp .env.example .env
```

`.env` 파일을 열어 본인의 카카오 API 키를 입력하세요:

```env
KAKAO_API_KEY=your_kakao_api_key_here
BACKEND_API_URL=http://localhost:8000
```

카카오 API 키는 [Kakao Developers](https://developers.kakao.com/)에서 발급받을 수 있습니다.

## 실행 방법

### 1. 백엔드 API 서버 실행

먼저 채팅 API 서버를 실행해야 합니다. 별도의 터미널에서:

```bash
# 백엔드 서버 실행 (포트 8000)
# 예: uvicorn main:app --reload --port 8000
```

백엔드 서버가 `http://localhost:8000`에서 실행되어야 하며, 다음 엔드포인트를 제공해야 합니다:
- `POST /chat/stream`: SSE 스트리밍 채팅 응답

### 2. Streamlit 프론트엔드 실행

새로운 터미널에서 다음 명령어를 실행하세요:

```bash
streamlit run homepage.py
```

실행 후 브라우저에서 자동으로 열리며, 기본 주소는 `http://localhost:8501`입니다.

> **주의**: 채팅 기능을 사용하려면 백엔드 API 서버가 먼저 실행되어 있어야 합니다.

## 프로젝트 구조

```
.
├── homepage.py      # 메인 애플리케이션 파일
│   ├── 채팅 페이지 (실시간 스트리밍 채팅)
│   └── 공고 검색 페이지 (지도 + 필터 검색)
├── logo.png         # 로고 이미지
├── .env             # 환경 변수 (git에 포함되지 않음)
├── .env.example     # 환경 변수 예시 파일
├── .gitignore       # Git 제외 파일 목록
└── README.md        # 프로젝트 설명서
```

## API 스펙

### POST /chat/stream

**요청:**
```json
{
  "content": "서울 행복주택 찾아줘",
  "session_id": "user_12345678"
}
```

**응답 (SSE 스트리밍):**
```
data: {"type": "sources", "data": [...], "session_id": "user_12345678"}

data: {"type": "content", "data": "안녕하세요", "session_id": "user_12345678"}

data: {"type": "content", "data": "!", "session_id": "user_12345678"}

data: {"type": "done", "session_id": "user_12345678"}

data: [DONE]
```

## 사용 방법

### 채팅 페이지
1. 좌측 사이드바에서 "채팅" 메뉴 선택
2. 채팅창에 원하는 조건 입력 (예: "서울 행복주택 보증금 2000만원 이하")
3. 질문이 즉시 화면에 표시되고, "💭 답변 생성 중..." 메시지 확인
4. AI 답변이 실시간으로 스트리밍되며 화면에 표시됨
5. 대화 이력이 세션에 저장되어 연속 대화 가능

### 공고 검색 페이지
1. 좌측 사이드바에서 "공고 검색" 메뉴 선택
2. 검색창에 키워드 입력 또는 필터 버튼으로 조건 설정
   - 지역: 서울, 경기, 부산, 대구 등
   - 주택 유형: 행복주택, 청년주택, 공공임대 등
   - 가격 범위: 슬라이더로 보증금 범위 설정
   - 주택 면적: 슬라이더로 면적 범위 설정
3. 검색 결과 리스트에서 원하는 공고 클릭
4. 지도에서 위치 확인 및 상세 정보 조회

## 기술 스택

- **Streamlit**: 웹 애플리케이션 프레임워크
- **Folium**: 지도 시각화 라이브러리
- **Kakao Maps API**: 주소 좌표 변환 (Geocoding)
- **SSE (Server-Sent Events)**: 실시간 스트리밍 채팅
- **Python Requests**: HTTP 통신 및 스트리밍 처리
- **Python**: 백엔드 로직

## 주의사항

- **환경 변수 설정 필수**: `.env` 파일을 생성하고 API 키를 설정해야 합니다
- **백엔드 API 서버**가 실행 중이어야 채팅 기능이 작동합니다
  - 기본 주소: `http://localhost:8000` (`.env`에서 변경 가능)
  - `/chat/stream` 엔드포인트가 SSE 형식으로 응답해야 합니다
  - 응답 형식: `data: {"type": "content", "data": "텍스트", "session_id": "..."}`
- 카카오 API 키가 없으면 지도에 마커가 표시되지 않을 수 있습니다
- 이미지 파일(`logo.png`)이 프로젝트 루트 디렉토리에 있어야 합니다
- 인터넷 연결이 필요합니다 (지도 및 API 호출)
- **보안**: `.env` 파일은 절대 Git에 커밋하지 마세요 (`.gitignore`에 포함됨)

## 문제 해결

### 채팅 응답이 "서버에 연결할 수 없습니다" 오류
백엔드 API 서버가 실행 중인지 확인하세요:
```bash
# 스트리밍 엔드포인트 테스트
curl -N http://localhost:8000/chat/stream \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"content":"안녕","session_id":"test"}'
```

### 스트리밍 응답이 표시되지 않는 경우
- 백엔드가 SSE 형식으로 응답하는지 확인
- 응답 형식: `data: {"type": "content", "data": "텍스트"}`
- 스트림 종료 신호: `data: {"type": "done"}` 또는 `data: [DONE]`

### 포트가 이미 사용 중인 경우
```bash
streamlit run homepage.py --server.port 8502
```

### 브라우저가 자동으로 열리지 않는 경우
터미널에 표시된 URL을 직접 브라우저에 입력하세요.

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.
