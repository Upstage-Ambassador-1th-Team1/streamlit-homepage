"""
CSS styles for the Streamlit app
"""


def get_base_styles(page: str) -> str:
    """Get base CSS styles for the app."""
    return f"""
<style>
/* Hide default "Running..." status */
div[data-testid="stStatusWidget"] {{
    display: none !important;
}}

/* Hide default Streamlit page navigation */
div[data-testid="stSidebarNav"] {{
    display: none !important;
}}

div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {{
    justify-content: center !important; 
}}

div[data-testid="stSidebar"] button {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 90% !important;
    margin: 0 auto !important;
    margin-bottom: 15px !important;
    font-size: 34px;
    font-weight: bold;
    color: #2F4F6F;
    cursor: pointer;
    transform: scale(1.0);
    background-color: transparent !important;
    border: none;
    box-shadow: none;
}}

section[data-testid="stSidebar"] {{
    padding-left: 5px;
    padding-right: 5px;
    width: 210px !important;
}}

div[data-testid="stSidebar"] button:has(div:has(p:contains("채팅"))) {{
    background-color: {"#D8FCE8" if page=="home" else "transparent"} !important;
    border-bottom: {"3px solid #A7E4C2" if page=="home" else "none"} !important;
}}

div[data-testid="stSidebar"] button:has(div:has(p:contains("공고 검색"))) {{
    background-color: {"#D8FCE8" if page=="search" else "transparent"} !important;
    border-bottom: {"3px solid #A7E4C2" if page=="search" else "none"} !important;
}}

.content {{
    margin-left: 220px;
    padding: 20px;
    overflow: hidden;
}}

div[data-testid="stTextInput"] {{
    margin-top: -12px;
    margin-bottom: 0px;
}}

div[data-testid="stPopover"] div[data-testid="stPopoverBody"],
div[data-testid="stPopoverBody"] {{
    width: 350px !important;
    min-width: 350px !important;
    max-width: 350px !important;
}}
</style>
"""


def get_sidebar_styles() -> str:
    """Get sidebar button styles."""
    return """
<style>
button[kind="primary"], button[kind="secondary"] {
    background-color: transparent; 
    border: none;
    box-shadow: none;
    color: #2F4F6F;
    font-size: 20px;
    font-weight: bold;
    border-radius: 0;
    padding: 8px 0;
    text-align: center;
    width: 100%;
}
</style>
"""


def get_search_page_styles() -> str:
    """Get styles specific to search page."""
    return """
<style>
html, body {
    overflow: hidden !important;
}

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

div.stColumn > div:first-child {
    margin-top: 0px !important; 
}

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
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    word-break: keep-all;   
}

.listing-sub {
    font-size: 13px;
    line-height: 1.3;
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
    color: #1d4ed8;
    background: #e0edff;
    border-radius: 999px;
    vertical-align: middle;
    white-space: nowrap;
}

.listing-img {
    width: 78px;
    height: 78px;
    border-radius: 10px;
    object-fit: cover;
    flex-shrink: 0;
}
</style>
"""


def get_detail_panel_styles() -> str:
    """Get styles for the detail panel."""
    return """
<style>
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
"""

