"""
Chat page component
"""
import streamlit as st
import requests
import uuid
from config import CHAT_BACKEND_URL


def render_chat_page():
    """Render the chat page."""
    # Fixed header gradient
    st.markdown("""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        height: 70px;
        background: linear-gradient(to bottom, #ffffff 60%, rgba(255,255,255,0) 100%);
        width: 100%;
        margin-bottom: 10px;
        z-index: 9999;
    "></div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요😊 당신의 집 요청 집착이에요! 🧚‍♀️<br> 원하시는 공공임대 공고를 '착'하고 불러와드릴게요 🏡<br>지역 / 예산 / 주택유형 아무거나 적어보세요 💬"}
        ]

    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"user_{uuid.uuid4().hex[:8]}"
    
    if 'is_loading' not in st.session_state:
        st.session_state.is_loading = False
    if 'pending_query' not in st.session_state:
        st.session_state.pending_query = None

    # Display messages
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

    # Handle streaming response
    if st.session_state.is_loading and st.session_state.pending_query:
        response_placeholder = st.empty()
        
        try:
            api_url = f"{CHAT_BACKEND_URL}/chat/stream"
            payload = {
                "content": st.session_state.pending_query,
                "session_id": st.session_state.session_id
            }
            
            with requests.post(api_url, json=payload, stream=True, timeout=60) as response:
                if response.status_code == 200:
                    full_response = ""
                    
                    for line in response.iter_lines():
                        if line:
                            try:
                                line_text = line.decode('utf-8').strip()
                                
                                if line_text.startswith('data: '):
                                    line_text = line_text[6:]
                                
                                if line_text == '[DONE]':
                                    continue
                                
                                data = requests.compat.json.loads(line_text)
                                
                                if data.get('type') == 'content':
                                    chunk = data.get('data', '')
                                    
                                    if chunk:
                                        full_response += chunk
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
                            except Exception:
                                continue
                    
                    assistant_response = full_response if full_response else "응답을 받지 못했습니다."
                else:
                    assistant_response = f"오류가 발생했습니다. (상태 코드: {response.status_code})"
        except requests.exceptions.ConnectionError:
            assistant_response = "⚠️ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요."
        except requests.exceptions.Timeout:
            assistant_response = "⚠️ 요청 시간이 초과되었습니다. 다시 시도해주세요."
        except Exception as e:
            assistant_response = f"⚠️ 오류가 발생했습니다: {str(e)}"
        
        st.session_state.messages[-1] = {"role": "assistant", "content": assistant_response}
        st.session_state.is_loading = False
        st.session_state.pending_query = None
        st.rerun()

    # Chat input
    user_input = st.chat_input("질문을 입력하세요.")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": "💭 답변 생성 중..."})
        st.session_state.is_loading = True
        st.session_state.pending_query = user_input
        st.rerun()

