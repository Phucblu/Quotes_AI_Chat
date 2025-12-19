import streamlit as st
import requests
import time
from gtts import gTTS
import io
from PIL import Image
import pytesseract

# ========== CONFIG ==========
st.set_page_config(page_title="Chat Clone", page_icon="💬", layout="centered")

# ========== CSS (chỉnh font-size ở đây) ==========
st.markdown("""
<style>
/* Nền */
body {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
}

/* Chat container (giữ để căn giữa) */
.chat-container { max-width: 720px; margin: 0 auto; padding: 24px 20px 100px; }

/* Header */
.header { display:flex; align-items:center; gap:12px; color:#fff; margin-bottom:16px; }
.header h1 { font-size:28px; margin:0; }

/* Bong bóng chat (dùng khi render bằng HTML) */
.bubble { display:flex; gap:12px; margin:10px 0; align-items:flex-start; }
.bubble .avatar { width:40px; height:40px; border-radius:50%; display:grid; place-items:center; font-size:20px; background:rgba(255,255,255,0.12); color:#fff; }
.bubble .content { max-width:78%; padding:12px 14px; border-radius:14px; line-height:1.5; font-size:16px; }

/* --- TÙY CHỈNH KÍCH THƯỚC CHỮ CHO QUOTE --- */
.quote-text { font-size:22px; font-weight:600; line-height:1.4; } /* <-- tăng/decrease ở đây */

/* User bubble */
.bubble.user { justify-content:flex-end; }
.bubble.user .content { background:#2ecc71; color:#0b2a18; border-bottom-right-radius:4px; box-shadow:0 6px 20px rgba(46,204,113,0.25); }
.bubble.user .avatar { order:2; background:rgba(255,255,255,0.18); color:#0b2a18; }

/* Assistant bubble */
.bubble.assistant { justify-content:flex-start; }
.bubble.assistant .content { background:rgba(255,255,255,0.12); color:#f1f1f1; border-bottom-left-radius:4px; backdrop-filter:blur(4px); box-shadow:0 6px 20px rgba(0,0,0,0.25); }

/* Input bar (nếu cần) */
.input-bar { position:fixed; left:0; right:0; bottom:0; background:rgba(0,0,0,0.45); border-top:1px solid rgba(255,255,255,0.15); backdrop-filter:blur(6px); padding:14px 16px; }
.input-inner { max-width:720px; margin:0 auto; display:flex; gap:10px; }
.input-inner input { flex:1; padding:12px 14px; border-radius:10px; border:1px solid rgba(255,255,255,0.15); background:rgba(255,255,255,0.10); color:#fff; }
.input-inner button { padding:10px 16px; border-radius:10px; border:none; background:#ffae42; color:#2a1900; cursor:pointer; font-weight:600; }

/* Typing dots (tăng kích thước dot nếu muốn) */
.typing { display:inline-flex; gap:6px; align-items:center; }
.dot { width:8px; height:8px; border-radius:50%; background:#eee; opacity:.8; animation:pulse 1.2s infinite ease-in-out; }
.dot:nth-child(2){ animation-delay:.2s; }
.dot:nth-child(3){ animation-delay:.4s; }
@keyframes pulse { 0%{ transform:translateY(0); opacity:.3; } 50%{ transform:translateY(-3px); opacity:.95; } 100%{ transform:translateY(0); opacity:.3; } }
</style>
""", unsafe_allow_html=True)

# ========== STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": str}

# ========== HEADER ==========
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown("""
    <div class="header">
        <span>💬</span>
        <h1>Chat Clone</h1>
    </div>
""", unsafe_allow_html=True)

# ========== HIỂN THỊ LỊCH SỬ ==========
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "assistant"
    avatar_emoji = "🧑‍💻" if msg["role"] == "user" else "🤖"
    # Nếu là quote (đánh dấu bằng key "is_quote_html"), render HTML để áp dụng class quote-text
    if msg.get("is_quote_html"):
        st.markdown(f"""
            <div class="bubble {role_class}">
                <div class="avatar">{avatar_emoji}</div>
                <div class="content"><div class="quote-text">{msg['content']}</div></div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="bubble {role_class}">
                <div class="avatar">{avatar_emoji}</div>
                <div class="content">{msg['content']}</div>
            </div>
        """, unsafe_allow_html=True)

# ========== NÚT TỪ KHOÁ ==========
col1, col2, col3 = st.columns(3)
with col1:
    btn_word = st.button("quotes word")
with col2:
    btn_pic = st.button("quotes picture")


