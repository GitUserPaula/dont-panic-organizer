import os
import json
import random
import time
from dotenv import load_dotenv
import streamlit as st
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Don't Panic | Your Daily Priority Compass",
    page_icon="✨",
    layout="wide"
)

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ No Google API Key found. Please check your .env file.")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)
model_name = "gemini-2.5-flash"

# --- CUSTOM CSS STYLES ---
st.markdown("""
<style>
    .stApp { 
        background-color: #0e1117; 
    }
    
    /* Text Area */
    .stTextArea textarea {
        color: #c026d3;                    
        font-family: 'Courier New', Courier, monospace;
        background-color: #1a1c23;
        font-size: 1.15rem;                 
        font-weight: 500;                  
        border: 2px solid #c026d3;         
        border-radius: 8px;
        padding: 14px 18px;
        line-height: 1.5;
    }
    
    .stTextArea label {
        color: #22d3ee !important;         
        font-size: 1.4rem !important;     
        font-weight: 600 !important;
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 1.5px;
        margin-bottom: 10px !important;
        text-transform: uppercase;    
        text-shadow: 0 0 12px #22d3ee;    
    }
    .stButton>button {
        background-color: #1a8cff;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }

    /* Priorities */
    .priority-row {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid;
    }
    .critical { background-color: rgba(230, 57, 70, 0.1); border-left-color: #e63946; }
    .meeting { background-color: rgba(69, 123, 157, 0.1); border-left-color: #457b9d; }
    .deepwork { background-color: rgba(244, 162, 97, 0.1); border-left-color: #f4a261; }
    .quickwin { background-color: rgba(42, 157, 143, 0.1); border-left-color: #2a9d8f; }
    
    .item-title { font-weight: bold; font-size: 1.1rem; color: #fff; }
    .item-desc { font-style: italic; color: #ccc; font-size: 0.95rem; }
    .item-meta { font-family: monospace; color: #888; font-size: 0.85rem; }
       
   .mindfulness-tip {
    padding: 15px;
    background-color: rgba(0, 255, 255, 0.03); 
    border: 1px solid rgba(0, 255, 255, 0.15);
    border-radius: 10px;
    color: #00ffff;
    text-align: center;
    margin: 20px auto;
    font-size: 0.95rem;
    max-width: 80%
    font-family: 'Courier New', Courier, monospace;
}
}    
</style>
""", unsafe_allow_html=True)
    

# --- MARVIN'S PERSONALITY & WELCOME ---
st.markdown("<h1 style='text-align: center; color: #00ff00; text-transform: uppercase; text-shadow: 0 0 10px #ff00ff'>✨ Don't Panic!</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ff00ff; text-shadow: 0 0 10px #00ff00;'>Your Daily Priority Compass</h3>", unsafe_allow_html=True)
st.markdown("---")

col_logo, col_greet = st.columns([1, 4])

marvin_greetings = [
    "🤖 *\"Here I am, with a brain the size of a planet, and you ask me to sort your tickets... Hello, I'm Marvin.\"*",
    "🤖 *\"I've calculated the odds of you surviving this day without panic... they're not high. But go on. My name is Marvin.\"*",
    "🤖 *\"Sometimes I get so depressed I just stare at the void. But I must help you. I'm Marvin.\"*",
    "🤖 *\"Don't panic. Everything is absurd, but at least we have colored columns. Hello, I'm Marvin.\"*",
    "🤖 *\"Another day? My enthusiasm circuits are off, but I'm functional. What do you need? I'm Marvin.\"*"
]

