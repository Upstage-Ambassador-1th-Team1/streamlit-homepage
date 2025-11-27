"""
Configuration and constants for the Streamlit app
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API URLs
CHAT_BACKEND_URL = os.getenv("CHAT_BACKEND_URL", "http://localhost:8000")
HOUSING_API_URL = os.getenv("HOUSING_API_URL", "http://localhost:8000")

# Region coordinates for map
REGION_COORDS = {
    "서울": [37.5665, 126.9780],
    "경기": [37.4138, 127.5183],
    "인천": [37.4563, 126.7052],
    "강원": [37.8228, 128.1555],
    "충북": [36.6357, 127.4917],
    "충남": [36.5184, 126.8000],
    "대전": [36.3504, 127.3845],
    "세종": [36.4800, 127.2890],
    "전북": [35.7167, 127.1440],
    "전남": [34.8161, 126.4633],
    "광주": [35.1595, 126.8526],
    "경북": [36.4919, 128.8889],
    "경남": [35.4606, 128.2132],
    "부산": [35.1796, 129.0756],
    "대구": [35.8714, 128.6014],
    "울산": [35.5384, 129.3114],
    "제주": [33.4996, 126.5312],
}

# Filter options
LOCATION_OPTIONS = [
    "전체", "서울", "부산", "대구", "인천", "광주", "대전", "울산",
    "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"
]

COMPANY_OPTIONS = ["전체", "LH", "SH"]

HOUSE_TYPES = [
    "전체", "공공임대", "국민공공임대주택", "국민임대", "도시형생활주택",
    "매입임대", "매입임대주택", "영구임대", "장기안심주택", "장기전세주택",
    "전세임대", "청년안심주택", "행복주택"
]

# Pagination
ITEMS_PER_PAGE = 4
VISIBLE_PAGES = 5

