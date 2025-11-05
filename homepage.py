import streamlit as st
from streamlit_folium import st_folium
import folium
import base64
import os

st.set_page_config(page_title="홈 페이지", layout="wide")

# 로고 경로 
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

# 파일 존재 여부 확인 및 인코딩
encoded = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
else:
    st.error(f"로고 파일 경로를 찾을 수 없습니다: {logo_path}")


# --- 세션 상태 초기화 ---
if "page" not in st.session_state:
    st.session_state.page = "home"

page = st.session_state.page

# --- CSS 스타일링 ---
st.markdown(f"""
<style>
div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {{
    justify-content: flex-start !important; 
}}

/* 사이드바의 버튼 자체 스타일 (폰트 크기, 색상 등) */
div[data-testid="stSidebar"] button {{
    display: block;
    width: 100%; /* 버튼이 사이드바 폭을 채우도록 설정 */
    
    margin-left: -30px !important; 
    
    text-align: left !important;
    font-size: 24px;
    font-weight: bold;
    color: #2F4F6F;
    cursor: pointer;
    transform: scale(1.0); /* 크기 변환을 1.1에서 1.0으로 수정하여 자연스럽게 만듭니다. */
    margin-bottom: 15px;
    background-color: transparent !important; /* 기본 배경색 투명화 */
    border: none;
    box-shadow: none;
}}

/* st.sidebar의 기본 패딩을 줄여 메뉴를 더 왼쪽으로 붙입니다. */
section[data-testid="stSidebar"] {{
    padding-left: 5px;
    padding-right: 5px;
    width: 210px !important; /* 너비를 고정합니다. */
}}

/* 홈 버튼 강조 */
div[data-testid="stSidebar"] button:has(div:has(p:contains("채팅"))) {{
    background-color: {"#D8FCE8" if page=="home" else "transparent"} !important;
    border-bottom: {"3px solid #A7E4C2" if page=="home" else "none"} !important;
}}

/* 공고 검색 버튼 강조 */
div[data-testid="stSidebar"] button:has(div:has(p:contains("공고 검색"))) {{
    background-color: {"#D8FCE8" if page=="search" else "transparent"} !important;
    border-bottom: {"3px solid #A7E4C2" if page=="search" else "none"} !important;
}}

/* 오른쪽 콘텐츠 영역 */
.content {{
    margin-left: 220px;
    padding: 20px;
    overflow: hidden;
}}

/* 채팅 영역 */
.chat-box {{
    max-height: 60vh;
    overflow-y: auto;
    margin-bottom: 10px;
}}
.chat-user {{
    background-color: #D0F0C0;
    padding: 20px;
    border-radius: 10px;
    max-width: 60%;
    margin-left: auto;
    margin-bottom: 10px;
}}
.chat-assistant {{
    background-color: #F0F0F0;
    padding: 20px;
    border-radius: 10px;
    max-width: 60%;
    margin-right: auto;
    margin-bottom: 10px;
}}

/* 💡 추가: 검색창과 필터 버튼 주변의 간격 조정 (팝오버 사용을 위해) */
div[data-testid="stTextInput"] {{
    margin-top: -12px;
    margin-bottom: 0px;
}}

/* 💡 추가: 검색 버튼 스타일 조정 */
div[data-testid="stButton"][id="filter_button"]>button {{
    background-color: transparent !important;
    border: 1px solid #ccc !important;
    font-size: 16px !important; /* 폰트 크기 조정 */
    font-weight: bold;
    color: #1f77b4;
    cursor: pointer;
    padding: 4px 8px !important; /* 패딩 조정 */
    margin: 0;
    transform: translateY(-2px); 
    height: 38px; /* 높이 맞춤 */
}}
/* 공고 카드 스타일 */
.listing-card {{
    background-color: #F8F9FA;
    padding: 12px;
    margin-bottom: 25px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}
div[data-testid="stPopover"] div[data-testid="stPopoverBody"],
div[data-testid="stPopoverBody"] {{
    width: 350px !important;
    min-width: 350px !important;
    max-width: 350px !important;
}}

/* 💡 [신규] 검색 입력 필드와 필터 태그를 감싸는 커스텀 컨테이너 스타일 */
.custom-search-container {{
    padding: 8px 10px;
    border: 1px solid #ccc; /* Streamlit 기본 입력 필드와 유사하게 보이도록 테두리 */
    border-radius: 0.5rem; /* Streamlit 기본 입력 필드와 유사하게 보이도록 둥근 모서리 */
    background-color: #f0f2f6; /* Streamlit 기본 입력 필드 배경색 */
    margin-bottom: 0; /* 아래 마진 제거 */
}}
/* 💡 [신규] 검색 입력 필드 자체 스타일 */
.custom-search-container input {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    width: 100%;
    font-size: 16px;
    padding: 0;
    margin-bottom: 8px; /* 태그와의 간격 */
}}
/* 필터 태그 margin-bottom 수정 */
.custom-search-container .filter-tag {{
    margin-bottom: 0 !important;
}}
</style>
""", unsafe_allow_html=True)

