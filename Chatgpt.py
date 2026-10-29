import base64
import inspect
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import find_dotenv, load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv(), override=True)

BRAND = "hasnaaain-GPT-4.2"
HISTORY_FILE = Path(__file__).with_name("chat_history.json")
USER_AVATAR, AI_AVATAR = "😊", "✨"
MAX_HISTORY_MSGS = 30          # messages sent to the model each turn
MAX_DOC_CHARS = 40_000         # per attached document
MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"]
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
TEXT_EXT = {".txt", ".md", ".py", ".csv", ".json", ".js", ".ts", ".html", ".css",
            ".log", ".yaml", ".yml", ".xml", ".sql", ".ini", ".toml", ".java", ".c", ".cpp"}
ALL_EXT = sorted({e.lstrip(".") for e in IMAGE_EXT | TEXT_EXT | {".pdf"}})

PERSONAS = {
    "Helpful assistant": "You are a helpful, friendly assistant. Be clear and concise.",
    "Python tutor": "You are a patient Python tutor. Explain step by step and give small runnable examples.",
    "Code reviewer": "You are a senior engineer. Review code for bugs, style and performance; suggest fixes.",
    "Creative writer": "You are an imaginative writer. Use vivid language and original ideas.",
    "Study buddy": "You are a study buddy. Summarise, quiz the user, and explain concepts simply.",
}

SUGGESTIONS = [
    ("💡 Explain a concept simply", "Explain how neural networks learn, as if I'm 12."),
    ("🐍 Write some Python", "Write a Python function that removes duplicates from a list while keeping order."),
    ("📄 Summarise a document", "I'll attach a file - please summarise it in 5 bullet points."),
    ("🎨 Brainstorm ideas", "Give me 10 creative project ideas for an AI course."),
]

st.set_page_config(page_title=BRAND, page_icon="icon.png", layout="wide")

# --------------------------------------------------------------------------- #
# Styling  (light, colourful, animated background shapes, stylish fonts)
# --------------------------------------------------------------------------- #
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Outfit:wght@300;400;500;600&display=swap');

html, body, .stApp, .stApp p, .stApp label, .stApp li, .stApp button, .stApp input,
.stApp textarea, .stApp [data-baseweb] { font-family: 'Outfit', sans-serif; }
.stApp h1, .stApp h2, .stApp h3 { font-family: 'Bodoni Moda', serif; font-weight: 600; }

/* Palette B - Ocean Complementary (solid colours only, no gradients)
   bg #F2FAF9 | ink #12303B | muted #4F6B73 | teal #0F9D8F | coral #FF7A59 | sand #FFC857 | soft #D8F1EE | border #CFE5E2 */
