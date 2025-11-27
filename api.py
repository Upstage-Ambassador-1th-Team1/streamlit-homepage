"""
API calls to the backend with caching
"""
import streamlit as st
import requests
import time
from config import HOUSING_API_URL
from utils import format_date, extract_region_from_address, extract_short_rent


@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide default spinner
def fetch_all_listings() -> list:
    """
    Fetch ALL listings from backend's cached endpoint.
    No filters - filtering is done on frontend.
    """
    try:
        start_time = time.time()
        
        resp = requests.get(
            f"{HOUSING_API_URL}/api/v1/listings/all",
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        
        # Process into frontend format
        raw_listings = []
        for item in data.get("items", []):
            addr = item.get("location_full_address") or ""
            depo = item.get("deposit_amount_krw") or 0
            rent = item.get("monthly_rent_krw") or 0
            area_m2 = item.get("exclusive_area_m2")
            financial = item.get("financial_terms_summary") or ""
            
            deposit_text = (item.get("deposit_and_rent_text") or "").strip()
            if not deposit_text:
                if depo or rent:
                    deposit_text = f"보증금 {depo:,}원 / 월 {rent:,}원"
                elif financial:
                    deposit_text = financial
                else:
                    deposit_text = "임대조건: 공고문 참고"
            
            # Get application period from timeline
            app_period = ""
            for step in item.get("timeline_steps", []):
                if "신청접수" in step.get("step_name", ""):
                    app_period = step.get("period", "")
                    break
            
            raw_listings.append({
                "id": item.get("id"),
                "name": item.get("announcement_title"),
                "complex": item.get("location_label") or "",
                "location": addr,
                "region": extract_region_from_address(addr),
                "deposit": deposit_text,
                "deposit_short": extract_short_rent(deposit_text),
                "area": f"{area_m2}㎡" if area_m2 else "-",
                "area_m2": area_m2,
                "deposit_amount_krw": depo,
                "monthly_rent_krw": rent,
                "notice_date": format_date(item.get("published_date") or ""),
                "application_period": app_period,
                "subscription_type": item.get("subscription_type") or "",
                "company_type": item.get("company_type") or "",
                "eligibility_summary": item.get("eligibility_summary") or "",
                "timeline_steps": item.get("timeline_steps") or [],
                "link": item.get("link") or "",
                "lat": item.get("latitude"),
                "lon": item.get("longitude"),
            })
        
        # Deduplicate
        dedup = {}
        for item in raw_listings:
            key = (item["name"], item["location"])
            if key not in dedup or (dedup[key]["deposit"].startswith("임대조건") and not item["deposit"].startswith("임대조건")):
                dedup[key] = item
        
        listings = list(dedup.values())
        elapsed = time.time() - start_time
        print(f"[LISTINGS] ⏱️ {elapsed:.2f}s | {len(raw_listings)} raw → {len(listings)} unique")
        return listings

    except Exception as e:
        print(f"[LISTINGS] ❌ Failed: {e}")
        st.error(f"백엔드에서 공고를 가져오는 중 오류: {e}")
        return []

