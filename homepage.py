import streamlit as st
from streamlit_folium import st_folium
import folium
import base64
import os
from folium import Element
import time
import requests
from dotenv import load_dotenv
import textwrap

load_dotenv()

KAKAO_API_KEY = "102d0b0b719c47186ef3afa94f03e00d"  # 예: "46c0a0f1e9f1a0...."
CHAT_BACKEND_URL = os.getenv("CHAT_BACKEND_URL", "http://localhost:8000")
HOUSING_API_URL = "http://127.0.0.1:8000"
import re

def extract_short_rent(text):
    """
    '임대기간 ~ 가능'까지만 잘라주는 함수
    """
    if not text:
        return "임대조건 정보 없음"

    # 1) '임대기간'으로 시작하는 문장 찾기
    m = re.search(r"(임대기간[^.]+가능)", text)
    if m:
        return m.group(1).strip()

    # 2) 못 찾으면 첫 40자만
    return text[:40] + "…"
def format_date(date_str: str) -> str:
    """
    '2025-09-30' -> '2025.09.30' 형태로 바꿔줌
    """
    if not date_str:
        return ""
    if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
        return date_str.replace("-", ".")
    return date_str
def extract_region_from_address(addr: str):
    if not addr:
        return None

    addr = addr.strip()

    # 서울
    if addr.startswith("서울"):
        # '서울', '서울특별시', '서울시' 모두 포함
        return "서울"

    # 경기
    if addr.startswith("경기") or addr.startswith("경기도"):
        return "경기"

    # 부산
    if addr.startswith("부산") or addr.startswith("부산광역시"):
        return "부산"

    # 대구
    if addr.startswith("대구") or addr.startswith("대구광역시"):
        return "대구"

    # 필요하면 인천, 광주 등 추가
    return None
