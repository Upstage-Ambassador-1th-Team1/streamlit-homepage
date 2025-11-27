"""
Utility functions for text processing and formatting
"""
import re
from typing import Optional


def extract_short_rent(text: str) -> str:
    """Extract short rent info from text."""
    if not text:
        return "임대조건 정보 없음"

    m = re.search(r"(임대기간[^.]+가능)", text)
    if m:
        return m.group(1).strip()

    return text[:40] + "…" if len(text) > 40 else text


def format_date(date_str: str) -> str:
    """Convert '2025-09-30' to '2025.09.30' format."""
    if not date_str:
        return ""
    if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
        return date_str.replace("-", ".")
    return date_str


def extract_region_from_address(addr: str) -> Optional[str]:
    """Extract region name from full address."""
    if not addr:
        return None

    first_word = addr.strip().split()[0] if addr.strip() else ""
    
    # Map first word to region (based on actual data)
    REGION_MAP = {
        # 서울
        "서울특별시": "서울",
        "서울시": "서울",
        "서울": "서울",
        # 경기
        "경기도": "경기",
        "경기": "경기",
        # 부산
        "부산광역시": "부산",
        "부산": "부산",
        # 대구
        "대구광역시": "대구",
        "대구": "대구",
        # 인천
        "인천광역시": "인천",
        "인천": "인천",
        # 광주
        "광주광역시": "광주",
        # 대전
        "대전광역시": "대전",
        "대전": "대전",
        # 울산
        "울산광역시": "울산",
        "울산": "울산",
        # 세종
        "세종특별자치시": "세종",
        "세종": "세종",
        # 강원
        "강원특별자치도": "강원",
        "강원도": "강원",
        "강원": "강원",
        # 충북
        "충청북도": "충북",
        "충북": "충북",
        # 충남
        "충청남도": "충남",
        "충남": "충남",
        # 전북
        "전북특별자치도": "전북",
        "전라북도": "전북",
        "전북": "전북",
        # 전남
        "전라남도": "전남",
        "전남": "전남",
        # 경북
        "경상북도": "경북",
        "경북": "경북",
        # 경남
        "경상남도": "경남",
        "경남": "경남",
        # 제주
        "제주특별자치도": "제주",
        "제주": "제주",
    }
    
    region = REGION_MAP.get(first_word)
    if not region and first_word:
        print(f"[REGION] Unknown first word: '{first_word}' from address: {addr[:50]}")
    return region


def convert_summary_to_html(text: str) -> str:
    """Convert eligibility summary to HTML with bullet points."""
    if not text or not isinstance(text, str):
        return "공급대상 정보는 공고문을 참고하세요."

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 1]
    joined = "<br>".join(f"• {s}" for s in sentences)

    return f'<span style="font-size:13px; line-height:1.5;">{joined}</span>'


def convert_rent_to_html(text: str) -> str:
    """Convert rent conditions to HTML with bullet points."""
    if not text or not isinstance(text, str):
        return "임대조건 정보는 공고문을 참고하세요."

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 1]
    joined = "<br>".join(f"• {s}" for s in sentences)

    return f'<span style="font-size:13px; line-height:1.5;">{joined}</span>'


def get_housing_label(title_text: str) -> str:
    """Extract housing type label from title."""
    if "행복주택" in title_text:
        return "행복"
    elif "청년" in title_text:
        return "청년"
    elif "장기" in title_text:
        return "장기"
    elif "국민" in title_text:
        return "국민"
    elif "영구" in title_text:
        return "영구"
    elif "매입" in title_text:
        return "매입"
    elif "전세" in title_text:
        return "전세"
    elif "공공" in title_text:
        return "공공"
    elif "도시형" in title_text:
        return "도시형"
    return ""


def format_rent(amount: Optional[int]) -> str:
    """Format rent amount to Korean won."""
    if amount is None:
        return "-"
    if amount >= 10000:
        return f"{amount // 10000}만원"
    return f"{amount:,}원"

