import streamlit as st
from streamlit_folium import st_folium
import folium
import base64
import os
from folium import Element
import time
import requests

KAKAO_API_KEY = "102d0b0b719c47186ef3afa94f03e00d"  # 예: "46c0a0f1e9f1a0...."
def kakao_geocode(address: str):
    """카카오 주소검색으로 lat, lon 반환"""
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    res = requests.get(url, headers=headers, params=params, timeout=5)
    if res.status_code == 200:
        data = res.json()
        docs = data.get("documents")
        if docs:
            lat = float(docs[0]["y"])  # 위도
            lon = float(docs[0]["x"])  # 경도
            return lat, lon
    return None, None

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
    st.markdown("""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        height: 70px;              /* 사각형 높이 */
        background: linear-gradient(to bottom, #ffffff 60%, rgba(255,255,255,0) 100%);
        width: 100%;
        margin-bottom: 10px;       /* 아래 컨텐츠랑 살짝 띄우기 */
        z-index: 9999;
    "></div>
    """, unsafe_allow_html=True)
    # (채팅 페이지 로직 유지)
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요😊 당신의 집 요청 집착이에요! 🧚‍♀️<br> 원하시는 공공임대 공고를 ‘착’하고 불러와드릴게요 🏡<br>지역 / 예산 / 주택유형 아무거나 적어보세요 💬"}
        ]

    # Chat Input은 리스트 출력 전에 위치해야 합니다.
    if query := st.chat_input("질문을 입력하세요."):
        st.session_state.messages.append({"role": "user", "content": query})
        # 여기에 실제 LLM 로직이 들어갈 예정입니다.
        response = f"안녕하세요! 집집이예요 🏠  \n보증금 2,000만원 이하의 행복주택 공고를 찾아드릴게요.  \n\n현재 모집 중인 **2025년 2차 청년안심주택(공공임대)** 공고에서 청년계층을 대상으로 **시세 30~50% 수준의 임대조건**을 제공하는 주택이 있습니다.  \n행복주택과 유사한 공공임대주택으로, 보증금 2,000만원 이하 조건에 부합하는 단지가 있을 수 있어요.  \n\n### 추천 공고 정보  \n**✅ 2025년 2차 청년안심주택(공공임대)**  \n- **대상**: 만 19~39세 무주택 청년  \n- **임대조건**: 시중 시세의 30~50% (순위에 따라 차등 적용)  \n- **보증금 예시**:  \n  - 시세 1억원 주택 → 보증금 약 **3,000~5,000만원** (단, 일부 단지는 보증금 지원 혜택 적용 가능)  \n- **신청기간**: 2025.08.11 ~ 08.13  \n- **입주예정**: 2026.01.30 ~ 03.03  \n\n### 보증금 2,000만원 이하 주택 찾기 팁  \n1. **지역별 주거안심종합센터**에 문의하시면 보증금 지원 프로그램(예: 청년전용 임대보증금 대출)을 안내받을 수 있어요.  \n   - 예: 강남센터 (02-2086-9800), 마포센터 (02-380-0100) 등  \n2. **행복주택**의 경우, 보증금 조건은 단지별로 상이하므로 [SH공사 홈페이지](https://www.i-sh.co.kr)에서 \"행복주택\"으로 검색해보세요.  \n\n### 추가 안내  \n- 현재 공고에는 정확한 보증금 금액이 명시되지 않았으나, **청년안심주택은 시세 대비 30~50% 할인**되므로 저렴한 단지를 찾을 수 있을 거예요.  \n- 신청 전 반드시 **공고문의 \"임대조건\" 항목**을 확인하시거나, 해당 지역 센터에 문의해 주세요!  \n\n📋 **출처**: 2025년 2차 청년안심주택 입주자 모집공고 (2025-07-30)  \n\n더 자세한 조건이 있으시면 언제든 알려주세요! 😊"
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 메시지 표시
    for i, message in enumerate(st.session_state.messages):
        margin_top = "0px" if i == 0 else "10px"
        if message['role'] == 'user':
            st.markdown(
                f"""
                <div style="display:flex; justify-content:flex-end; margin-top:{margin_top}; margin-bottom:20px;">
                    <div style="
                        background-color:#D0F0C0;
                        padding:20px;
                        border-radius:15px;
                        max-width:60%;
                        word-wrap:break-word;
                    ">
                        {message['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="display:flex; justify-content:flex-start; margin-top:{margin_top}; margin-bottom:20px;">
                    <div style="
                        background-color:#F0F0F0;
                        padding:20px;
                        border-radius:15px;
                        max-width:60%;
                        word-wrap:break-word;
                    ">
                        {message['content']}
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
    .detail-panel {
        position: fixed;
        top: 90px;
        right: 40px;
        width: 380px;
        max-height: 78vh;
        background: #ffffff;
        border-radius: 18px;
        box-shadow: 0 6px 24px rgba(15,23,42,0.12);
        padding: 0;
        overflow-y: auto;
        z-index: 9999;
        border: 1px solid rgba(15,23,42,0.03);
    }
    .detail-header {
        padding: 16px 20px 12px 20px;
        border-bottom: 1px solid #edf1f3;
    }
    .detail-badge {
        display: inline-block;
        background: #E6F7EF;
        color: #11835E;
        padding: 3px 10px 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        margin-bottom: 10px;
    }
    .detail-title {
        font-size: 18px;
        font-weight: 700;
        line-height: 1.4;
        margin-bottom: 4px;
    }
    .detail-sub {
        font-size: 13px;
        color: #6b7280;
    }
    .detail-meta {
        display: flex;
        gap: 10px;
        font-size: 11.5px;
        color: #94a3b8;
        margin-top: 8px;
    }
    .detail-tabs {
        display: flex;
        gap: 0;
        border-bottom: 1px solid #edf1f3;
        margin-top: 6px;
    }
    .detail-tab {
        flex: 1;
        text-align: center;
        padding: 10px 0;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        background: #fff;
    }
    .detail-tab.active {
        color: #0f766e;
        border-bottom: 2px solid #0f766e;
    }
    .detail-body {
        padding: 16px 20px 18px 20px;
    }
    .section-title {
        font-weight: 600;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .section-box {
        background: #f8fafc;
        border: 1px solid rgba(15,23,42,0.02);
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 12px;
        font-size: 13px;
    }
    .section-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        font-size: 13px;
    }
    .section-label {
        color: #64748b;
    }
    .section-value {
        font-weight: 500;
    }
    .detail-footer {
        position: sticky;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #10B981;
        color: #ffffff;
        text-align: center;
        font-weight: 600;
        font-size: 15px;
        padding: 14px 0;
        border-top: 1px solid rgba(0,0,0,0.05);
        border-bottom-left-radius: 18px;
        border-bottom-right-radius: 18px;
        cursor: pointer;
        transition: background 0.2s ease-in-out;
    }
    .detail-footer:hover {
        background: #0f9c74;
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
        if "selected_listing" not in st.session_state: st.session_state.selected_listing = None
        if "detail_tab" not in st.session_state:
            st.session_state.detail_tab = "content"
        if "last_map_click" not in st.session_state:
            st.session_state.last_map_click = None
        if "selected_region" not in st.session_state:
            st.session_state.selected_region = None
        if "allowDetailMarkers" not in st.session_state:
            st.session_state.allowDetailMarkers = False

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

        listings = [
            {"name": "서울 강남구 역삼 행복주택", "location": "서울특별시 강남구 테헤란로 201 (역삼동)", "deposit": "보증금 2000만원 / 월 35만원", "area": "36.7㎡"},
            {"name": "서울 마포구 상암 청년전세임대", "location": "서울특별시 마포구 월드컵북로 400 (상암동)", "deposit": "보증금 1000만원 / 월 18만원", "area": "29.8㎡"},
            {"name": "서울 노원구 공릉 국민임대", "location": "서울특별시 노원구 동일로 138길 42 (공릉동)", "deposit": "보증금 1500만원 / 월 22만원", "area": "34.2㎡"},
            {"name": "서울 송파구 가락 행복주택", "location": "서울특별시 송파구 중대로 140 (가락동)", "deposit": "보증금 2500만원 / 월 28만원", "area": "33.5㎡"},
            {"name": "서울 관악구 봉천 청년매입임대", "location": "서울특별시 관악구 봉천로 227 (봉천동)", "deposit": "보증금 800만원 / 월 20만원", "area": "26.9㎡"},
            {"name": "경기 수원시 권선 국민임대", "location": "경기도 수원시 권선구 권선로 308 (권선동)", "deposit": "보증금 1200만원 / 월 19만원", "area": "31.4㎡"},
            {"name": "경기 고양시 덕양 행복주택", "location": "경기도 고양시 덕양구 행주로 50 (행주동)", "deposit": "보증금 2000만원 / 월 24만원", "area": "30.5㎡"},
            {"name": "경기 성남시 수정 국민임대", "location": "경기도 성남시 수정구 수정로 123 (신흥동)", "deposit": "보증금 1800만원 / 월 26만원", "area": "33.1㎡"},
            {"name": "경기 안양시 동안 행복주택", "location": "경기도 안양시 동안구 관악대로 312 (호계동)", "deposit": "보증금 1500만원 / 월 21만원", "area": "28.9㎡"},
            {"name": "부산 해운대구 국민임대", "location": "부산광역시 해운대구 해운대로 620 (좌동)", "deposit": "보증금 1600만원 / 월 25만원", "area": "32.4㎡"},
            {"name": "부산 사하구 행복주택", "location": "부산광역시 사하구 낙동대로 290 (당리동)", "deposit": "보증금 1400만원 / 월 22만원", "area": "30.7㎡"},
            {"name": "부산 동래구 청년임대", "location": "부산광역시 동래구 중앙대로 1267 (온천동)", "deposit": "보증금 900만원 / 월 18만원", "area": "29.0㎡"},
            {"name": "부산 북구 국민임대", "location": "부산광역시 북구 금곡대로 202 (금곡동)", "deposit": "보증금 1700만원 / 월 24만원", "area": "31.2㎡"},
            {"name": "부산 수영구 행복주택", "location": "부산광역시 수영구 광안해변로 150 (광안동)", "deposit": "보증금 2000만원 / 월 27만원", "area": "33.3㎡"},
            {"name": "대구 수성구 행복주택", "location": "대구광역시 수성구 달구벌대로 2480 (범어동)", "deposit": "보증금 1500만원 / 월 23만원", "area": "30.2㎡"},
            {"name": "대구 달서구 국민임대", "location": "대구광역시 달서구 월배로 250 (상인동)", "deposit": "보증금 1200만원 / 월 19만원", "area": "29.5㎡"},
            {"name": "대구 북구 청년임대", "location": "대구광역시 북구 칠곡중앙대로 180 (구암동)", "deposit": "보증금 800만원 / 월 17만원", "area": "28.1㎡"},
            {"name": "대구 동구 행복주택", "location": "대구광역시 동구 아양로 75 (신암동)", "deposit": "보증금 1300만원 / 월 21만원", "area": "31.0㎡"},
            {"name": "대구 중구 매입임대", "location": "대구광역시 중구 달성로 136 (대신동)", "deposit": "보증금 900만원 / 월 18만원", "area": "28.7㎡"},
            {"name": "인천 서구 검단 행복주택", "location": "인천광역시 서구 불로로 160 (불로동)", "deposit": "보증금 2000만원 / 월 25만원", "area": "32.8㎡"},
            {"name": "인천 남동구 청년전세임대", "location": "인천광역시 남동구 인주대로 620 (구월동)", "deposit": "보증금 1000만원 / 월 16만원", "area": "29.2㎡"},
            {"name": "인천 부평구 국민임대", "location": "인천광역시 부평구 경원대로 1120 (십정동)", "deposit": "보증금 1800만원 / 월 23만원", "area": "31.6㎡"},
            {"name": "인천 중구 행복주택", "location": "인천광역시 중구 제물량로 250 (신흥동)", "deposit": "보증금 1500만원 / 월 20만원", "area": "30.4㎡"},
            {"name": "광주 북구 행복주택", "location": "광주광역시 북구 하서로 120 (매곡동)", "deposit": "보증금 1300만원 / 월 22만원", "area": "31.1㎡"},
            {"name": "광주 남구 국민임대", "location": "광주광역시 남구 서문대로 105 (진월동)", "deposit": "보증금 1100만원 / 월 19만원", "area": "30.3㎡"},
            {"name": "광주 서구 청년임대", "location": "광주광역시 서구 상무대로 950 (화정동)", "deposit": "보증금 900만원 / 월 17만원", "area": "28.4㎡"},
            {"name": "광주 동구 행복주택", "location": "광주광역시 동구 중앙로 180 (대인동)", "deposit": "보증금 1200만원 / 월 20만원", "area": "29.8㎡"},
            {"name": "광주 광산구 국민임대", "location": "광주광역시 광산구 하남대로 280 (신가동)", "deposit": "보증금 1400만원 / 월 23만원", "area": "32.0㎡"},
            {"name": "대전 서구 행복주택", "location": "대전광역시 서구 둔산로 102 (둔산동)", "deposit": "보증금 1800만원 / 월 24만원", "area": "31.8㎡"},
            {"name": "대전 유성구 국민임대", "location": "대전광역시 유성구 대학로 91 (궁동)", "deposit": "보증금 1500만원 / 월 21만원", "area": "30.5㎡"},
            {"name": "대전 동구 청년임대", "location": "대전광역시 동구 동서대로 1650 (용전동)", "deposit": "보증금 1000만원 / 월 18만원", "area": "28.7㎡"},
            {"name": "대전 중구 행복주택", "location": "대전광역시 중구 중앙로 130 (문화동)", "deposit": "보증금 1300만원 / 월 20만원", "area": "30.1㎡"},
            {"name": "대전 대덕구 국민임대", "location": "대전광역시 대덕구 한밭대로 1098 (오정동)", "deposit": "보증금 1200만원 / 월 19만원", "area": "29.4㎡"},
            {"name": "세종시 아름 행복주택", "location": "세종특별자치시 한누리대로 312 (어진동)", "deposit": "보증금 2000만원 / 월 26만원", "area": "32.6㎡"},
            {"name": "강원 춘천시 국민임대", "location": "강원특별자치도 춘천시 공지로 250 (효자동)", "deposit": "보증금 1100만원 / 월 18만원", "area": "29.9㎡"},
            {"name": "강원 원주시 행복주택", "location": "강원특별자치도 원주시 시청로 50 (무실동)", "deposit": "보증금 1500만원 / 월 21만원", "area": "31.7㎡"},
            {"name": "강원 강릉시 청년임대", "location": "강원특별자치도 강릉시 강릉대로 230 (교동)", "deposit": "보증금 800만원 / 월 17만원", "area": "28.6㎡"},
            {"name": "제주 제주시 국민임대", "location": "제주특별자치도 제주시 중앙로 210 (이도이동)", "deposit": "보증금 1600만원 / 월 23만원", "area": "30.9㎡"},
            {"name": "제주 서귀포시 행복주택", "location": "제주특별자치도 서귀포시 중앙로 70 (서귀동)", "deposit": "보증금 1400만원 / 월 21만원", "area": "30.2㎡"},
            {"name": "울산 남구 국민임대", "location": "울산광역시 남구 삼산로 200 (삼산동)", "deposit": "보증금 1300만원 / 월 20만원", "area": "30.0㎡"},
            {"name": "울산 북구 행복주택", "location": "울산광역시 북구 산업로 1200 (화봉동)", "deposit": "보증금 1100만원 / 월 19만원", "area": "29.3㎡"},
            {"name": "충북 청주시 국민임대", "location": "충청북도 청주시 상당구 상당로 150 (남문로)", "deposit": "보증금 1500만원 / 월 22만원", "area": "31.0㎡"},
            {"name": "전북 전주시 행복주택", "location": "전라북도 전주시 완산구 팔달로 250 (중앙동)", "deposit": "보증금 1400만원 / 월 20만원", "area": "30.4㎡"},
            {"name": "경남 창원시 청년임대", "location": "경상남도 창원시 의창구 원이대로 450 (용호동)", "deposit": "보증금 1000만원 / 월 17만원", "area": "29.8㎡"},
            {"name": "경북 포항시 행복주택", "location": "경상북도 포항시 북구 중흥로 100 (두호동)", "deposit": "보증금 1300만원 / 월 20만원", "area": "30.8㎡"},
            {"name": "경북 구미시 국민임대", "location": "경상북도 구미시 송동로 180 (도량동)", "deposit": "보증금 1100만원 / 월 18만원", "area": "29.6㎡"}
        ]
        def kakao_geocode(address: str):
            url = "https://dapi.kakao.com/v2/local/search/address.json"
            headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
            params = {"query": address}
            res = requests.get(url, headers=headers, params=params, timeout=5)

            # 상태코드가 200이 아니면 왜 그런지 보자
            if res.status_code != 200:
                print(f"[ERROR {res.status_code}] {address} -> {res.text}")
                return None, None

            data = res.json()
            docs = data.get("documents", [])
            if not docs:
                print(f"[NO_MATCH] {address}")
                return None, None

            lat = float(docs[0]["y"])
            lon = float(docs[0]["x"])
            return lat, lon
            
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

        st.markdown("""
        <style>
        .listing-btn > button {
            width: 100%;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            padding: 14px 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            cursor: pointer;
        }
        .listing-btn > button:hover {
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.12);
        }
        .listing-text {
            text-align: left;
        }
        .listing-title {
            font-weight: 700;
            margin-bottom: 4px;
        }
        .listing-sub {
            font-size: 13px;
            line-height: 1.3;
        }
        .listing-img {
            width: 78px;
            height: 78px;
            border-radius: 10px;
            object-fit: cover;
        }
        </style>
        """, unsafe_allow_html=True)

        # 2) 공고 리스트 출력
        if "selected_listing" not in st.session_state:
            st.session_state.selected_listing = None

        for idx, item in enumerate(page_items):
            # 이미지 소스 그대로
            image_src = apt_base64_src if apt_base64_src else "https://via.placeholder.com/80x80?text=No+Img"

            # 버튼으로 만들기
            with st.container():
                clicked = st.button(
                    # 버튼 안에 들어갈 텍스트는 한 줄짜리여야 해서, 아래에서 바로 HTML로 한 번 더 감싸줄 거야
                    " ",  # 내용은 비워둘게
                    key=f"listing_{idx}",
                    type="secondary",
                    use_container_width=True
                )
                # 버튼 위에 우리가 원하는 모양을 올린다
                st.markdown(f"""
                <div style="
                    position:relative;
                    top:-62px;
                    pointer-events:none;
                    width:100%;                 /* ✅ 전체 폭 채우기 */
                    box-sizing:border-box;      /* ✅ padding 줘도 안 줄어들게 */
                    background:#F8F9FA;
                    border-radius:16px;
                    box-shadow:0 4px 12px rgba(15,23,42,0.08);
                    padding:14px 16px;          /* ✅ 안쪽 여백 */
                    margin-bottom:-45px;
                ">                    
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
                        <div class="listing-text">
                            <div class="listing-title">{item['name']}</div>
                            <div class="listing-sub">📍 {item['location']}</div>
                            <div class="listing-sub">💰 {item['deposit']}</div>
                        </div>
                        <img src="{image_src}" class="listing-img">
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # 버튼이 위아래로 좀 높아졌으니 간격 보정

            if clicked:
                st.session_state.selected_listing = item

        # 페이지네이션 버튼 (유지)
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
                st.session_state.selected_listing = None
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
                        st.session_state.selected_listing = None
        with cols[-1]:
            if st.button("▶", key="next_page_btn") and st.session_state.page_num < total_pages:
                st.session_state.page_num += 1
                st.session_state.selected_listing = None
                
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
                if (typeof map !== 'undefined') {{
                    // 그 위치로 줌
                    map.flyTo([{lat}, {lon}], 13);
                }}

                // 개별 공고 말풍선 보이게
                document.querySelectorAll('.individual-listing-marker').forEach(function(el) {{
                    el.style.display = 'block';
                    el.style.opacity = '1';
                }});

                // 이 지역박스는 클릭하면 잠깐 숨김
                this.style.display = 'none';
            """

            css_style = f"""
                <div class="region-marker" onclick="{js_action}" style="
                    width: 60px;
                    height: 70px;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    cursor: pointer;
                    position: relative;
                    z-index: {count + 100};
                ">
                    <div style="
                        background-color: {header_bg_color};
                        color: white;
                        font-weight: bold;
                        padding: 4px 0;
                        text-align: center;
                        font-size: 12px;
                    ">{region_name}</div>
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
        for item in listings:
            loc = item["location"]
            if "서울" in loc: region_counts["서울"] += 1
            elif "경기" in loc: region_counts["경기"] += 1
            elif "인천" in loc: region_counts["인천"] += 1
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
        for region_name, count in sorted(region_counts.items(), key=lambda x: x[1]):
            if region_name in region_coords:
                lat, lon = region_coords[region_name]
                region_icon = create_custom_icon(region_name, count, lat, lon) 
                folium.Marker(
                    location=[lat, lon],
                    icon=region_icon,
                    z_index_offset=count*1000
                ).add_to(m)
                
        for item in listings:
            # 1) 리스트에 이미 lat/lon이 들어있으면 그걸 쓰고
            lat = item.get("lat")
            lon = item.get("lon")

            # 2) 없으면 주소로 카카오 호출해서 채워넣기
            if not lat or not lon:
                addr = item.get("location")
                if not addr:
                    continue
                lat, lon = kakao_geocode(addr)  # ⬅️ 위쪽에 이미 정의해둔 함수 그대로 사용
                if not lat or not lon:
                    # 이 공고는 좌표가 안 나왔으니까 그냥 건너뛴다
                    continue
                # 성공했으면 item에 저장해두면 다음 rerun 때 또 안 부름
                item["lat"] = lat
                item["lon"] = lon
                time.sleep(0.25)  # 카카오가 너무 빠르게 많이 부르면 429 나올 수 있어서 살짝 쉬기

            # 3) 이제 지도에 찍기
            popup_html = f"""
            <div class="individual-listing-marker" style="
                position: relative;
                display: inline-block;
                background: #fff;
                backdrop-filter: blur(2px);
                color: #333;
                border: 1.3px solid #000;                  
                border-radius: 6px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.25, 0.88);
                font-family: 'Pretendard', 'Malgun Gothic', sans-serif;
                font-size: 12px;
                line-height: 1.4;
                text-align: center;
                overflow: hidden;
                width: 95px;
                opacity: 0.6;
            ">
                <!-- 상단 검정 헤더 -->
                <div style="
                    background: rgba(0,0,0);
                    color: #fff;
                    font-weight: 700;
                    padding: 3px 0 4px 0;
                    font-size: 12px;
                ">
                    {'국민 LH'}
                </div>

                <!-- 흰색 본체 -->
                <div style="padding: 5px 6px 6px 6px;">
                    <div style="font-weight: 500;">{item.get('area', '—')}</div>
                    <div style="color: #000; font-weight: 600;">
                        {item.get('deposit', '—')}
                    </div>
                </div>

                <!-- 꼬리 -->
                <div style="
                    position: absolute;
                    bottom: -6px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 0;
                    height: 0;
                    border-left: 6px solid transparent;
                    border-right: 6px solid transparent;
                    border-top: 6px solid #fff;
                "></div>
            </div>
            """
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=popup_html)
            ).add_to(m)

        # folium 내부 JS 삽입을 위한 클래스 정의
        from folium import MacroElement
        from jinja2 import Template

        class ToggleMarkers(MacroElement):
            _template = Template("""
            {% macro script(this, kwargs) %}
            // folium이 실제로 만든 지도 객체 이름을 가져옴
            var map = {{ this._parent.get_name() }};

            function applyZoomVisibility() {
                var zoom = map.getZoom();
                var regionMarkers = document.querySelectorAll('.region-marker');
                var detailMarkers = document.querySelectorAll('.individual-listing-marker');

                if (zoom >= 12) {
                    regionMarkers.forEach(el => el.style.display = 'none');
                    detailMarkers.forEach(el => el.style.display = 'block');
                } else {
                    regionMarkers.forEach(el => el.style.display = 'block');
                    detailMarkers.forEach(el => el.style.display = 'none');
                }
            }

            // 처음 로드됐을 때 한 번
            map.whenReady(function() {
                applyZoomVisibility();

                // 여기서 region-marker 들에 클릭이벤트를 붙인다
                document.querySelectorAll('.region-marker').forEach(function(el) {
                    el.addEventListener('click', function() {
                        var lat = parseFloat(el.getAttribute('data-lat'));
                        var lon = parseFloat(el.getAttribute('data-lon'));

                        // 지도 이동
                        map.flyTo([lat, lon], 13);

                        // 개별 공고 보이게
                        document.querySelectorAll('.individual-listing-marker').forEach(function(d) {
                            d.style.display = 'block';
                            d.style.opacity = '1';
                        });

                        // 이 지역마커는 숨겨도 되고
                        // el.style.display = 'none';
                    });
                });
            });

            // 줌 바뀔 때마다 표시 전환
            map.on('zoomend', applyZoomVisibility);
            {% endmacro %}
            """)

        # ✅ folium 지도에 위 JS 추가
        m.get_root().add_child(ToggleMarkers())

        map_event = st_folium(m, width="100%", height=845)
        new_click = None
        if map_event:
            new_click = map_event.get("last_clicked")  # {'lat': ..., 'lng': ...} 형태

        # 3) '새로운' 지도 클릭이면 → 패널 닫고, 클릭값 저장하고 rerun
        if new_click and new_click != st.session_state.last_map_click:
            st.session_state.last_map_click = new_click
            st.session_state.selected_listing = None
            st.rerun()
        selected = st.session_state.selected_listing
        if selected:
            공고일 = "25.11.07"
            접수일 = "25.11.25 ~ 25.11.27"
            조회수 = "193"
            공급대상 = "무주택 청년, 대학생(청년), 신혼부부 등"
            공급지역 = selected["location"]
            모집단지 = "1개 단지 (총 모집호수 93)"

            st.markdown(f"""
            <div class="detail-panel">
                <div class="detail-header">
                    <div class="detail-badge">{selected.get('type', '공공임대')}</div>
                    <div class="detail-title">{selected['name']}</div>
                    <div class="detail-sub">{selected['location']}</div>
                    <div class="detail-meta">
                        <div>공고일 {공고일}</div>
                        <div>접수일 {접수일}</div>
                        <div>조회 {조회수}</div>
                    </div>
                </div>
                <div class="detail-body">
                    <div class="section-title">공급대상 및 임대조건</div>
                    <div class="section-box">
                        <div class="section-row">
                            <span class="section-label">공급대상</span>
                            <span class="section-value">{공급대상}</span>
                        </div>
                        <div class="section-row">
                            <span class="section-label">공급지역</span>
                            <span class="section-value">{공급지역}</span>
                        </div>
                        <div class="section-row">
                            <span class="section-label">임대조건</span>
                            <span class="section-value">{selected['deposit']}</span>
                        </div>
                    </div>
                    <div class="section-title" style="margin-top:14px;">모집단지</div>
                    <div class="section-box">
                        <div class="section-row">
                            <span class="section-label">모집단지</span>
                            <span class="section-value">{모집단지}</span>
                        </div>
                        <div style="margin-top:6px; font-size:12.5px; color:#0f766e; cursor:pointer;">
                            단지 상세보기 &rsaquo;
                        </div>
                    </div>
                    <div class="section-title" style="margin-top:14px;">공급일정</div>
                    <div class="section-box" style="padding:0;">
                        <div style="display:flex; border-bottom:1px solid #e2e8f0;">
                            <div style="width:45%; background:#f8fafc; padding:9px 10px; font-size:12.5px;">접수기간</div>
                            <div style="flex:1; padding:9px 10px; font-size:12.5px;">2025.11.24 ~ 2025.11.28</div>
                        </div>
                        <div style="display:flex; border-bottom:1px solid #e2e8f0;">
                            <div style="width:45%; background:#f8fafc; padding:9px 10px; font-size:12.5px;">서류제출대상자 발표일</div>
                            <div style="flex:1; padding:9px 10px; font-size:12.5px;">2025.12.12</div>
                        </div>
                        <div style="display:flex; border-bottom:1px solid #e2e8f0;">
                            <div style="width:45%; background:#f8fafc; padding:9px 10px; font-size:12.5px;">서류접수기간</div>
                            <div style="flex:1; padding:9px 10px; font-size:12.5px;">2025.12.15 ~ 2025.12.19</div>
                        </div>
                        <div style="display:flex; border-bottom:1px solid #e2e8f0;">
                            <div style="width:45%; background:#f8fafc; padding:9px 10px; font-size:12.5px;">당첨자발표일</div>
                            <div style="flex:1; padding:9px 10px; font-size:12.5px;">2026.04.17</div>
                        </div>
                        <div style="display:flex;">
                            <div style="width:45%; background:#f8fafc; padding:9px 10px; font-size:12.5px;">계약기간</div>
                            <div style="flex:1; padding:9px 10px; font-size:12.5px;">2026.05.12 ~ 2026.05.14</div>
                        </div>
                    </div>
                    <div class="section-title" style="margin-top:14px;">문의</div>
                    <div class="section-box">
                        LH / SH 고객센터<br>
                        접수 전 공고문 원문을 반드시 확인하세요.
                    </div>
                </div>
                  <a href="https://www.i-sh.co.kr/main/lay2/program/S1T294C295/www.jbdc.co.kr" 
                    target="_blank" style="text-decoration:none;">
                    <div class="detail-footer">공고 원문보기</div>
                </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
st.markdown('</div>', unsafe_allow_html=True)