def fetch_listings_from_backend(
    skip: int = 0,
    limit: int = 50,
    *,
    location: str | None = None,
    subscription_types: list[str] | None = None,
    min_deposit: int | None = None,
    max_deposit: int | None = None,
    min_rent: int | None = None,
    max_rent: int | None = None,
    min_area: float | None = None,
    max_area: float | None = None,
    unit_types: list[str] | None = None,
):
    try:
        payload = {
            "location": location,                          # None이면 전체
            "subscription_types": subscription_types or [],# []이면 전체
            "min_deposit": min_deposit or 0,              # 0이면 필터 없음으로 처리한다고 가정
            "max_deposit": max_deposit or 0,
            "min_rent": min_rent or 0,
            "max_rent": max_rent or 0,
            "min_area": min_area or 0,
            "max_area": max_area or 0,
            "unit_types": unit_types or [],
            "skip": skip,
            "limit": limit,
            "sort_by": "created_at",
            "sort_order": "desc",
        }

        resp = requests.post(
            f"{HOUSING_API_URL}/api/v1/search",
            json=payload,
            timeout=100,
        )
        resp.raise_for_status()
        data = resp.json()

        raw_listings = []

        for ann in data.get("items", []):
            prog = ann.get("program_info") or {}
            company_type = ann.get("company_type") or ""
            subscription_type = ann.get("subscription_type") or ""
            raw_notice_date = ann.get("published_date") or ann.get("announcement_date") or ""
            notice_date = format_date(raw_notice_date)
            eligibility_summary = (prog.get("eligibility_summary") or "").strip()
            timeline = prog.get("timeline_steps") or []
            application_period = ""
            for step in timeline:
                step_name = step.get("step_name", "")
                if "신청접수" in step_name:
                    application_period = step.get("period", "")
                    break

            financial_summary = (prog.get("financial_terms_summary") or "").strip()
            link = ann.get("link") or ""
            department = ann.get("department") or ""

            # 백엔드 스펙: supply_projects 안에 실제 세대/단지 정보가 들어간다고 가정
            units = prog.get("supply_units") or prog.get("supply_projects") or []

            for u in units:
                deposit_text = (u.get("deposit_and_rent_text") or "").strip()
                depo = u.get("deposit_amount_krw") or 0
                rent = u.get("monthly_rent_krw") or 0
                area_m2 = u.get("exclusive_area_m2")

                if not deposit_text:
                    if depo or rent:
                        depo_txt = f"{depo:,}원" if depo else "0원"
                        rent_txt = f"{rent:,}원" if rent else "0원"
                        deposit_text = f"보증금 {depo_txt} / 월 {rent_txt}"
                    elif financial_summary:
                        deposit_text = financial_summary
                    else:
                        deposit_text = "임대조건: 공고문 참고"

                complex_name = u.get("location_label") or ""
                addr_full = u.get("location_full_address") or ""
                raw_listings.append(
                    {
                        "id": u.get("id") or ann.get("id"),
                        "name": ann.get("title"),
                        "complex": complex_name,
                        "location": u.get("location_full_address") or "",
                        "region": extract_region_from_address(addr_full), 
                        "deposit": deposit_text,
                        "deposit_short": extract_short_rent(deposit_text),
                        "area": (
                            f"{area_m2}㎡"
                            if area_m2
                            else "-"
                        ),
                        "notice_date": notice_date,
                        "application_period": application_period,
                        "company_type": company_type,
                        "subscription_type": subscription_type,
                        "eligibility_summary": eligibility_summary,
                        "timeline_steps": timeline,
                        "link": link,
                        "department": department,

                        # 숫자 필터용 값들도 같이 들고 있기
                        "area_m2": area_m2,
                        "deposit_amount_krw": depo,
                        "monthly_rent_krw": rent,
                    }
                )

        # 🔹 중복 제거 (이름 + 주소 기준)
        dedup = {}
        for item in raw_listings:
            key = (item["name"], item["location"])
            if key in dedup:
                old = dedup[key]
                if (
                    old["deposit"].startswith("임대조건: 공고문 참고")
                    and item["deposit"] != old["deposit"]
                ):
                    dedup[key] = item
            else:
                dedup[key] = item

        listings = list(dedup.values())
        sub_types = sorted({ (item.get("subscription_type") or "") for item in listings })
        companies = sorted({ (item.get("company_type") or "") for item in listings })
        print("[DEBUG] subscription_type 리스트:", sub_types)
        print("[DEBUG] company_type 리스트:", companies)
        print(
            f"[DEBUG] fetched {len(raw_listings)} raw listings "
            f"→ {len(listings)} unique listings from backend"
        )

        return listings

    except Exception as e:
        st.error(f"백엔드에서 공고를 가져오는 중 오류가 발생했습니다: {e}")
        return []