.stApp { background: #F2FAF9; color: #12303B; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stBottom"], [data-testid="stBottom"] > div { background: transparent; }
.block-container { max-width: 860px; padding-top: 1.6rem; padding-bottom: 7rem; position: relative; z-index: 1; }

/* ---------- animated background shapes (only translate / rotate: never distorted) ---------- */
.bgfx { position: fixed; inset: 0; overflow: hidden; z-index: 0; pointer-events: none; }
.bgfx span { position: absolute; display: block; opacity: .28; will-change: transform; }
.s1 { width: 220px; height: 220px; border-radius: 50%; top: 6%; left: 24%;
      background: #0F9D8F; animation: driftA 22s ease-in-out infinite; }
.s2 { width: 160px; height: 160px; border-radius: 50%; top: 10%; right: 6%;
      border: 18px solid #FFC857; animation: driftB 26s ease-in-out infinite; }
.s3 { width: 120px; height: 120px; border-radius: 28px; bottom: 12%; left: 30%;
      background: #FFC857; animation: spin 30s linear infinite; }
.s4 { width: 150px; height: 150px; bottom: 8%; right: 7%;
      clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
      background: #FF7A59; animation: driftA 24s ease-in-out infinite reverse; }
.s5 { width: 70px; height: 70px; border-radius: 50%; top: 52%; left: 55%;
      background: #FF7A59; animation: driftB 18s ease-in-out infinite; }
.s6 { width: 90px; height: 90px; border-radius: 50%; top: 66%; right: 24%;
      border: 10px solid #0F9D8F; animation: driftA 20s ease-in-out infinite; }
.s7 { width: 100px; height: 100px; border-radius: 22px; top: 38%; left: 22%;
      background: #0F9D8F; transform: rotate(45deg);
      animation: spin 36s linear infinite reverse; }
@keyframes driftA { 0%,100% { transform: translate(0,0) rotate(0deg); }
                    50% { transform: translate(50px,-70px) rotate(180deg); } }
@keyframes driftB { 0%,100% { transform: translate(0,0) rotate(0deg); }
                    50% { transform: translate(-60px,60px) rotate(-120deg); } }
@keyframes spin   { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .bgfx span { animation: none !important; } }

/* ---------- brand ---------- */
.brandbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 1rem; }
.brand { font-family: 'Bodoni Moda', serif; font-size: 2rem; font-weight: 600; letter-spacing: -.5px; color: #12303B; line-height: 1.1; }
.brand i, .hero i { font-style: italic; color: #FF7A59; padding-right: 2px; }
.chip { display: inline-flex; align-items: center; height: 32px; padding: 0 14px; border-radius: 999px; font-size: .8rem;
        background: #FFFFFF; border: 1px solid #CFE5E2; color: #0F9D8F; white-space: nowrap; }
.hero { text-align: center; padding: 2.2rem 0 1.4rem; }
.hero .eyebrow { letter-spacing: .3em; font-size: .72rem; font-weight: 600; color: #0F9D8F; margin-bottom: .6rem; }
.hero h1 { font-family: 'Bodoni Moda', serif; font-weight: 500; font-size: clamp(2.2rem, 5vw, 3.6rem); line-height: 1.05; margin: 0; color: #12303B; }
.side-label { font-size: .7rem; letter-spacing: .18em; font-weight: 600; color: #0F9D8F; margin: 1rem 0 .4rem; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #CFE5E2; }
[data-testid="stSidebar"] > div:first-child { background: transparent; }
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap; gap: .4rem; align-items: center; }
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div:last-child button { justify-content: center; }

/* ---------- buttons (all same radius / height, nothing stretched) ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
    border-radius: 14px; min-height: 44px; font-weight: 500; background: #FFFFFF; color: #12303B;
    border: 1px solid #CFE5E2; transition: transform .15s ease, border-color .15s ease; }
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px); border-color: #0F9D8F; color: #0F9D8F; }
[data-testid="stSidebar"] .stButton > button { justify-content: flex-start; text-align: left; }
[data-testid="stSidebar"] .stButton > button p { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.stApp button[kind="primary"], .stApp button[data-testid="stBaseButton-primary"],
.stApp [data-testid="stFormSubmitButton"] > button {
    background: #0F9D8F; border: 1px solid #0F9D8F; color: #FFFFFF; }
.stApp button[kind="primary"]:hover, .stApp button[data-testid="stBaseButton-primary"]:hover,
.stApp [data-testid="stFormSubmitButton"] > button:hover { background: #0C857A; border-color: #0C857A; color: #FFFFFF; }
.stApp button[kind="primary"] p, .stApp button[data-testid="stBaseButton-primary"] p,
.stApp [data-testid="stFormSubmitButton"] > button p { color: #FFFFFF; }
.st-key-active_chat button { background: #D8F1EE; border-color: #0F9D8F; }

/* ---------- chat messages ---------- */
[data-testid="stChatMessage"] { background: #FFFFFF; border: 1px solid #CFE5E2;
    border-radius: 22px; padding: 14px 18px; margin-bottom: 12px; }
/* your messages: teal bubble on the right (white text) */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #0F9D8F; border-color: #0F9D8F; flex-direction: row-reverse; width: fit-content; max-width: 82%; margin-left: auto; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stCaptionContainer"],
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stCaptionContainer"] { color: #FFFFFF; }
[data-testid^="stChatMessageAvatar"] { border-radius: 50%; width: 38px; height: 38px; min-width: 38px; flex-shrink: 0; background: #FFC857; }
[data-testid="stChatInput"] { border-radius: 999px; border: 1.5px solid #0F9D8F; background: #FFFFFF; }
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] textarea { border-radius: 999px; background: transparent; }
[data-testid="stChatInput"] button { background: #FF7A59; color: #FFFFFF; border-radius: 50%; }

/* ---------- misc cards ---------- */
[data-testid="stExpander"] { border-radius: 16px; border: 1px solid #CFE5E2; background: #FFFFFF; overflow: hidden; }
[data-testid="stForm"] { border-radius: 24px; border: 1px solid #CFE5E2; background: #FFFFFF; padding: 1.4rem; }
[data-testid="stImage"] img { border-radius: 14px; }
</style>
<div class="bgfx"><span class="s1"></span><span class="s2"></span><span class="s3"></span><span class="s4"></span><span class="s5"></span><span class="s6"></span><span class="s7"></span></div>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# History storage
# --------------------------------------------------------------------------- #
def save_history():
    """Persist chats to disk (never the API key; image bytes are not stored)."""
    data = {"current": st.session_state.current, "chats": {}}
    for cid, c in st.session_state.chats.items():
        data["chats"][cid] = {
            **{k: v for k, v in c.items() if k != "messages"},
            "messages": [
                {
                    "role": m["role"],
                    "content": m["content"],
                    "files": m.get("files", []),
                    "n_images": len(m.get("images", [])) or m.get("n_images", 0),
                }
                for m in c["messages"]
            ],
        }
    try:
        HISTORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        pass


def load_history():
    if HISTORY_FILE.exists():
        try:
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            chats = data.get("chats", {})
            for c in chats.values():
                for m in c["messages"]:
                    m.setdefault("images", [])
            if chats:
                return chats, data.get("current") if data.get("current") in chats else next(iter(chats))
        except (OSError, ValueError, KeyError):
            pass
    return {}, None


def new_chat():
    cid = uuid.uuid4().hex[:8]
    st.session_state.chats[cid] = {
        "id": cid, "title": "New chat", "created": datetime.now().isoformat(timespec="seconds"),
        "messages": [], "docs": [],
    }
    st.session_state.current = cid
    save_history()


def current_chat():
    return st.session_state.chats[st.session_state.current]


if "chats" not in st.session_state:
    st.session_state.chats, st.session_state.current = load_history()
    if not st.session_state.chats:
        new_chat()
st.session_state.setdefault("api_key", "")
st.session_state.setdefault("uploader_n", 0)


# --------------------------------------------------------------------------- #
# Step 1: ask for the API key
# --------------------------------------------------------------------------- #
def validate_key(key: str):
    from openai import AuthenticationError, OpenAI
    try:
        OpenAI(api_key=key, timeout=15).models.list()
        return True, ""
    except AuthenticationError:
        return False, "That key was rejected by OpenAI. Please check it and try again."
    except Exception as e:  # network problems etc.
        return False, f"Couldn't verify the key: {e}"


def api_key_gate():
    st.markdown("<style>[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'], "
                "[data-testid='collapsedControl'] { display: none; }</style>", unsafe_allow_html=True)
    st.markdown("<div class='hero'><div class='eyebrow'>WELCOME TO</div>"
                "<h1>hasnaaain-GPT-<i>4.2</i></h1></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        with st.form("api_form"):
            st.markdown("**Enter your OpenAI API key to start chatting**")
            key = st.text_input("API key", type="password", placeholder="sk-...", label_visibility="collapsed")
            go = st.form_submit_button("Continue  →", use_container_width=True)
        st.caption(" Your key stays in this browser session only. It is never written to disk.")
        if go:
            if not key.strip():
                st.error("Please paste your API key first.")
            else:
                with st.spinner("Checking your key..."):
                    ok, msg = validate_key(key.strip())
                if ok:
                    st.session_state.api_key = key.strip()
                    st.rerun()
                else:
                    st.error(msg)
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key and st.button("Use the key from my .env file", use_container_width=True):
            with st.spinner("Checking your key..."):
                ok, msg = validate_key(env_key)
            if ok:
                st.session_state.api_key = env_key
                st.rerun()
            else:
                st.error(msg)
    st.stop()


if not st.session_state.api_key:
    api_key_gate()


# --------------------------------------------------------------------------- #
# File handling
# --------------------------------------------------------------------------- #
def read_pdf(data: bytes) -> str:
    try:
        from io import BytesIO
        from pypdf import PdfReader
    except ImportError:
        return "[PDF support needs:  pip install pypdf]"
    reader = PdfReader(BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def process_files(files, chat):
    """Return (image data-urls, attached file names). Text/PDF go into chat['docs']."""
    images, names = [], []
    for f in files:
        ext = Path(f.name).suffix.lower()
        data = f.getvalue()
        if ext in IMAGE_EXT:
            mime = f.type or f"image/{ext.lstrip('.')}"
            images.append(f"data:{mime};base64,{base64.b64encode(data).decode()}")
        elif ext == ".pdf" or ext in TEXT_EXT:
            text = read_pdf(data) if ext == ".pdf" else data.decode("utf-8", errors="replace")
            chat["docs"] = [d for d in chat["docs"] if d["name"] != f.name]
            chat["docs"].append({"name": f.name, "text": text[:MAX_DOC_CHARS]})
        else:
            st.toast(f"Skipped {f.name}: unsupported file type", icon="⚠️")
            continue
        names.append(f.name)
    return images, names


# --------------------------------------------------------------------------- #
# Sidebar: new chat, history, settings, tools
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("<div class='brand' style='font-size:1.45rem'>hasnaaain-GPT-<i>4.2</i></div>",
                unsafe_allow_html=True)
    if st.button("＋  New chat", type="primary", use_container_width=True, key="newchat"):
        new_chat()
        st.rerun()

    st.markdown("<div class='side-label'>HISTORY</div>", unsafe_allow_html=True)
    ordered = sorted(st.session_state.chats.values(), key=lambda c: c["created"], reverse=True)
    for c in ordered:
        is_active = c["id"] == st.session_state.current
        title = c["title"] if len(c["title"]) <= 26 else c["title"][:25] + "…"
        col_a, col_b = st.columns([5, 1])
        if col_a.button(("● " if is_active else "") + title, key="active_chat" if is_active else f"chat_{c['id']}",
                        use_container_width=True):
            st.session_state.current = c["id"]
            save_history()
            st.rerun()
        if col_b.button("✕", key=f"del_{c['id']}", use_container_width=True, help="Delete this chat"):
            del st.session_state.chats[c["id"]]
            if not st.session_state.chats:
                new_chat()
            elif st.session_state.current == c["id"]:
                st.session_state.current = next(iter(st.session_state.chats))
            save_history()
            st.rerun()

    st.markdown("<div class='side-label'>TOOLS</div>", unsafe_allow_html=True)
    with st.expander("⚙️  Settings"):
        model = st.selectbox("Engine", MODELS, key="model")
        temperature = st.slider("Creativity", 0.0, 1.5, 0.5, 0.1, key="temp")
        persona = st.selectbox("Personality", list(PERSONAS), key="persona")
        custom_system = st.text_area("Custom system role (optional)", key="custom_sys",
                                     placeholder="e.g. You are a friendly pirate...")

    chat_now = current_chat()
    with st.expander(f"📎  Files in this chat ({len(chat_now['docs'])})"):
        if not chat_now["docs"]:
            st.caption("Attach files with the 📎 in the message box.")
        for i, d in enumerate(chat_now["docs"]):
            ca, cb = st.columns([5, 1])
            ca.caption(f"📄 {d['name']}")
            if cb.button("✕", key=f"rmdoc_{i}", help="Remove file"):
                chat_now["docs"].pop(i)
                save_history()
                st.rerun()

    export_md = f"# {chat_now['title']}\n\n" + "\n\n".join(
        f"**{'You' if m['role'] == 'user' else BRAND}:** {m['content']}" for m in chat_now["messages"])
    st.download_button("⬇️  Export this chat", export_md, file_name="chat.md", mime="text/markdown",
                       use_container_width=True, disabled=not chat_now["messages"])
    if st.button("🔑  Change API key", use_container_width=True):
        st.session_state.api_key = ""
        st.rerun()
    approx_tokens = sum(len(m["content"]) for m in chat_now["messages"]) // 4
    st.caption(f"≈ {approx_tokens:,} tokens in this chat")


# --------------------------------------------------------------------------- #
# LLM helpers
# --------------------------------------------------------------------------- #
def system_text(chat) -> str:
    base = custom_system.strip() or PERSONAS[persona]
    text = f"Your name is {BRAND}. {base}"
    if chat["docs"]:
        text += "\n\nThe user attached these documents. Use them when relevant:\n"
        for d in chat["docs"]:
            text += f"\n### {d['name']}\n{d['text']}\n"
    return text


def to_langchain(chat):
    out = [SystemMessage(content=system_text(chat))]
    for m in chat["messages"][-MAX_HISTORY_MSGS:]:
        if m["role"] == "assistant":
            out.append(AIMessage(content=m["content"]))
        elif m.get("images"):
            parts = [{"type": "text", "text": m["content"] or "Please look at the attached image(s)."}]
            parts += [{"type": "image_url", "image_url": {"url": u}} for u in m["images"]]
            out.append(HumanMessage(content=parts))
        else:
            out.append(HumanMessage(content=m["content"]))
    return out


def generate(chat) -> bool:
    llm = ChatOpenAI(model=model, temperature=temperature, api_key=st.session_state.api_key, streaming=True)

    def tokens():
        for chunk in llm.stream(to_langchain(chat)):
            if chunk.content:
                yield chunk.content

    try:
        with st.chat_message("assistant", avatar=AI_AVATAR):
            reply = st.write_stream(tokens())
    except Exception as e:
        msg = str(e)
        if "401" in msg or "invalid_api_key" in msg:
            st.error("OpenAI rejected your API key. Use 🔑 Change API key in the sidebar.")
        else:
            st.error(f"Something went wrong: {msg}")
        return False
    chat["messages"].append({"role": "assistant", "content": reply, "images": []})
    save_history()
    return True


def render_message(m):
    with st.chat_message(m["role"], avatar=USER_AVATAR if m["role"] == "user" else AI_AVATAR):
        if m["role"] == "user":
            for img in m.get("images", []):
                st.image(img, width=220)
            if m.get("n_images") and not m.get("images"):
                st.caption(f"🖼️ {m['n_images']} image(s) (not kept after restart)")
            if m.get("files"):
                st.caption("📎 " + ", ".join(m["files"]))
        if m["content"]:
            st.markdown(m["content"])


# --------------------------------------------------------------------------- #
# Main area
# --------------------------------------------------------------------------- #
chat = current_chat()
st.markdown(f"<div class='brandbar'><div class='brand'>hasnaaain-GPT-<i>4.2</i></div>"
            f"<div class='chip'>{model} · {persona}</div></div>", unsafe_allow_html=True)

# Attachments: native 📎 in the chat box on recent Streamlit, expander fallback on older versions
HAS_CHAT_FILES = "accept_file" in inspect.signature(st.chat_input).parameters
fallback_files = []
if not HAS_CHAT_FILES:
    with st.expander("📎  Attach files"):
        fallback_files = st.file_uploader("Files", accept_multiple_files=True, type=ALL_EXT,
                                          key=f"up_{st.session_state.uploader_n}", label_visibility="collapsed")

if HAS_CHAT_FILES:
    box = st.chat_input(f"Message {BRAND}…", accept_file="multiple", file_type=ALL_EXT)
    in_text, in_files = (box["text"], list(box["files"])) if box else ("", [])
else:
    box = st.chat_input(f"Message {BRAND}…")
    in_text, in_files = (box or ""), list(fallback_files or [])

pending = st.session_state.pop("pending_prompt", None)
if pending:
    in_text, in_files = pending, []

should_generate = False
if st.session_state.pop("regen", False):
    should_generate = True
elif in_text.strip() or in_files:
    images, names = process_files(in_files, chat)
    text = in_text.strip() or "Please review the attached file(s)."
    chat["messages"].append({"role": "user", "content": text, "images": images, "files": names})
    if chat["title"] == "New chat":
        chat["title"] = (in_text.strip() or (names[0] if names else "New chat"))[:40]
    st.session_state.uploader_n += 1
    save_history()
    should_generate = True

if not chat["messages"]:
    st.markdown("<div class='hero'><div class='eyebrow'>YOUR PERSONAL AI</div>"
                "<h1>Hello, how can I <i>help</i> you today?</h1></div>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (label, prompt) in enumerate(SUGGESTIONS):
        if cols[i % 2].button(label, key=f"sg_{i}", use_container_width=True):
            st.session_state.pending_prompt = prompt
            st.rerun()

for m in chat["messages"]:
    render_message(m)

failed = False
if should_generate:
    if generate(chat):
        st.rerun()   # refresh sidebar title + show the regenerate button
    failed = True

if chat["messages"] and (not should_generate or failed):
    last_is_user = chat["messages"][-1]["role"] == "user"
    if st.button("↻  Retry" if last_is_user else "↻  Regenerate", key="regen_btn"):
        if not last_is_user:
            chat["messages"].pop()
        st.session_state.regen = True
        st.rerun()