# --- 왼쪽 메뉴 (st.sidebar 사용) ---
with st.sidebar:
    # 로고 표시
    if encoded:
        st.markdown(
            f"""
            <a href>
                <img src="data:image/png;base64,{encoded}" width="200", style="margin-top:-40px; margin-bottom:60px;">
            </a>
            """,
            unsafe_allow_html=True
        )
    
    # URL 쿼리 가져오기 (메인 콘텐츠 영역에서도 사용)
    params = st.query_params
    current_page = params.get("page", ["home"])[0] 

    # 버튼 클릭 시 페이지 변경 (query_params 사용)
    if st.button("채팅", key="home_btn", type="primary"):
        st.query_params = {"page": ["home"]}
        st.rerun()
        
    if st.button("공고 검색", key="search_btn", type="secondary"):
        st.query_params = {"page": ["search"]}
        st.rerun()

    st.markdown("""
    <style>
    /* 메뉴 버튼 추가 스타일 유지 */
    button[kind="primary"], button[kind="secondary"] {
        background-color: transparent; 
        border: none;
        box-shadow: none;
        color: #2F4F6F;
        font-size: 20px;
        font-weight: bold;
        border-radius: 0;
        padding: 8px 0;
        text-align: left;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)


# --- 오른쪽 콘텐츠 영역 ---
st.markdown('<div class="content">', unsafe_allow_html=True)

# URL 쿼리 가져오기
params = st.query_params
page = params.get("page", ["home"])[0] 

if page == "home":
    # (채팅 페이지 로직 유지)
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Chat Input은 리스트 출력 전에 위치해야 합니다.
    if query := st.chat_input("질문을 입력하세요."):
        st.session_state.messages.append({"role": "user", "content": query})
        # 여기에 실제 LLM 로직이 들어갈 예정입니다.
        response = f"서울 강남구 지역의 공공임대주택을 찾아드릴게요! 🏠  \n\n현재 모집 중인 강남구 청년안심주택 및 공공임대주택 공고를 확인했어요.  \n\n### 📌 **강남구 추천 공공임대주택**  \n1. **2025년 2차 청년안심주택(강남센터 관할)**  \n   - 📍 **위치**: 서울시 강남구 일원 (세부 단지는 공고문 참조)  \n   - 💰 **임대조건**: 시세 30~50% (순위별 차등)  \n   - 📅 **신청기간**: 2025.08.11 ~ 08.13  \n   - ✅ **대상**: 만 19~39세 무주택 청년  \n   - 📐 **면적**: 20~40㎡ (원룸/투룸)  \n   - 🚗 **주차**: 입주자 필수(장애인·유자녀) 우선, 나눔카 15% 운영  \n\n2. **행복주택 강남역 인근 단지**  \n   - 📍 **위치**: 강남구 역삼동 일대  \n   - 💰 **임대조건**: 시세 60~80%  \n   - 📅 **모집**: 수시 (공고별 상이)  \n   - ✅ **대상**: 청년, 신혼부부, 일반 무주택자  \n\n### 📋 **신청 자격 예시 (청년안심주택 기준)**  \n- **소득 기준**: 도시근로자 월평균소득 70% 이하 (2인 가구 기준 약 434만원)  \n- **자산 기준**: 총자산 2억 4,800만원 이하 (1인 가구)  \n- **기타**: 무주택자, 강남구에 직장/학교 소재 시 가점  \n\n### 📍 **강남센터 연락처**  \n- **주소**: 서울시 강남구 선릉로 615 썬라이더빌딩 4층  \n- **전화**: 02-2086-9800~1  \n\n### 💡 **추천 이유**  \n- 강남구 역세권 접근성과 청년 맞춤형 조건  \n- 반려동물 동반 가능 (단, 관리규약 준수 필수)  \n\n자세한 공고문과 전자팸플릿은 [SH공사 홈페이지](https://www.i-sh.co.kr)에서 확인하실 수 있어요.  \n특정 단지나 조건이 있으시면 추가로 알려주세요! 😊  \n\n📋 **출처**:  \n- 2025년 2차 청년안심주택 입주자 모집공고 (2025-07-30)  \n- SH공사 강남센터 공고 자료"
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 메시지 표시
    for i, message in enumerate(st.session_state.messages):
        margin_top = "50px" if i == 0 else "10px"
        if message['role'] == 'user':
            st.markdown(
                f"""
                <div style="display:flex; justify-content:flex-end; margin-top:{margin_top}; margin-bottom:10px;">
                    <div style="
                        background-color:#D0F0C0;
                        padding:10px;
                        border-radius:10px;
                        max-width:60%;
                        word-wrap:break-word;
                    ">
                        <b>User:</b> {message['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="display:flex; justify-content:flex-start; margin-top:{margin_top}; margin-bottom:10px;">
                    <div style="
                        background-color:#F0F0F0;
                        padding:10px;
                        border-radius:10px;
                        max-width:60%;
                        word-wrap:break-word;
                    ">
                        <b>Assistant:</b> {message['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

elif page == "search":
    # (스타일링 유지)
    st.markdown("""
    <style>
    html, body {
    overflow: hidden !important;
    }
    /* (공고 검색 페이지 전용 스타일 유지) */
    [data-testid="stAppViewContainer"] {
        padding: 0;
        margin: 0;
        overflow: hidden !important;
    }
    .block-container {
        padding: 0;
        margin: 0;
        width: 100%;
    }
    div.st-folium {
        width: 100% !important;
        height: 100vh !important;
        padding: 0;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # 🔸 좌측에 검색 / 우측에 지도 (2:5 비율)
    col_gap, col_search, col_gap2, col_map = st.columns([0.2, 2, 0.1, 5])

    # ---- 왼쪽: 공고 검색 영역 ----
    with col_search:
        st.markdown("""
        <style>
        html, body {
            overflow: hidden !important;
        }
        div.stColumn > div:first-child {
            margin-top: 0px !important; 
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 검색창과 필터 버튼을 위한 컬럼 분할 (유지)
        col_input, col_button = st.columns([4, 1.1])

        # 세션 상태 초기화/로드
        if "search_text" not in st.session_state: st.session_state.search_text = ""
        if "location" not in st.session_state: st.session_state.location = "전체"
        if "house_type" not in st.session_state: st.session_state.house_type = "전체"
        if "price_slider" not in st.session_state: st.session_state.price_slider = (500, 2000)
        if "applied_filters" not in st.session_state: st.session_state.applied_filters = []
        if "applied_price" not in st.session_state: st.session_state.applied_price = None 
        if "area_slider" not in st.session_state: st.session_state.area_slider = (0, 150)   # 주택 면적(㎡)
        if "applied_area" not in st.session_state: st.session_state.applied_area = None

        with col_input:
            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
            # 텍스트 입력 CSS는 전체 스타일 블록에 통합됨
            keyword = st.text_input(
                "나에게 맞는 공고를 찾아보세요!", 
                placeholder="예: 서울 행복주택",
                value=st.session_state.search_text,
                key="search_input"
            )
            st.session_state.search_text = keyword

        # 필터 값이 변경되었을 때만 갱신하는 함수
        def update_applied_filters():
            filters = []
            if st.session_state.location != "전체":
                filters.append(f"지역: {st.session_state.location}")
            if st.session_state.house_type != "전체":
                filters.append(f"유형: {st.session_state.house_type}")
            st.session_state.applied_filters = filters
            # '적용' 버튼을 눌러야 applied_price가 업데이트되므로, 여기서는 price_slider만 건드리지 않음
            
        update_applied_filters()

        # 빨간 필터 표시
        # if st.session_state.applied_filters or st.session_state.applied_price:
        #     filter_html = ""
        #     for filter_name in st.session_state.applied_filters:
        #         filter_html += f"""
        #         <div style='
        #             background-color: #f26f6d; 
        #             color: white; 
        #             padding: 5px 10px; 
        #             border-radius: 5px; 
        #             margin: 0 1px 15px 0; 
        #             display: inline-block; 
        #             font-size: 14px;
        #             font-weight: bold;
        #             white-space: nowrap;
        #         '>{filter_name}</div>
        #         """
        #     if st.session_state.applied_price:
        #         price = st.session_state.applied_price
        #         filter_html += f"""
        #         <div style='
        #             background-color: #f26f6d; 
        #             color: white; 
        #             padding: 5px 10px; 
        #             border-radius: 5px; 
        #             margin: 0 1px 5px 0; 
        #             display: inline-block; 
        #             font-size: 14px;
        #             font-weight: bold;
        #             white-space: nowrap;
        #         '>가격: {price[0]}~{price[1]}만원</div>
        #         """
        #     if filter_html:
        #         st.markdown(filter_html, unsafe_allow_html=True)
    
        with col_button:
            st.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
            
            # 💡 [핵심 수정] st.button 대신 st.popover를 사용하여 필터 UI 오버레이
            filter_popover = st.popover("필터", use_container_width=True)
            
            with filter_popover:
                # 필터 위젯 배치
                location_options = ["전체", "서울", "경기", "부산", "대구"]
                st.selectbox(
                    "지역 선택", 
                    location_options, 
                    key="location",
                    index=location_options.index(st.session_state.location)
                )

                house_types = ["전체", "행복주택", "청년주택", "공공임대"]
                st.selectbox(
                    "주택 유형", 
                    house_types, 
                    key="house_type",
                    index=house_types.index(st.session_state.house_type)
                )

                # 슬라이더는 popover에 넣어도 리스트를 밀어내지 않습니다.
                st.slider(
                    "가격 범위 (만원)", 0, 10000,
                    st.session_state.get("price_slider", (500, 2000)),
                    key="price_slider"
                )
                st.slider(
                    "주택 면적 (㎡)", 0, 200,
                    st.session_state.get("area_slider", (0, 150)),
                    key="area_slider"
                )

                # '적용' 버튼 클릭 시 필터 상태 업데이트 및 리스트 재검색 유도
                if st.button("적용", use_container_width=True):
                    # 가격 필터 적용
                    st.session_state.applied_price = st.session_state.price_slider
                    # 필터 변경 사항을 반영하기 위해 rerun을 사용하거나, 리스트를 업데이트하는 함수를 호출합니다.
                    # 여기서는 간단히 rerun하지 않고, 다음에 리스트를 그릴 때 세션 상태를 사용하도록 합니다.
                    st.toast("필터가 적용되었습니다.")


        # 예시 공고 리스트 (데이터 유지)
        listings = [
            {"name": "서울 강남구 역삼 행복주택", "location": "서울 강남구", "price": "보증금 2000만원 / 월 35만원", "image": "seoul_gangnam_1.jpg"},
            {"name": "서울 마포구 상암 청년전세임대", "location": "서울 마포구", "price": "보증금 1000만원 / 월 18만원", "image": "seoul_mapo_1.jpg"},
            {"name": "서울 노원구 공릉 국민임대", "location": "서울 노원구", "price": "보증금 1500만원 / 월 22만원", "image": "seoul_nowon_1.jpg"},
            {"name": "서울 송파구 가락 행복주택", "location": "서울 송파구", "price": "보증금 2500만원 / 월 28만원", "image": "seoul_songpa_1.jpg"},
            {"name": "서울 관악구 봉천 청년매입임대", "location": "서울 관악구", "price": "보증금 800만원 / 월 20만원", "image": "seoul_gwanak_1.jpg"},
            {"name": "경기 수원시 권선 국민임대", "location": "경기 수원시", "price": "보증금 1200만원 / 월 19만원", "image": "gyeonggi_suwon_1.jpg"},
            {"name": "경기 고양시 덕양 행복주택", "location": "경기 고양시", "price": "보증금 2000만원 / 월 24만원", "image": "gyeonggi_goyang_1.jpg"},
            {"name": "경기 성남시 수정 국민임대", "location": "경기 성남시", "price": "보증금 1800만원 / 월 26만원", "image": "gyeonggi_seongnam_1.jpg"},
            {"name": "경기 안양시 동안 행복주택", "location": "경기 안양시", "price": "보증금 1500만원 / 월 21만원", "image": "gyeonggi_anyang_1.jpg"},
            {"name": "부산 해운대구 국민임대", "location": "부산 해운대구", "price": "보증금 1600만원 / 월 25만원", "image": "busan_haeundae_1.jpg"},
            {"name": "부산 사하구 행복주택", "location": "부산 사하구", "price": "보증금 1400만원 / 월 22만원", "image": "busan_saha_1.jpg"},
            {"name": "부산 동래구 청년임대", "location": "부산 동래구", "price": "보증금 900만원 / 월 18만원", "image": "busan_dongnae_1.jpg"},
            {"name": "부산 북구 국민임대", "location": "부산 북구", "price": "보증금 1700만원 / 월 24만원", "image": "busan_buk_1.jpg"},
            {"name": "부산 수영구 행복주택", "location": "부산 수영구", "price": "보증금 2000만원 / 월 27만원", "image": "busan_suyeong_1.jpg"},
            {"name": "대구 수성구 행복주택", "location": "대구 수성구", "price": "보증금 1500만원 / 월 23만원", "image": "daegu_suseong_1.jpg"},
            {"name": "대구 달서구 국민임대", "location": "대구 달서구", "price": "보증금 1200만원 / 월 19만원", "image": "daegu_dalseo_1.jpg"},
            {"name": "대구 북구 청년임대", "location": "대구 북구", "price": "보증금 800만원 / 월 17만원", "image": "daegu_buk_1.jpg"},
            {"name": "대구 동구 행복주택", "location": "대구 동구", "price": "보증금 1300만원 / 월 21만원", "image": "daegu_dong_1.jpg"},
            {"name": "대구 중구 매입임대", "location": "대구 중구", "price": "보증금 900만원 / 월 18만원", "image": "daegu_jung_1.jpg"},
            {"name": "인천 서구 검단 행복주택", "location": "인천 서구", "price": "보증금 2000만원 / 월 25만원", "image": "incheon_seo_1.jpg"},
            {"name": "인천 남동구 청년전세임대", "location": "인천 남동구", "price": "보증금 1000만원 / 월 16만원", "image": "incheon_namdong_1.jpg"},
            {"name": "인천 부평구 국민임대", "location": "인천 부평구", "price": "보증금 1800만원 / 월 23만원", "image": "incheon_bupyeong_1.jpg"},
            {"name": "인천 중구 행복주택", "location": "인천 중구", "price": "보증금 1500만원 / 월 20만원", "image": "incheon_jung_1.jpg"},
            {"name": "광주 북구 행복주택", "location": "광주 북구", "price": "보증금 1300만원 / 월 22만원", "image": "gwangju_buk_1.jpg"},
            {"name": "광주 남구 국민임대", "location": "광주 남구", "price": "보증금 1100만원 / 월 19만원", "image": "gwangju_nam_1.jpg"},
            {"name": "광주 서구 청년임대", "location": "광주 서구", "price": "보증금 900만원 / 월 17만원", "image": "gwangju_seo_1.jpg"},
            {"name": "광주 동구 행복주택", "location": "광주 동구", "price": "보증금 1200만원 / 월 20만원", "image": "gwangju_dong_1.jpg"},
            {"name": "광주 광산구 국민임대", "location": "광주 광산구", "price": "보증금 1400만원 / 월 23만원", "image": "gwangju_gwangsan_1.jpg"},
            {"name": "대전 서구 행복주택", "location": "대전 서구", "price": "보증금 1800만원 / 월 24만원", "image": "daejeon_seo_1.jpg"},
            {"name": "대전 유성구 국민임대", "location": "대전 유성구", "price": "보증금 1500만원 / 월 21만원", "image": "daejeon_yuseong_1.jpg"},
            {"name": "대전 동구 청년임대", "location": "대전 동구", "price": "보증금 1000만원 / 월 18만원", "image": "daejeon_dong_1.jpg"},
            {"name": "대전 중구 행복주택", "location": "대전 중구", "price": "보증금 1300만원 / 월 20만원", "image": "daejeon_jung_1.jpg"},
            {"name": "대전 대덕구 국민임대", "location": "대전 대덕구", "price": "보증금 1200만원 / 월 19만원", "image": "daejeon_daedeok_1.jpg"},
            {"name": "세종시 아름 행복주택", "location": "세종특별자치시", "price": "보증금 2000만원 / 월 26만원", "image": "sejong_1.jpg"},
            {"name": "강원 춘천시 국민임대", "location": "강원 춘천시", "price": "보증금 1100만원 / 월 18만원", "image": "gangwon_chuncheon_1.jpg"},
            {"name": "강원 원주시 행복주택", "location": "강원 원주시", "price": "보증금 1500만원 / 월 21만원", "image": "gangwon_wonju_1.jpg"},
            {"name": "강원 강릉시 청년임대", "location": "강원 강릉시", "price": "보증금 800만원 / 월 17만원", "image": "gangwon_gangneung_1.jpg"},
            {"name": "제주 제주시 국민임대", "location": "제주 제주시", "price": "보증금 1600만원 / 월 23만원", "image": "jeju_jeju_1.jpg"},
            {"name": "제주 서귀포시 행복주택", "location": "제주 서귀포시", "price": "보증금 1400만원 / 월 21만원", "image": "jeju_seogwipo_1.jpg"},
            {"name": "울산 남구 국민임대", "location": "울산 남구", "price": "보증금 1300만원 / 월 20만원", "image": "ulsan_nam_1.jpg"},
            {"name": "울산 북구 행복주택", "location": "울산 북구", "price": "보증금 1100만원 / 월 19만원", "image": "ulsan_buk_1.jpg"},
            {"name": "충북 청주시 국민임대", "location": "충북 청주시", "price": "보증금 1500만원 / 월 22만원", "image": "chungbuk_cheongju_1.jpg"},
            {"name": "전북 전주시 행복주택", "location": "전북 전주시", "price": "보증금 1400만원 / 월 20만원", "image": "jeonbuk_jeonju_1.jpg"},
            {"name": "경남 창원시 청년임대", "location": "경남 창원시", "price": "보증금 1000만원 / 월 17만원", "image": "gyeongnam_changwon_1.jpg"},
            {"name": "경북 포항시 행복주택", "location": "경북 포항시", "price": "보증금 1300만원 / 월 20만원", "image": "gyeongbuk_pohang_1.jpg"},
            {"name": "경북 구미시 국민임대", "location": "경북 구미시", "price": "보증금 1100만원 / 월 18만원", "image": "gyeongbuk_gumi_1.jpg"}
        ]


        # ---- 페이지네이션 (공고 리스트 아래) ----
        items_per_page = 5  
        if "page_num" not in st.session_state:
            st.session_state.page_num = 1

        # 전체 페이지 계산
        total_pages = len(listings) // items_per_page + (1 if len(listings) % items_per_page else 0)

        # 현재 페이지에 해당하는 공고만 표시
        start = (st.session_state.page_num - 1) * items_per_page
        end = start + items_per_page
        page_items = listings[start:end]
        
        # 이미지 로딩 함수 및 경로 지정 (유지)
        def get_base64_image(image_path):
            if not os.path.exists(image_path):
                # st.error(f"이미지 파일을 찾을 수 없습니다: {image_path}")
                return None
            try:
                with open(image_path, "rb") as f:
                    encoded_string = base64.b64encode(f.read()).decode()
                    return f"data:image/jpeg;base64,{encoded_string}"
            except Exception as e:
                # st.error(f"이미지 인코딩 오류: {e}")
                return None

        apt_image_path = r"C:\Users\박다영\OneDrive\바탕 화면\Upstage AI Ambassador\test_apt.jpg" 
        apt_base64_src = get_base64_image(apt_image_path)
        
        st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

        # 공고 리스트 출력 (유지)
        for item in page_items:
            # 검색 키워드 필터링 (필터 상태는 반영되지 않음)
            if keyword.lower() in item["name"].lower():
                image_src = apt_base64_src if apt_base64_src else "https://via.placeholder.com/80x80?text=No+Img"
                st.markdown(f"""
                <div class="listing-card" style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex-grow: 1;">
                        <b>{item['name']}</b><br>
                        📍 {item['location']}<br>
                        💰 {item['price']}
                    </div>
                    <img src="{image_src}" style="
                        width:80px;
                        height:80px;
                        border-radius:8px;
                        object-fit:cover;
                        margin-left:15px;
                    ">
                </div>
                """, unsafe_allow_html=True)

        # 페이지네이션 버튼 (유지)
        st.markdown('<div style="margin-top:30px;">', unsafe_allow_html=True) 
        max_buttons = 5
        current = st.session_state.page_num

        if total_pages <= max_buttons:
            start_page = 1
            end_page = total_pages
        else:
            start_page = ((current - 1) // max_buttons) * max_buttons + 1
            end_page = min(start_page + max_buttons - 1, total_pages)

        # ... (페이지네이션 버튼 로직 유지)

        cols = st.columns((end_page - start_page + 1) + 2) 
        with cols[0]:
            if st.button("◀", key="prev_page_btn") and st.session_state.page_num > 1:
                st.session_state.page_num -= 1
        for i, page_num in enumerate(range(start_page, end_page+1)):
            with cols[i+1]:
                if page_num == st.session_state.page_num:
                    st.markdown(f"""
                        <button style="
                            background-color:#F0F2F6;
                            color:#2F4F6F;
                            font-weight:bold;
                            border:none; 
                            border-radius:5px;
                            padding:5px 10px;
                            margin:0 3px;
                            width:40px;
                            height:38px;
                            line-height:1; 
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            cursor:default;
                            transform: translateY(1px);
                        ">{page_num}</button>
                    """, unsafe_allow_html=True)
                else:
                    if st.button(str(page_num), key=f"page_btn_{page_num}"):
                        st.session_state.page_num = page_num
        with cols[-1]:
            if st.button("▶", key="next_page_btn") and st.session_state.page_num < total_pages:
                st.session_state.page_num += 1
                
    # ---- 오른쪽: 지도 영역 ----
    with col_map:
        # (지도 로직 유지)
        region_coords = {
            "서울": [37.5665, 126.9780], "경기": [37.4138, 127.5183], "인천": [37.4563, 126.7052], 
            "강원": [37.8228, 128.1555], "충북": [36.6357, 127.4917], "충남": [36.5184, 126.8000], 
            "대전": [36.3504, 127.3845], "세종": [36.4800, 127.2890], "전북": [35.7167, 127.1440], 
            "전남": [34.8161, 126.4633], "광주": [35.1595, 126.8526], "경북": [36.4919, 128.8889], 
            "경남": [35.4606, 128.2132], "부산": [35.1796, 129.0756], "대구": [35.8714, 128.6014], 
            "울산": [35.5384, 129.3114], "제주": [33.4996, 126.5312],
        }

        region_counts = {key: 0 for key in region_coords.keys()}

        for item in listings:
            loc = item["location"]
            if "서울" in loc: region_counts["서울"] += 1
            elif "경기" in loc: region_counts["경기"] += 1
            elif "인천" in loc: region_counts["인천"] += 1
            # ... (나머지 지역 카운팅 로직 유지)
            elif "강원" in loc: region_counts["강원"] += 1
            elif "충북" in loc: region_counts["충북"] += 1
            elif "충남" in loc: region_counts["충남"] += 1
            elif "대전" in loc: region_counts["대전"] += 1
            elif "세종" in loc: region_counts["세종"] += 1
            elif "전북" in loc: region_counts["전북"] += 1
            elif "전남" in loc or "전라남" in loc: region_counts["전남"] += 1
            elif "광주" in loc: region_counts["광주"] += 1
            elif "경북" in loc or ("경상북" in loc): region_counts["경북"] += 1
            elif "경남" in loc or ("경상남" in loc): region_counts["경남"] += 1
            elif "부산" in loc: region_counts["부산"] += 1
            elif "대구" in loc: region_counts["대구"] += 1
            elif "울산" in loc: region_counts["울산"] += 1
            elif "제주" in loc: region_counts["제주"] += 1
            
        # folium 지도 생성
        m = folium.Map(location=[36.5, 127.8], zoom_start=7)

        def create_custom_icon(region_name, count, lat, lon):
            if count == 0:
                header_bg_color = "#1E90FF"
                count_text_color = "#1E90FF"
            else:
                header_bg_color = "#e91e63"
                count_text_color = "#e91e63"

            js_action = f"""
                map.flyTo([{lat}, {lon}], 13); 
                this.style.visibility='hidden'; 
                map.on('zoomend', function() {{
                    if (map.getZoom() < 12) {{
                        document.querySelectorAll('div[onclick]').forEach(el => el.style.visibility='visible');
                    }}
                }});
            """
            css_style = f"""
                <div onclick="{js_action}" style="
                    width: 60px;
                    height: 70px;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    cursor: pointer;
                    position: relative;              /* 추가 */
                    z-index: {count + 100}; 
                ">
                    <div style="
                        background-color: {header_bg_color};
                        color: white;
                        font-weight: bold;
                        padding: 4px 0;
                        text-align: center;
                        font-size: 12px;
                    ">
                        {region_name}
                    </div>
                    <div style="
                        padding: 4px 0;
                        text-align: center;
                        flex-grow: 1;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                    ">
                        <span style="color: #444; font-size: 12px;">공고수</span>
                        <span style="color: {count_text_color}; font-weight: bold; font-size: 14px;">{count}</span>
                    </div>
                </div>
            """
            return folium.DivIcon(
                html=css_style,
                icon_anchor=(30, 70) 
            )
        
        for region_name, count in sorted(region_counts.items(), key=lambda x: x[1]):
            if region_name in region_coords:
                lat, lon = region_coords[region_name]
                region_icon = create_custom_icon(region_name, count, lat, lon) 
                folium.Marker(
                    location=[lat, lon],
                    icon=region_icon,
                    z_index_offset=count*1000
                ).add_to(m)

        st_folium(m, width="100%", height=845)

st.markdown('</div>', unsafe_allow_html=True)