def fetch_map_points_from_backend():
    """
    지도용 좌표를 /api/v1/map/points 에서 가져온다.
    """
    try:
        resp = requests.get(
            f"{HOUSING_API_URL}/api/v1/map/points",
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        points = data.get("points", []) or []

        # 주소 → 포인트 dict 으로 정리해두면 나중에 찾기 편해
        addr_to_point = {}
        for p in points:
            addr = (p.get("location_full_address") or "").strip()
            lat = p.get("latitude")
            lon = p.get("longitude")
            if not addr or lat is None or lon is None:
                continue

            addr_to_point[addr] = {
                "lat": lat,
                "lon": lon,
                "location_label": p.get("location_label"),
                "title": p.get("title"),
                "subscription_type": p.get("subscription_type"),
                "exclusive_area_m2": p.get("exclusive_area_m2"),
                "deposit_amount_krw": p.get("deposit_amount_krw"),
                "monthly_rent_krw": p.get("monthly_rent_krw"),
                "announcement_id": p.get("announcement_id"),
                "id": p.get("id"),
            }

        print(f"[MAP] fetched {len(points)} map points from backend")
        return addr_to_point

    except Exception as e:
        print(f"[MAP] failed to fetch map points: {e}")
        return {}    
def kakao_geocode(address: str):
    """카카오 주소검색으로 lat, lon 반환"""
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        # ✅ 여기서 한 번만 로그 찍고, 앱은 죽지 않도록
        print(f"[KAKAO GEOCODE ERROR] {address}: {e}")
        return None, None

    data = res.json()
    docs = data.get("documents", [])
    if not docs:
        return None, None

    first = docs[0]
    return float(first["y"]), float(first["x"])

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

    # 세션 ID 초기화
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = f"user_{uuid.uuid4().hex[:8]}"
    
    # 로딩 상태 초기화
    if 'is_loading' not in st.session_state:
        st.session_state.is_loading = False
    if 'pending_query' not in st.session_state:
        st.session_state.pending_query = None
    
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

    # API 호출 처리 (로딩 상태일 때만)
    if st.session_state.is_loading and st.session_state.pending_query:
        # 스트리밍 응답을 위한 placeholder
        response_placeholder = st.empty()
        
        try:
            api_url = f"{CHAT_BACKEND_URL}/chat/stream"
            payload = {
                "content": st.session_state.pending_query,
                "session_id": st.session_state.session_id
            }
            
            # 스트리밍 요청
            with requests.post(api_url, json=payload, stream=True, timeout=60) as response:
                if response.status_code == 200:
                    full_response = ""
                    
                    # 스트리밍 데이터 수신
                    for line in response.iter_lines():
                        if line:
                            try:
                                # JSON 파싱
                                line_text = line.decode('utf-8').strip()
                                
                                # SSE 형식: "data: " 접두사 제거
                                if line_text.startswith('data: '):
                                    line_text = line_text[6:]  # "data: " 제거
                                
                                # [DONE] 신호 무시
                                if line_text == '[DONE]':
                                    continue
                                
                                # JSON 객체 파싱
                                data = requests.compat.json.loads(line_text)
                                
                                # type이 "content"인 경우만 처리
                                if data.get('type') == 'content':
                                    chunk = data.get('data', '')
                                    
                                    if chunk:
                                        full_response += chunk
                                        # 실시간으로 화면에 표시
                                        response_placeholder.markdown(
                                            f"""
                                            <div style="display:flex; justify-content:flex-start; margin-top:10px; margin-bottom:20px;">
                                                <div style="
                                                    background-color:#F0F0F0;
                                                    padding:20px;
                                                    border-radius:15px;
                                                    max-width:60%;
                                                    word-wrap:break-word;
                                                ">
                                                    {full_response}
                                                </div>
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )
                            except Exception as e:
                                # 빈 줄이나 파싱 불가능한 줄은 무시
                                continue
                    
                    # 최종 응답 저장
                    assistant_response = full_response if full_response else "응답을 받지 못했습니다."
                else:
                    assistant_response = f"오류가 발생했습니다. (상태 코드: {response.status_code})"
        except requests.exceptions.ConnectionError:
            assistant_response = "⚠️ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요."
        except requests.exceptions.Timeout:
            assistant_response = "⚠️ 요청 시간이 초과되었습니다. 다시 시도해주세요."
        except Exception as e:
            assistant_response = f"⚠️ 오류가 발생했습니다: {str(e)}"
        
        # 로딩 메시지를 실제 응답으로 교체
        st.session_state.messages[-1] = {"role": "assistant", "content": assistant_response}
        st.session_state.is_loading = False
        st.session_state.pending_query = None
        st.rerun()

    # Chat Input
    user_input = st.chat_input("질문을 입력하세요.")
    
    # 사용자 입력 처리
    if user_input:
        # 1. 사용자 메시지를 즉시 추가
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 2. 로딩 메시지 추가
        st.session_state.messages.append({"role": "assistant", "content": "💭 답변 생성 중..."})
        st.session_state.is_loading = True
        st.session_state.pending_query = user_input
        
        # 3. 화면 즉시 갱신
        st.rerun()

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
        if "company_filter" not in st.session_state: st.session_state.company_filter = "전체"
        if "selected_listing" not in st.session_state: st.session_state.selected_listing = None
        if "detail_tab" not in st.session_state:
            st.session_state.detail_tab = "content"
        if "last_map_click" not in st.session_state:
            st.session_state.last_map_click = None
        if "selected_region" not in st.session_state:
            st.session_state.selected_region = None
        if "allowDetailMarkers" not in st.session_state:
            st.session_state.allowDetailMarkers = False
        if "applied_house_type" not in st.session_state: 
            st.session_state.applied_house_type = "전체"
        if "applied_company" not in st.session_state:
            st.session_state.applied_company = "전체"
        if "applied_location" not in st.session_state: 
            st.session_state.applied_location = "전체"
        if "last_search_keyword" not in st.session_state:
            st.session_state.last_search_keyword = ""

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
            if keyword != st.session_state.last_search_keyword:
                st.session_state.last_search_keyword = keyword
                if keyword.strip():
                    st.toast("🔍 검색 중입니다.. 조금만 기다려주세요!")

        # 필터 값이 변경되었을 때만 갱신하는 함수
        def update_applied_filters():
            filters = []
            if st.session_state.location != "전체":
                filters.append(f"지역: {st.session_state.location}")
            if st.session_state.house_type != "전체":
                filters.append(f"유형: {st.session_state.house_type}")
            if st.session_state.company_filter != "전체":
                filters.append(f"공급기관: {st.session_state.company_filter}")
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
                company_options = ["전체", "LH", "SH"]
                st.selectbox(
                    "공급기관", 
                    company_options, 
                    key="company_filter",
                    index=company_options.index(st.session_state.company_filter)
                )
                house_types = ["전체", "도시형생활주택", "매입임대주택"]
                st.selectbox(
                    "주택 유형", 
                    house_types, 
                    key="house_type",
                    index=house_types.index(st.session_state.house_type)
                )

                # 슬라이더는 popover에 넣어도 리스트를 밀어내지 않습니다.
                st.slider(
                    "가격 범위 (만원)", 0, 10000,
                    st.session_state.price_slider,
                    key="price_slider"
                )
                st.slider(
                    "주택 면적 (㎡)", 0, 200,
                    st.session_state.get("area_slider", (0, 150)),
                    key="area_slider"
                )

                # '적용' 버튼 클릭 시 필터 상태 업데이트 및 리스트 재검색 유도
                if st.button("적용", use_container_width=True):
                    st.session_state.applied_price = st.session_state.price_slider
                    st.session_state.applied_area = st.session_state.area_slider

                    # 지역 / 유형 / 공급기관
                    st.session_state.applied_location = st.session_state.location
                    st.session_state.applied_house_type = st.session_state.house_type
                    st.session_state.applied_company = st.session_state.company_filter

                    # 페이지는 1페이지로 리셋
                    st.session_state.page_num = 1

                    st.toast("필터가 적용되었습니다.")
                    st.rerun()
        if "page_num" not in st.session_state:
            st.session_state.page_num = 1

        # ✅ 1) 적용된 필터 값 읽어오기
        applied_location = st.session_state.get("applied_location", "전체")
        applied_house_type = st.session_state.get("applied_house_type", "전체")
        applied_company = st.session_state.get("applied_company", "전체")  # (현재는 프론트에서만 사용 가능)
        applied_price = st.session_state.get("applied_price", None)        # (min, max) 단위: "만원"
        applied_area = st.session_state.get("applied_area", None)          # (min, max) 단위: ㎡

        # ✅ 2) UI → API 파라미터 변환

        # location: "전체" → None (필터 안씀)
        api_location = None if applied_location == "전체" else applied_location

        # subscription_types: 주택 유형 (도시형생활주택 / 매입임대주택)
        subscription_types: list[str] = []
        if applied_house_type != "전체":
            subscription_types = [applied_house_type]

        unit_types: list[str] = []

        if (
            applied_location == "전체"
            and applied_house_type == "전체"
            and applied_company == "전체"
        ):
            api_location = None
            subscription_types = []
            min_rent = 0
            max_rent = 0
            min_area = 0
            max_area = 0

        listings = fetch_listings_from_backend(
            skip=0,
            limit=100,
            location=None,
            subscription_types=subscription_types,
            min_deposit=0,      # 지금은 별도 UI 없으니 0 (필터 없음)
            max_deposit=0,
            min_rent=min_rent,
            max_rent=max_rent,
            min_area=min_area,
            max_area=max_area,
            unit_types=unit_types,
        )

        # ==== 💰 가격 필터 (보증금 기준, 만원 → 원) ====
        applied_price = st.session_state.get("applied_price", None)
        if applied_price:
            min_price, max_price = applied_price  # 예: (500, 2000)  -> 만원 단위
            min_price *= 10000
            max_price *= 10000

            listings = [
                item for item in listings
                if item.get("deposit_amount_krw") is not None
                and min_price <= item["deposit_amount_krw"] <= max_price
            ]

        # ==== 📏 면적 필터 (㎡) ====
        applied_area = st.session_state.get("applied_area", None)
        if applied_area:
            min_area, max_area = applied_area

            listings = [
                item for item in listings
                if item.get("area_m2") is not None
                and min_area <= item["area_m2"] <= max_area
            ]

        applied_location = st.session_state.get("applied_location", "전체")
        if applied_location != "전체":
            listings = [
                item for item in listings
                if item.get("region") == applied_location
            ] 
        # ✅ house type 1:1 필터 (subscription_type 기준)
        applied_house_type = st.session_state.get("applied_house_type", "전체")
        if applied_house_type != "전체":
            listings = [
                item for item in listings
                if item.get("subscription_type") == applied_house_type
            ]

        # ✅ company 1:1 필터 (company_type 기준)
        applied_company = st.session_state.get("applied_company", "전체")
        if applied_company != "전체":
            listings = [
                item for item in listings
                if item.get("company_type") == applied_company
            ]
        keyword = (st.session_state.get("search_text") or "").strip()
        if keyword:
            kw = keyword.lower()
            tokens = [t for t in kw.split() if t]  # '청년', '매입임대주택' 이런 식

            def matches(item):
                text = " ".join([
                    item.get("name", ""),
                    item.get("location", ""),
                    item.get("complex", ""),
                    item.get("subscription_type", ""),
                ]).lower()

                # 모든 토큰이 다 들어 있으면 매칭 (AND 검색)
                return all(tok in text for tok in tokens)

            listings = [item for item in listings if matches(item)]
        # ---- 페이지네이션 (공고 리스트 아래) ----
        items_per_page = 4  
        if "page_num" not in st.session_state:
            st.session_state.page_num = 1

        # 전체 페이지 계산
        total_pages = max(1, (len(listings) + items_per_page - 1) // items_per_page)

        # 현재 페이지 번호를 유효 범위로 보정
        if st.session_state.page_num < 1:
            st.session_state.page_num = 1
        elif st.session_state.page_num > total_pages:
            st.session_state.page_num = total_pages

        current_page = st.session_state.page_num
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
            font-size: 15px;
            line-height: 1.35;

            /* 최대 2줄까지만 보이게 + 나머지는 … 처리 */
            display: -webkit-box;
            -webkit-line-clamp: 2;          /* 2줄까지만 */
            -webkit-box-orient: vertical;
            overflow: hidden;
            word-break: keep-all;   
        }     
        .listing-sub.clamp-1 {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }    
        .complex-pill {
            display: inline-block;
            margin-left: 6px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: 600;
            color: #1d4ed8;              /* 글자색 */
            background: #e0edff;          /* 연한 파란 배경 */
            border-radius: 999px;         /* 동그란 알약 모양 */
            vertical-align: middle;
            white-space: nowrap;
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
            flex-shrink: 0.
        }
        </style>
        """, unsafe_allow_html=True)

        # 2) 공고 리스트 출력
        if "selected_listing" not in st.session_state:
            st.session_state.selected_listing = None

        for idx, item in enumerate(page_items):
            # 이미지 소스 그대로
            image_src = apt_base64_src if apt_base64_src else "https://via.placeholder.com/80x80?text=No+Img"
            complex_html = ""
            if item.get("complex"):
                complex_html = f"<span class='complex-pill'>{item['complex']}</span>"
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
                    margin-bottom:-40px;
                ">                    
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
                        <div class="listing-text" style="flex:1; min-width:0;">
                            <div class="listing-title">{item['name']}{complex_html}</div>
                            <div class="listing-sub"> 📅 공고일&nbsp;{item.get('notice_date', '')}</div>
                            <div class="listing-sub clamp-1">📍 {item['location']}</div>
                            <div class="listing-sub clamp-1">💰 {item.get('deposit_short', item['deposit'])}</div>
                        </div>
                        <img src="{image_src}" class="listing-img">
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # 버튼이 위아래로 좀 높아졌으니 간격 보정

            if clicked:
                st.session_state.selected_listing = item

        # 공고 개수
        num_items = len(page_items)

        # 🔧 0개일 때만 아래로 밀어서 위치 맞춰주기
        if num_items == 0:
            st.markdown(
                """
                <div style="
                    margin-top: 40px;
                    text-align: center;
                    color: #6b7280;
                    font-size: 16px;
                ">
                    🔍 검색된 공고가 없습니다
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            VISIBLE_PAGES = 5
            cols = st.columns(VISIBLE_PAGES + 2)

            # ◀ 이전
            with cols[0]:
                if st.button("◀", key="prev_page_btn"):
                    # 1보다 작아지지 않게만 막기
                    st.session_state.page_num = max(1, st.session_state.page_num - 1)
                    st.session_state.selected_listing = None
                    st.rerun()

            # 1~5 페이지 버튼 (전부 st.button 사용)
            for i, page_num in enumerate(range(1, VISIBLE_PAGES + 1)):
                with cols[i + 1]:
                    # 현재 페이지는 눌러도 아무 일 안 일어나게만 처리
                    if st.button(str(page_num), key=f"page_btn_{page_num}"):
                        st.session_state.page_num = page_num
                        st.session_state.selected_listing = None
                        st.rerun()

            # ▶ 다음
            with cols[-1]:
                if st.button("▶", key="next_page_btn"):
                    # 5보다 커지지 않게만 막기
                    st.session_state.page_num = min(VISIBLE_PAGES, st.session_state.page_num + 1)
                    st.session_state.selected_listing = None
                    st.rerun()
                
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
        
        addr_to_point = fetch_map_points_from_backend()
        for item in listings:
            # 1) 리스트에 이미 lat/lon이 들어있으면 그걸 쓰고
            lat = item.get("lat")
            lon = item.get("lon")

            # 2) 없으면 주소로 카카오 호출해서 채워넣기
            if not lat or not lon:
                addr = item.get("location")
                if not addr:
                    continue
                p = addr_to_point.get(addr)

                if p:
                    lat = p["lat"]
                    lon = p["lon"]
                    item["lat"] = lat
                    item["lon"] = lon               
                
                else:
                    lat, lon = kakao_geocode(addr)
                    if not lat or not lon:
                        continue
                    item["lat"] = lat
                    item["lon"] = lon
                    time.sleep(0.25)
                item["lat"] = lat
                item["lon"] = lon
                time.sleep(0.25)  # 카카오가 너무 빠르게 많이 부르면 429 나올 수 있어서 살짝 쉬기
            agency = (item.get("company_type") or "").strip()          # LH, SH 등
            sub_type = (item.get("subscription_type") or "").strip()   # 행복주택, 장기전세주택 등
            title_text = (item.get("name") or "") + " " + sub_type
            complex_name = item.get("complex") or item.get("name")

            # 🔹 앞에 붙일 한글 키워드 (행복 / 장기 / 청년 등)
            label_prefix = ""
            if "행복주택" in title_text:
                label_prefix = "행복"
            elif "장기전세" in title_text:
                label_prefix = "장기"
            elif "청년" in title_text:
                label_prefix = "청년"
            # 필요하면 여기 조건 더 추가해서 커스터마이즈 가능

            # 🔹 최종 라벨: "행복 LH", "장기 LH" 이런 식
            if label_prefix and agency:
                header_text = f"{label_prefix} {agency}"
            elif agency:
                header_text = agency
            else:
                header_text = item.get("complex") or item.get("name") or "공고"
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
                opacity: 0;
            ">
                <!-- 상단 검정 헤더 -->
                <div style="
                    background: rgba(0,0,0);
                    color: #fff;
                    font-weight: 700;
                    padding: 3px 0 4px 0;
                    font-size: 12px;
                ">
                    {header_text}
                </div>

                <!-- 흰색 본체 -->
                <div style="padding: 5px 6px 6px 6px;">
                    <div style="font-weight: 500;">{item.get('area', '—')}</div>
                    <div style="color: #000; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {item.get('deposit_short', item.get('deposit', '임대조건 정보 없음'))}
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
            tooltip_html = f"""
            <div style="font-family:'Pretendard','Malgun Gothic',sans-serif; font-size:11px;">
            <b>{complex_name}</b><br>
            <span style="color:#6b7280;">{item.get('location', '')}</span>
            </div>
            """
            # marker = folium.Marker(
            #     location=[lat, lon],
            #     icon=folium.DivIcon(html=popup_html)
            # )
            # marker.add_child(folium.Tooltip(tooltip_html, sticky=True))
            # marker.add_to(m)

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
        def convert_summary_to_html(text: str) -> str:
            if not text or not isinstance(text, str):
                return "공급대상 정보는 공고문을 참고하세요."

            import re
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            sentences = [s.strip() for s in sentences if len(s.strip()) > 1]

            # 줄바꿈으로만 구분
            joined = "<br>".join(f"• {s}" for s in sentences)

            # 앞뒤 개행/공백 없이 한 줄로 반환
            return f'<span style="font-size:13px; line-height:1.5;">{joined}</span>'
        def convert_rent_to_html(text: str) -> str:
            """
            임대조건 긴 문장을 줄바꿈해서 보기 좋게 만드는 함수
            (공급대상과 비슷한 스타일)
            """
            if not text or not isinstance(text, str):
                return "임대조건 정보는 공고문을 참고하세요."

            import re
            # 마침표 기준으로 문장 나누기 (한국어/영어 둘 다 대략 커버)
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            sentences = [s.strip() for s in sentences if len(s.strip()) > 1]

            # • 불릿 붙여서 줄바꿈
            joined = "<br>".join(f"• {s}" for s in sentences)

            # 한 줄짜리 HTML로 반환 (앞뒤 개행/들여쓰기 없음 → 밑 HTML 안 깨짐)
            return f'<span style="font-size:13px; line-height:1.5;">{joined}</span>'
        if selected:
            공고일 = selected.get("notice_date", "-")
            접수일 = selected.get("application_period", "-")
            조회수 = "-"  # 조회수는 백엔드에 없으면 그냥 '-' 로 두자
            raw_공급대상 = selected.get("eligibility_summary", "")
            공급대상_html = convert_summary_to_html(raw_공급대상)
            공급지역 = selected.get("location", "-")
            모집단지 = selected.get("complex", "모집단지 정보 없음")
            임대조건_html = convert_rent_to_html(selected.get("deposit", ""))
            전용면적 = selected.get("area", "-")  
            보증금 = selected.get("deposit", "-")  
            월세 = selected.get("monthly_rent_krw", None)
            # 월세 숫자값이 있을 때 표시용 문자열로 변환
            if 월세 is None:
                월세_text = "-"
            else:
                # 350000 → "35만원"
                if 월세 >= 10000:
                    월세_text = f"{월세 // 10000}만원"
                else:
                    월세_text = f"{월세}원"
            rows = []
            for step in selected.get("timeline_steps", []):
                step_name = (step.get("step_name") or "").strip()
                period = (step.get("period") or "").strip()
                if not step_name and not period:
                    continue

                # 줄바꿈/들여쓰기 없이 한 덩어리로 만들기
                rows.append(
                    f'<div style="display:flex; border-bottom:1px solid #e2e8f0;">'
                    f'<div style="width:45%; background:#f8fafc; padding:9px 10px; font-size:12.5px;">{step_name}</div>'
                    f'<div style="flex:1; padding:9px 10px; font-size:12.5px;">{period}</div>'
                    f'</div>'
                )

            # 사이에 굳이 개행 넣지 말고 바로 이어붙여도 됨
            timeline_rows = "".join(rows)

            raw_link = selected.get("link", "")
            link_href = raw_link if raw_link else "#"

            panel_html = f"""
            <div class="detail-panel">
                <div class="detail-header">
                    <div class="detail-badge">{selected.get('subscription_type', '공공임대')}</div>
                    <div class="detail-title">{selected['name']}</div>
                    <div class="detail-sub">{selected['location']}</div>
                    <div class="detail-meta">
                        <div>공고일 {공고일}</div>
                        <div>접수일 {접수일}</div>
                    </div>
                </div>
                <div class="detail-body">
                    <div class="section-title">공급대상 및 임대조건</div>
                    <div class="section-box">
                    <div style="margin-bottom:14px;">
                        <div style="font-weight:600; color:#475569; margin-bottom:6px; font-size:14px;">공급대상</div>
                        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px;
                                    padding:10px 12px; font-size:13px; line-height:1.55;">
                            {공급대상_html}
                        </div>
                    </div>
                    <div style="margin-bottom:14px;">
                        <div style="font-weight:600; color:#475569; margin-bottom:6px; font-size:14px;">
                            공급지역
                        </div>
                        <div style="
                            background:#ffffff;
                            border:1px solid #e2e8f0;
                            border-radius:10px;
                            padding:8px 10px;
                            font-size:13px;
                            line-height:1.5;
                        ">
                            {공급지역}
                        </div>
                    </div>
                        <div>
                            <div style="font-weight:600; color:#475569; margin-bottom:6px; font-size:14px;">임대조건</div>
                            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; font-size:13px; line-height:1.55;">
                                {임대조건_html}
                            </div>
                        </div>
                    </div>
                    <div class="section-title" style="margin-top:14px;">모집단지</div>
                    <div class="section-box">
                        <div class="section-row">
                            <span class="section-label">모집단지</span>
                            <span class="section-value">{모집단지}</span>
                        </div>
                        <div class="section-row">
                            <span class="section-label">전용면적</span>
                            <span class="section-value">{전용면적}</span>
                        </div>
                        <div class="section-row">
                            <span class="section-label">월세</span>
                            <span class="section-value">{월세_text}</span>
                        </div>
                    </div>
            <div class="section-title" style="margin-top:14px;">공급일정</div>
            <div class="section-box" style="padding:0;">
                {timeline_rows}
            </div>
            <div class="section-title" style="margin-top:14px;">문의</div>
            <div class="section-box">
                LH / SH 고객센터<br>
                접수 전 공고문 원문을 반드시 확인하세요.
            </div>
            </div>
            <a href="{link_href}"
            target="_blank" style="text-decoration:none;">
                <div class="detail-footer">공고 원문보기</div>
            </a>
            </div>
            """
            st.markdown(panel_html, unsafe_allow_html=True)
        
st.markdown('</div>', unsafe_allow_html=True)