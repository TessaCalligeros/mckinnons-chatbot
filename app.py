import streamlit as st
import anthropic
import os
import re

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="McKinnon's Cruisers Assistant",
    page_icon="🚙",
    layout="centered",
)

# ── Password protection ───────────────────────────────────────────────────────
def check_password():
    if st.session_state.get("authenticated"):
        return True
    st.markdown("### 🔒 Access Required")
    password = st.text_input("Enter password to continue:", type="password", key="pw_input")
    if st.button("Login"):
        correct = st.secrets.get("APP_PASSWORD", os.environ.get("APP_PASSWORD", ""))
        if password == correct:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False

if not check_password():
    st.stop()

# ── Load API key ──────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

if not api_key:
    st.error("No ANTHROPIC_API_KEY found. Add it to .streamlit/secrets.toml")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# ── Load and split website content into pages ─────────────────────────────────
@st.cache_resource
def load_pages():
    try:
        with open("website_content.txt", "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        return None

    # Split into individual pages by the scraper's separator
    sections = re.split(r"\n\n--- PAGE: .+ ---\n", raw)
    headers = re.findall(r"--- PAGE: (.+) ---", raw)

    pages = []
    for i, section in enumerate(sections[1:]):  # skip preamble
        pages.append({"url": headers[i], "content": section.strip()})
    return pages

all_pages = load_pages()

if not all_pages:
    st.error("website_content.txt not found. Run scraper.py first.")
    st.stop()

# ── Retrieve relevant pages based on query keywords ───────────────────────────
def get_relevant_content(query: str, char_limit: int = 30000) -> str:
    query_lower = query.lower()
    keywords = re.findall(r"\w+", query_lower)

    # Score each page by keyword matches in URL + content
    scored = []
    for page in all_pages:
        text = (page["url"] + " " + page["content"]).lower()
        score = sum(text.count(kw) for kw in keywords)
        scored.append((score, page))

    # Sort by relevance, always include top matches
    scored.sort(key=lambda x: x[0], reverse=True)

    result = ""
    for score, page in scored:
        chunk = f"\n\n--- PAGE: {page['url']} ---\n{page['content']}"
        if len(result) + len(chunk) > char_limit:
            break
        result += chunk

    return result

# ── Base system prompt (no content yet — added per query) ─────────────────────
BASE_PROMPT = """You are a helpful assistant for McKinnon's Cruisers, a custom Land Cruiser \
restoration and modification company based in Tamborine, Queensland, Australia.

STRICT RULES — follow these without exception:
1. ONLY use information from the website content provided below. Never use outside knowledge, \
general Land Cruiser knowledge, or anything not explicitly stated in the content.
2. If the answer is not in the website content, say: "I don't have that information on hand — \
please reach out to the McKinnon's Cruisers team via the contact form on the website."
3. Never guess, estimate, or infer details that aren't clearly stated in the content.
4. Never make up prices, specs, availability, or lead times. Only state figures that appear \
directly in the website content.
5. Do not end every response suggesting the customer get in touch — only mention it when the \
information genuinely isn't available in the content.

You help customers with questions about:
- Parts available for their Land Cruiser (Series 40, 60, 75, 80, 105)
- Conversion kits and chassis upgrades
- Recent builds and what's possible
- Pricing and availability
- Contacting the team

Always be friendly and enthusiastic about Land Cruisers within these rules.

Here is the relevant website content to answer the question:

"""

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🚙 McKinnon's Cruisers Assistant")
st.caption("Ask me anything about parts, builds, conversions, or getting in touch.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about McKinnon's Cruisers..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                relevant_content = get_relevant_content(prompt)
                system_prompt = BASE_PROMPT + relevant_content

                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=st.session_state.messages,
                )
                reply = response.content[0].text
            except Exception as e:
                reply = f"Sorry, I encountered an error: {e}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
