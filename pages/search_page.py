"""
Search page component with map
"""
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium import MacroElement
from jinja2 import Template

from config import (
    REGION_COORDS, LOCATION_OPTIONS, COMPANY_OPTIONS, 
    HOUSE_TYPES, ITEMS_PER_PAGE, VISIBLE_PAGES
)
from api import fetch_all_listings
from utils import convert_summary_to_html, convert_rent_to_html, get_housing_label, format_rent, extract_region_from_address
from styles import get_search_page_styles, get_detail_panel_styles


def init_session_state():
    """Initialize session state for search page."""
    defaults = {
        "search_text": "",
        "selected_listing": None,
        "detail_tab": "content",
        "applied_price": None,
        "applied_area": None,
        "applied_house_type": "전체",
        "applied_company": "전체",
        "applied_location": "전체",
        "page_num": 1,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def render_filters(col_input, col_button):
    """Render search input and filter controls."""
    with col_input:
        st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
        keyword = st.text_input(
            "나에게 맞는 공고를 찾아보세요!", 
            placeholder="예: 서울 행복주택",
            key="search_text"  # Use session state key directly
        )

    with col_button:
        st.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
        
        filter_popover = st.popover("필터", use_container_width=True)
        
        with filter_popover:
            with st.form("filter_form"):
                location = st.selectbox(
                    "지역 선택", 
                    LOCATION_OPTIONS, 
                    index=LOCATION_OPTIONS.index(st.session_state.applied_location)
                )
                company = st.selectbox(
                    "공급기관", 
                    COMPANY_OPTIONS, 
                    index=COMPANY_OPTIONS.index(st.session_state.applied_company)
                )
                house_type = st.selectbox(
                    "주택 유형", 
                    HOUSE_TYPES, 
                    index=HOUSE_TYPES.index(st.session_state.applied_house_type)
                )
                
                # Get current applied values or defaults
                current_price = st.session_state.get("applied_price") or (500, 2000)
                current_area = st.session_state.get("applied_area") or (0, 150)
                
                price_range = st.slider(
                    "가격 범위 (만원)", 0, 10000,
                    current_price
                )
                area_range = st.slider(
                    "주택 면적 (㎡)", 0, 200,
                    current_area
                )

                submitted = st.form_submit_button("적용", use_container_width=True)
                if submitted:
                    st.session_state.applied_price = price_range
                    st.session_state.applied_area = area_range
                    st.session_state.applied_location = location
                    st.session_state.applied_house_type = house_type
                    st.session_state.applied_company = company
                    st.session_state.page_num = 1
                    st.toast("필터가 적용되었습니다.")


def get_filtered_listings():
    """
    Fetch ALL listings (cached) and filter on frontend.
    Same data used for both listing cards and map.
    """
    # Fetch ALL listings once (cached for 5 minutes)
    all_listings = fetch_all_listings()
    
    # Get filter settings
    applied_location = st.session_state.get("applied_location", "전체")
    applied_house_type = st.session_state.get("applied_house_type", "전체")
    applied_company = st.session_state.get("applied_company", "전체")
    applied_price = st.session_state.get("applied_price", None)
    applied_area = st.session_state.get("applied_area", None)
    keyword = (st.session_state.get("search_text") or "").strip().lower()
    
    # Filter on frontend
    filtered = []
    for item in all_listings:
        # Location filter
        if applied_location != "전체":
            region = item.get("region") or ""
            if region != applied_location:
                continue
        
        # House type filter
        if applied_house_type != "전체":
            if item.get("subscription_type") != applied_house_type:
                continue
        
        # Company filter
        if applied_company != "전체":
            if item.get("company_type") != applied_company:
                continue
        
        # Price filter (deposit)
        if applied_price:
            min_price, max_price = applied_price
            min_price *= 10_000  # Convert to won
            max_price *= 10_000
            deposit = item.get("deposit_amount_krw") or 0
            if deposit < min_price or deposit > max_price:
                continue
        
        # Area filter
        if applied_area:
            min_area, max_area = applied_area
            area = item.get("area_m2") or 0
            if area < min_area or area > max_area:
                continue
        
        # Keyword search
        if keyword:
            tokens = keyword.split()
            text = " ".join([
                item.get("name", ""),
                item.get("location", ""),
                item.get("complex", ""),
                item.get("subscription_type", ""),
            ]).lower()
            if not all(tok in text for tok in tokens):
                continue
        
        filtered.append(item)
    
    return filtered


def render_listing_card(item, idx):
    """Render a single listing card."""
    image_src = "https://via.placeholder.com/80x80?text=🏠"
    complex_html = f"<span class='complex-pill'>{item['complex']}</span>" if item.get("complex") else ""
    
    with st.container():
        clicked = st.button(" ", key=f"listing_{idx}", type="secondary", use_container_width=True)
        st.markdown(f"""
        <div style="
            position:relative;
            top:-62px;
            pointer-events:none;
            width:100%;
            box-sizing:border-box;
            background:#F8F9FA;
            border-radius:16px;
            box-shadow:0 4px 12px rgba(15,23,42,0.08);
            padding:14px 16px;
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
    
    if clicked:
        st.session_state.selected_listing = item


def render_pagination(total_items: int):
    """Render pagination controls."""
    total_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    current_page = st.session_state.page_num
    
    if current_page < 1:
        st.session_state.page_num = 1
        current_page = 1
    elif current_page > total_pages:
        st.session_state.page_num = total_pages
        current_page = total_pages

    # Calculate which pages to show (window around current page)
    start_page = max(1, current_page - VISIBLE_PAGES // 2)
    end_page = min(total_pages, start_page + VISIBLE_PAGES - 1)
    start_page = max(1, end_page - VISIBLE_PAGES + 1)
    
    cols = st.columns(VISIBLE_PAGES + 2)

    with cols[0]:
        if st.button("◀", key="prev_page_btn", disabled=(current_page <= 1)):
            st.session_state.page_num = max(1, current_page - 1)
            st.session_state.selected_listing = None
            st.rerun()

    for i, page_num in enumerate(range(start_page, end_page + 1)):
        with cols[i + 1]:
            label = f"**{page_num}**" if page_num == current_page else str(page_num)
            if st.button(str(page_num), key=f"page_btn_{page_num}"):
                st.session_state.page_num = page_num
                st.session_state.selected_listing = None
                st.rerun()

    with cols[-1]:
        if st.button("▶", key="next_page_btn", disabled=(current_page >= total_pages)):
            st.session_state.page_num = min(total_pages, current_page + 1)
            st.session_state.selected_listing = None
            st.rerun()


def create_region_icon(region_name: str, count: int, lat: float, lon: float):
    """Create custom icon for region marker."""
    header_bg = "#e91e63" if count > 0 else "#1E90FF"
    count_color = "#e91e63" if count > 0 else "#1E90FF"
    
    html = f"""
    <div class="region-marker" onclick="
        window.activeRegion = '{region_name}';
        if (typeof map !== 'undefined') {{
            map.flyTo([{lat}, {lon}], 13);
        }}
        document.querySelectorAll('.individual-listing-marker').forEach(function(el) {{
            el.style.display = 'block';
            el.style.opacity = '1';
        }});
    " style="
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
            background-color: {header_bg};
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
            <span style="color: {count_color}; font-weight: bold; font-size: 14px;">{count}</span>
        </div>
    </div>
    """
    return folium.DivIcon(html=html, icon_anchor=(30, 70))


def create_listing_marker_html(item: dict) -> str:
    """Create HTML for individual listing marker."""
    agency = (item.get("company_type") or "").strip()
    sub_type = (item.get("subscription_type") or "").strip()
    title_text = (item.get("name") or "") + " " + sub_type
    
    label = get_housing_label(title_text)
    header_text = f"{label} {agency}" if label and agency else agency or item.get("complex") or "공고"
    
    loc = item.get("location", "")
    region = (item.get("region") or extract_region_from_address(loc) or "").strip()

    return f"""
    <div class="individual-listing-marker" data-region="{region}" style="
        position: relative;
        display: inline-block;
        background: #fff;
        color: #333;
        border: 1.3px solid #000;
        border-radius: 6px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        font-family: 'Pretendard', 'Malgun Gothic', sans-serif;
        font-size: 12px;
        line-height: 1.4;
        text-align: center;
        overflow: hidden;
        width: 95px;
        opacity: 0;
    ">
        <div style="
            background: rgba(0,0,0);
            color: #fff;
            font-weight: 700;
            padding: 3px 0 4px 0;
            font-size: 12px;
        ">{header_text}</div>
        <div style="padding: 5px 6px 6px 6px;">
            <div style="font-weight: 500;">{item.get('area', '—')}</div>
            <div style="color: #000; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                {item.get('deposit_short', item.get('deposit', '임대조건 정보 없음'))}
            </div>
        </div>
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


class ToggleMarkers(MacroElement):
    """Toggle visibility of region vs detail markers based on zoom level."""
    _template = Template("""
    {% macro script(this, kwargs) %}
    var map = {{ this._parent.get_name() }};

    function applyZoomVisibility() {
        var zoom = map.getZoom();
        var regionMarkers = document.querySelectorAll('.region-marker');
        var detailMarkers = document.querySelectorAll('.individual-listing-marker');
        var activeRegion = window.activeRegion || null; 
        if (zoom >= 12) {
            regionMarkers.forEach(function(el) {
                el.style.display = 'none';
            });
            detailMarkers.forEach(function(el) {
                var markerRegion = el.getAttribute('data-region');
                if (activeRegion && markerRegion === activeRegion) {
                    el.style.display = 'block';
                    el.style.opacity = '1';
                } else {
                    el.style.display = 'none';
                    el.style.opacity = '0';
                }
            });
        } else {
            regionMarkers.forEach(function(el) {
                el.style.display = 'block';
            });
            detailMarkers.forEach(function(el) {
                el.style.display = 'none';
                el.style.opacity = '0';
            });
        }
    }
    window.applyZoomVisibility = applyZoomVisibility;

    map.whenReady(function() {
        applyZoomVisibility();
    });

    map.on('zoomend', applyZoomVisibility);
    {% endmacro %}
    """)


def render_map(listings: list):
    """Render the folium map with markers."""
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    
    # Count listings per region (using proper region extraction)
    region_counts = {key: 0 for key in REGION_COORDS.keys()}
    for item in listings:
        loc = item.get("location", "")
        region = item.get("region") or extract_region_from_address(loc)
        if region and region in region_counts:
            region_counts[region] += 1

    # Add region markers
    for region_name, count in sorted(region_counts.items(), key=lambda x: x[1]):
        if region_name in REGION_COORDS:
            lat, lon = REGION_COORDS[region_name]
            icon = create_region_icon(region_name, count, lat, lon)
            folium.Marker(
                location=[lat, lon],
                icon=icon,
                z_index_offset=count * 1000
            ).add_to(m)

    # Add individual listing markers (only those with coordinates)
    for item in listings:
        lat = item.get("lat")
        lon = item.get("lon")
        
        if not lat or not lon:
            continue  # Skip listings without coordinates
        
        popup_html = create_listing_marker_html(item)
        complex_name = item.get("complex") or item.get("name")
        tooltip_html = f"""
        <div style="font-family:'Pretendard','Malgun Gothic',sans-serif; font-size:11px;">
        <b>{complex_name}</b><br>
        <span style="color:#6b7280;">{item.get('location', '')}</span>
        </div>
        """
        
        marker = folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=popup_html)
        )
        marker.add_child(folium.Tooltip(tooltip_html, sticky=True))
        marker.add_to(m)

    # Add zoom toggle functionality
    m.get_root().add_child(ToggleMarkers())
    
    # Count markers with coordinates
    with_coords = sum(1 for item in listings if item.get("lat") and item.get("lon"))
    print(f"[MAP] {with_coords}/{len(listings)} listings have coordinates")
    
    return m


