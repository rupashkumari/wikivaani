import streamlit as st
import wikipediaapi
import speech_recognition as sr
from gtts import gTTS
import os
import base64
from datetime import datetime
import requests
from PIL import Image
import io
import time

# Initialize Wikipedia API with user_agent
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent="WikiVaaniApp/1.0 (https://example.com; your@email.com)"
)

# App configuration
st.set_page_config(
    page_title="Wiki Vaani",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for dark theme
st.markdown("""
<style>
.stApp {
    background-color: #000000;
    color: #ffffff;
}
.sidebar .sidebar-content {
    background-color: #1a1a1a;
    color: #ffffff;
}
.article-card {
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(255,255,255,0.1);
    background-color: #1a1a1a;
    margin-bottom: 20px;
    color: #ffffff;
}
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}
p, div, span {
    color: #ffffff !important;
}
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    color: #ffffff;
    background-color: #1a1a1a;
}
.st-bd, .st-cb, .st-cg, .st-ch, .st-ci, .st-cj, .st-ck, .st-cl, .st-cm {
    color: #ffffff;
}
.stRadio>div>div>label, .stCheckbox>div>div>label {
    color: #ffffff;
}
.stSelectbox>div>div>select {
    color: #ffffff;
    background-color: #1a1a1a;
}
.stSlider>div>div>div>div>div {
    background-color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# Audio functions
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

def text_to_speech(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save("output.mp3")
        autoplay_audio("output.mp3")
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")

# Voice recognition with PyAudio check
def recognize_speech():
    try:
        import pyaudio  # Check if PyAudio is installed
    except ImportError:
        st.error("Microphone access requires PyAudio. Please install it first:")
        st.code("pip install pyaudio")
        return None
    
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("Listening... Speak now (5 second timeout)")
            audio = r.listen(source, timeout=5)
            try:
                text = r.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                st.error("Could not understand audio")
                return None
            except sr.RequestError as e:
                st.error(f"Recognition service error: {str(e)}")
                return None
    except Exception as e:
        st.error(f"Microphone error: {str(e)}")
        return None

# Wikipedia functions
def get_wiki_page(title):
    try:
        page = wiki_wiki.page(title)
        if not page.exists():
            return {"error": "Page not found"}
        
        return {
            "title": page.title,
            "summary": page.summary[:500] + ("..." if len(page.summary) > 500 else ""),
            "url": page.fullurl,
            "content": page.text[:3000] + ("..." if len(page.text) > 3000 else ""),
        }
    except Exception as e:
        return {"error": f"Wikipedia error: {str(e)}"}

# AI functions (simplified)
def summarize_text(text, length="medium"):
    lengths = {"short": 100, "medium": 250, "long": 400}
    return text[:lengths[length]] + f"... [AI Summary - {length}]"

def translate_text(text, target_lang="en"):
    lang_map = {"French": "fr", "Spanish": "es", "German": "de", "Hindi": "hi"}
    return f"[{target_lang} Translation]: {text[:200]}... (Real translation would appear here)"

def explain_simply(text):
    return f"Simple Explanation: {text[:200]}... [This would be a child-friendly explanation]"

# Main app function
def main():
    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Wiki Vaani")
        st.markdown("---")
        
        # Navigation options
        nav_option = st.radio(
            "Menu",
            ["Search", "Voice Search", "History", "Settings"],
            index=0
        )
        
        st.markdown("---")
        st.subheader("Recent Searches")
        if not st.session_state.history:
            st.info("No search history")
        else:
            for i, item in enumerate(reversed(st.session_state.history[-3:])):
                if st.button(f"{item['query']} ({item['time']})", key=f"hist_{i}"):
                    st.session_state.last_search = item["query"]
                    nav_option = "Search"
    
    # Main content area
    if nav_option == "Search":
        st.title("Wikipedia Search")
        st.markdown("### 🔍 Wikipedia Search")
        search_query = st.text_input(
            label="",
            value=getattr(st.session_state, "last_search", ""),
            placeholder="e.g. Albert Einstein, India, Water Cycle",
            help="Type a topic, person, event, or concept you'd like to learn about from Wikipedia.",
            key="search"
        )
        
        if not search_query:
            st.info("💡 You can search for people (e.g. Mahatma Gandhi), countries (e.g. India), science topics (e.g. Water Cycle), or any other Wikipedia topic.")
        
        if search_query:
            with st.spinner(f"Searching for '{search_query}'..."):
                article = get_wiki_page(search_query)
                
                if "error" in article:
                    st.error(article["error"])
                else:
                    # Display article
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown("<div class='article-card'>", unsafe_allow_html=True)
                        st.header(article["title"])
                        st.markdown(f"**Summary**: {article['summary']}")
                        
                        with st.expander("Read Full Article"):
                            st.write(article["content"])
                        
                        st.subheader("AI Tools")
                        tab1, tab2, tab3 = st.tabs(["📝 Summarize", "🌍 Translate", "🧒 Explain Simply"])
                        
                        with tab1:
                            length = st.radio("Length", ["short", "medium", "long"], horizontal=True, key="sum_len")
                            if st.button("Generate Summary", key="sum_btn"):
                                summary = summarize_text(article["content"], length)
                                st.write(summary)
                                if st.checkbox("Read aloud", key="sum_audio"):
                                    text_to_speech(summary)
                        
                        with tab2:
                            lang = st.selectbox("Language", ["French", "Spanish", "German", "Hindi"], key="trans_lang")
                            if st.button("Translate", key="trans_btn"):
                                translation = translate_text(article["summary"], lang)
                                st.write(translation)
                                if st.checkbox("Read aloud", key="trans_audio"):
                                    text_to_speech(translation)
                        
                        with tab3:
                            if st.button("Simplify Explanation", key="simple_btn"):
                                simple = explain_simply(article["summary"])
                                st.write(simple)
                                if st.checkbox("Read aloud", key="simple_audio"):
                                    text_to_speech(simple)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("Quick Links")
                        st.markdown(f"[📖 Read on Wikipedia]({article['url']})")
                    
                    # Add to history
                    st.session_state.history.append({
                        "query": search_query,
                        "time": datetime.now().strftime("%H:%M"),
                        "title": article["title"]
                    })
    
    elif nav_option == "Voice Search":
        st.title("Voice Search")
        if st.button("Start Voice Search"):
            query = recognize_speech()
            if query:
                st.session_state.last_search = query
                st.rerun()  # Changed from st.experimental_rerun() to st.rerun()
    
    elif nav_option == "History":
        st.title("Search History")
        if not st.session_state.history:
            st.info("No search history yet")
        else:
            for i, item in enumerate(reversed(st.session_state.history)):
                st.write(f"{i+1}. {item['query']} ({item['time']})")
    
    elif nav_option == "Settings":
        st.title("Settings")
        st.subheader("Audio Settings")
        st.slider("Voice Speed", 0.5, 2.0, 1.0, key="voice_speed")
        st.radio("Voice Gender", ["Male", "Female"], key="voice_gender")
        
        st.subheader("Appearance")
        st.selectbox("Theme", ["Light", "Dark"], key="theme")

if __name__ == "__main__":
    main()