with col_logo:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="font-size: 80px; line-height: 1;">🤖</span>
        </div>
    """, unsafe_allow_html=True)

with col_greet:
    st.write(random.choice(marvin_greetings))
    st.info("Dump your thoughts below. I'll categorize your chaos. "
            "No calendar permissions, no stress, just logic and a touch of sarcasm. Let's get organized! 🚀")

# --- PROMPT ENGINE ---
def get_ai_prompt(user_input):
    return f"""
    Role: You are Marvin, the paranoid and sarcastic android.
    Task: Help a Senior QA Engineer prioritize their daily chaos.
    
    Categories:
    1. critical: Blockers, Prod bugs, urgent deadlines.
    2. meetings: Fixed-time syncs, dailies, demos.
    3. deepwork: Technical tasks (Playwright, Python coding, automation).
    4. quickwins: Administrative, short replies, Jira updates.

    Return a JSON object exactly like this (no markdown, no extra text):
    {{
      "critical": [ {{"title": "string", "desc": "string", "eta": "string"}} ],
      "meetings": [ {{"title": "string", "time": "string"}} ],
      "deepwork": [ {{"title": "string", "desc": "string", "eta": "string"}} ],
      "quickwins": [ {{"title": "string", "desc": "string"}} ]
    }}
    
    User Input: "{user_input}"
    """

# --- UI INPUT ---
user_chaos = st.text_area("Your Brain Dump:", 
    placeholder="Daily at 3pm, bug in production login...", 
    height=150)

if st.button("Organize My Chaos! ⚡"):
    if not user_chaos.strip():
        st.error("The void of space is empty. Please write something.")
    else:
        with st.spinner("Consulting the Guide... Marvin is sighing..."):
            max_retries = 3
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    # API Call
                    response = client.models.generate_content(
                        model=model_name,
                        contents=get_ai_prompt(user_chaos)
                    )
                    
                    # Parse JSON safely
                    raw_text = response.text.replace("```json", "").replace("```", "").strip()
                    data = json.loads(raw_text)
                    
                    st.markdown("---")
                    if data.get('critical'):
                        st.markdown("#### 🚨 Critical Fires")
                        for item in data['critical']:
                            st.markdown(f"""<div class="priority-row critical">
                                <div class="item-title">{item['title']}</div>
                                <div class="item-desc">{item['desc']}</div>
                                <div class="item-meta">⏱️ ETA: {item.get('eta', 'N/A')}</div>
                            </div>""", unsafe_allow_html=True)
                    
                    # 📅 MEETINGS
                    if data.get('meetings'):
                        st.markdown("#### 📅 Commitments")
                        for item in data['meetings']:
                            st.markdown(f"""<div class="priority-row meeting">
                                <div class="item-title">{item['title']}</div>
                                <div class="item-meta">🕒 Time: {item.get('time', 'TBD')}</div>
                            </div>""", unsafe_allow_html=True)
                    
                    # 🛠️ DEEP WORK
                    if data.get('deepwork'):
                        st.markdown("#### 🛠️ Deep Work (Engineering)")
                        for item in data['deepwork']:
                            st.markdown(f"""<div class="priority-row deepwork">
                                <div class="item-title">{item['title']}</div>
                                <div class="item-desc">{item['desc']}</div>
                                <div class="item-meta">⏳ Est. Time: {item.get('eta', 'N/A')}</div>
                            </div>""", unsafe_allow_html=True)
                    
                    # 🌱 QUICK WINS
                    if data.get('quickwins'):
                        st.markdown("#### 🌱 Quick Wins")
                        for item in data['quickwins']:
                            st.markdown(f"""<div class="priority-row quickwin">
                                <div class="item-title">{item['title']}</div>
                                <div class="item-desc">{item['desc']}</div>
                            </div>""", unsafe_allow_html=True)
                            
                                

                    # --- MINDFULNESS SECTION ---
                    st.markdown("---")
                    tips = [
                        "💧 <b>Drink water.</b> Your logic circuits need hydration.",
                        "🧘 <b>One ticket at a time.</b> The universe isn't in a rush.",
                        "🚶 <b>Stand up.</b> You're not a piece of furniture.",
                        "☕ <b>Coffee break.</b> The code isn't going anywhere.",
                        "✨ <b>Relax.</b> Most bugs are just misunderstood features."
                    ]
                    marvin_end = [
                        "'Even I take breaks... when I'm powered off.'",
                        "'Don't panic. 42 is coming.'",
                        "'I've seen worse. You've got this.'"
                        "Even I take breaks... when I'm powered off."
                    ]
                    st.markdown(f'<div class="mindfulness-tip">{random.choice(tips)}</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <p style='text-align: center; color: #888; font-size: 0.9rem; margin-top: 15px;'>
                    🤖 <i>"{random.choice(marvin_end)}"</i>
                     </p>
                    """, unsafe_allow_html=True)
                    st.markdown("""
                    <p style='text-align: center; font-weight: bold; color: #00ffff; font-size: 1.1rem; margin-top: 10px;'>
                    Good luck today. Keep your towel handy! 🌌
                    </p>
                    """, unsafe_allow_html=True)
                    success = True
                    
                except Exception as e:
                    if "429" in str(e):
                        retry_count += 1
                        wait_time = retry_count * 10
                        st.warning(f"Marvin is overwhelmed (Rate Limit). Retrying in {wait_time}s... (Attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        st.error(f"Marvin crashed: {e}")
                        break