def render_detail_panel(selected: dict):
    """Render the detail panel for selected listing."""
    st.markdown(get_detail_panel_styles(), unsafe_allow_html=True)
    
    공고일 = selected.get("notice_date", "-")
    접수일 = selected.get("application_period", "-")
    공급대상_html = convert_summary_to_html(selected.get("eligibility_summary", ""))
    공급지역 = selected.get("location", "-")
    모집단지 = selected.get("complex", "모집단지 정보 없음")
    임대조건_html = convert_rent_to_html(selected.get("deposit", ""))
    전용면적 = selected.get("area", "-")
    월세_text = format_rent(selected.get("monthly_rent_krw"))
    
    rows = []
    for step in selected.get("timeline_steps", []):
        step_name = (step.get("step_name") or "").strip()
        period = (step.get("period") or "").strip()
        if step_name or period:
            rows.append(
                f'<div style="display:flex; border-bottom:1px solid #e2e8f0;">'
                f'<div style="width:45%; background:#f8fafc; padding:9px 10px; font-size:12.5px;">{step_name}</div>'
                f'<div style="flex:1; padding:9px 10px; font-size:12.5px;">{period}</div>'
                f'</div>'
            )
    timeline_rows = "".join(rows)
    
    link_href = selected.get("link", "") or "#"
    
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
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; font-size:13px; line-height:1.55;">
                        {공급대상_html}
                    </div>
                </div>
                <div style="margin-bottom:14px;">
                    <div style="font-weight:600; color:#475569; margin-bottom:6px; font-size:14px;">공급지역</div>
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:8px 10px; font-size:13px; line-height:1.5;">
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
        <a href="{link_href}" target="_blank" style="text-decoration:none;">
            <div class="detail-footer">공고 원문보기</div>
        </a>
    </div>
    """
    st.markdown(panel_html, unsafe_allow_html=True)


def render_search_page():
    """Render the search page."""
    st.markdown(get_search_page_styles(), unsafe_allow_html=True)
    
    init_session_state()
    
    # Show loading overlay while fetching data
    loading_placeholder = st.empty()
    
    # Check if data is already cached
    all_listings = None
    with loading_placeholder.container():
        st.markdown("""
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(255, 255, 255, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        ">
            <div style="
                font-size: 60px;
                margin-bottom: 20px;
                animation: bounce 1s infinite;
            ">🏠</div>
            <div style="
                font-size: 24px;
                font-weight: 600;
                color: #2F4F6F;
                margin-bottom: 10px;
            ">공고 정보를 불러오는 중입니다</div>
            <div style="
                font-size: 16px;
                color: #6b7280;
            ">잠시만 기다려주세요...</div>
            <div style="
                margin-top: 30px;
                width: 50px;
                height: 50px;
                border: 4px solid #e5e7eb;
                border-top: 4px solid #2F4F6F;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
        </style>
        """, unsafe_allow_html=True)
        all_listings = get_filtered_listings()
    
    # Clear loading overlay
    loading_placeholder.empty()
    
    col_gap, col_search, col_gap2, col_map = st.columns([0.2, 2, 0.1, 5])

    # Left column: Search and listings
    with col_search:
        col_input, col_button = st.columns([4, 1.1])
        render_filters(col_input, col_button)
        
        # Frontend pagination
        total = len(all_listings)
        start = (st.session_state.page_num - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_items = all_listings[start:end]
        
        st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
        
        if len(page_items) == 0:
            st.markdown(
                """
                <div style="margin-top: 40px; text-align: center; color: #6b7280; font-size: 16px;">
                    🔍 검색된 공고가 없습니다
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for idx, item in enumerate(page_items):
                render_listing_card(item, idx)
            render_pagination(total)

    # Right column: Map (same data as listings)
    with col_map:
        m = render_map(all_listings)
        st_folium(
            m, 
            width="100%", 
            height=845,
            key="housing_map",
            returned_objects=[],  # Prevent rerun on zoom/pan
        )

        # Detail panel
        if st.session_state.selected_listing:
            render_detail_panel(st.session_state.selected_listing)