prompt = None
if btn_word:
    prompt = "quotes word"
elif btn_pic:
    prompt = "quotes picture"


# ========== XỬ LÝ KHI NHẤN NÚT ==========
if prompt:
    # Lưu và hiển thị tin nhắn user
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()  # rerun để lịch sử user hiển thị ngay

# Nếu có tin nhắn mới (kiểm tra cuối danh sách)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last = st.session_state.messages[-1]["content"]

    # Hiệu ứng typing: chèn placeholder HTML, chờ, rồi xóa
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"""
            <div class="bubble assistant">
                <div class="avatar">🤖</div>
                <div class="content">
                    <span class="typing">
                        <span class="dot"></span>
                        <span class="dot"></span>
                        <span class="dot"></span>
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Giả lập thời gian xử lý (thay bằng gọi API thực tế nếu cần)
    time.sleep(1.6)

    # # Xử lý theo từ khoá
    #
    # elif "quotes picture" in last.lower():
    #     placeholder.empty()
    #     # ZenQuotes cung cấp endpoint ảnh; nếu không ổn, bạn có thể tạo ảnh riêng
    #     img_url = "https://zenquotes.io/api/image"
    #     st.session_state.messages.append({"role": "assistant", "content": f'<img src="{img_url}" alt="quote image" style="max-width:100%;">', "is_quote_html": False})
    #     st.rerun()
    #
    # elif "quotes word" in last.lower():
    #     res = requests.get("https://zenquotes.io/api/random")
    #     if res.status_code == 200:
    #         data = res.json()
    #         quote = f"“{data[0]['q']}” — {data[0]['a']}"
    #     else:
    #         quote = "Không lấy được quote lúc này 😢"
    #
    #     # Hiển thị text quote
    #     placeholder.empty()
    #     st.session_state.messages.append({"role": "assistant", "content": quote, "is_quote_html": True})
    #     st.rerun()
    #
    #     # Tạo audio (gTTS) và phát (lưu ý: rerun đã xảy ra; nếu muốn phát ngay, bạn có thể thay flow)
    #     # (Phát audio ngay trong cùng lần chạy nếu không dùng st.experimental_rerun)
    # else:
    #     placeholder.empty()
    #     reply = f"Mình đã nhận: “{last}”. Đây là phản hồi mẫu."
    #     st.session_state.messages.append({"role": "assistant", "content": reply})
    #     st.rerun()

    if "quotes picture" in last.lower():
        placeholder.empty()
        uploaded_file = st.file_uploader("Upload ảnh quote", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            text = pytesseract.image_to_string(img, lang="eng")
            if text.strip():
                st.session_state.messages.append({"role": "assistant", "content": text, "is_quote_html": True})
            else:
                st.session_state.messages.append(
                    {"role": "assistant", "content": "Không nhận diện được chữ trong ảnh 😢"})
            st.rerun()

    elif "quotes word" in last.lower():
        placeholder.empty()
        uploaded_file = st.file_uploader("Upload ảnh để đọc thành voice", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            text = pytesseract.image_to_string(img, lang="eng")
            if text.strip():
                st.session_state.messages.append({"role": "assistant", "content": text, "is_quote_html": True})
                # Tạo audio
                try:
                    tts = gTTS(text=text, lang="en", slow=True)
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.error("Không thể tạo audio: " + str(e))
            else:
                st.session_state.messages.append(
                    {"role": "assistant", "content": "Không nhận diện được chữ trong ảnh 😢"})
            st.rerun()

# # ========== PHÁT AUDIO CHO quotes voice (nếu cần) ==========
# # Lưu ý: để phát audio ngay sau khi hiển thị quote, ta kiểm tra message assistant cuối có phải quote và user trước đó là quotes voice
# if len(st.session_state.messages) >= 2:
#     last_assistant = st.session_state.messages[-1]
#     prev_user = st.session_state.messages[-2]
#     if prev_user["role"] == "user" and "quotes voice" in prev_user["content"].lower():
#         # Tạo audio từ text (gTTS)
#         text_for_audio = last_assistant["content"]
#         try:
#             tts = gTTS(text=text_for_audio, lang="en", slow=True)  # slow=True để đọc chậm
#             audio_bytes = io.BytesIO()
#             tts.write_to_fp(audio_bytes)
#             audio_bytes.seek(0)
#             st.audio(audio_bytes, format="audio/mp3")
#         except Exception as e:
#             st.error("Không thể tạo audio: " + str(e))


st.markdown('</div>', unsafe_allow_html=True)
