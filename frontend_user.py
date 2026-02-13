"""
Dynamic User Frontend - CTF Security Lab
Interactive, customizable UI for users powered by Pydantic models
"""

import streamlit as st
import requests
import os
from dotenv import load_dotenv
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="🎯 CTF Security Lab",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# API Base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS for engaging UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    .challenge-card {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stats-box {
        background: linear-gradient(to right, #00d2ff 0%, #3a7bd5 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-message {
        background-color: #4CAF50;
        color: white;
        padding: 15px;
        border-radius: 5px;
        font-weight: bold;
    }
    .error-message {
        background-color: #f44336;
        color: white;
        padding: 15px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# Session state initialization
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_challenge' not in st.session_state:
    st.session_state.current_challenge = None
if 'user_stats' not in st.session_state:
    st.session_state.user_stats = {
        'score': 0,
        'solved': 0,
        'rank': 'N/A'
    }


def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Optional[Dict]:
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if st.session_state.access_token:
        headers['Authorization'] = f"Bearer {st.session_state.access_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None


def login_page():
    """User login interface"""
    st.markdown('<h1 class="main-header">🔐 CTF Security Lab</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🚀 Login to Start Hacking!")
        
        tab1, tab2 = st.tabs(["🔑 Login", "✨ Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("🎯 Login", use_container_width=True):
                # Login API call
                response = make_api_request(
                    "/api/v1/auth/login",
                    method="POST",
                    data={
                        "username": username,
                        "password": password,
                        "grant_type": "password"
                    }
                )
                
                if response and 'access_token' in response:
                    st.session_state.access_token = response['access_token']
                    st.session_state.username = username
                    st.success("✅ Login successful! Welcome back, hacker! 🎉")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Try again!")
        
        with tab2:
            new_username = st.text_input("Choose Username", key="reg_username")
            new_email = st.text_input("Email Address", key="reg_email")
            new_password = st.text_input("Create Password", type="password", key="reg_password")
            full_name = st.text_input("Full Name (Optional)", key="reg_fullname")
            
            st.info("💡 Password must be at least 8 characters with uppercase and digit")
            
            if st.button("🎊 Create Account", use_container_width=True):
                response = make_api_request(
                    "/api/v1/auth/register",
                    method="POST",
                    data={
                        "username": new_username,
                        "email": new_email,
                        "password": new_password,
                        "full_name": full_name
                    }
                )
                
                if response:
                    st.success("🎉 Account created! You can now login!")
                    st.balloons()


def dashboard_page():
    """Main user dashboard"""
    st.markdown('<h1 class="main-header">🎯 Your CTF Dashboard</h1>', unsafe_allow_html=True)
    
    # User stats at top
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-box">
            <h2>🏆 {st.session_state.user_stats['score']}</h2>
            <p>Total Points</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-box">
            <h2>✅ {st.session_state.user_stats['solved']}</h2>
            <p>Challenges Solved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-box">
            <h2>#{st.session_state.user_stats['rank']}</h2>
            <p>Global Rank</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-box">
            <h2>🔥 Level 5</h2>
            <p>User Level</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Challenges", 
        "🔥 Practice Lab", 
        "🎨 Steganography",
        "🏆 Leaderboard", 
        "💬 AI Assistant"
    ])
    
    with tab1:
        show_challenges()
    
    with tab2:
        show_practice_lab()
    
    with tab3:
        show_steganography()
    
    with tab4:
        show_leaderboard()
    
    with tab5:
        show_ai_assistant()


def show_challenges():
    """Display available challenges"""
    st.subheader("🎯 Available Challenges")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        difficulty_filter = st.selectbox(
            "🎚️ Difficulty",
            ["All", "Easy", "Medium", "Hard", "Expert"]
        )
    
    with col2:
        vuln_filter = st.selectbox(
            "🔍 Vulnerability Type",
            ["All", "SQL Injection", "XSS", "Command Injection", "Path Traversal", "CSRF", "XXE"]
        )
    
    # Get challenges from API
    response = make_api_request("/api/v1/challenges/")
    
    if response and 'challenges' in response:
        challenges = response['challenges']
        
        for challenge in challenges:
            with st.expander(f"{'🔓' if challenge.get('solved') else '🔒'} {challenge['title']} - {challenge['points']} pts"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {challenge['description']}")
                    st.markdown(f"**Type:** {challenge['vulnerability_type']}")
                    st.markdown(f"**Difficulty:** {challenge['difficulty']}")
                    st.markdown(f"**Solves:** {challenge.get('solve_count', 0)} hackers")
                    
                    if challenge.get('tags'):
                        tags = ' '.join([f"`{tag}`" for tag in challenge['tags']])
                        st.markdown(f"**Tags:** {tags}")
                
                with col2:
                    if st.button(f"🚀 Start", key=f"start_{challenge['id']}"):
                        st.session_state.current_challenge = challenge
                        st.success("Challenge loaded! 🎯")
                    
                    if st.button(f"💡 Hint", key=f"hint_{challenge['id']}"):
                        st.info("💡 Think about how user input is processed...")
    
    # Show current challenge
    if st.session_state.current_challenge:
        st.markdown("---")
        show_challenge_interface(st.session_state.current_challenge)


def show_challenge_interface(challenge: Dict):
    """Interactive challenge interface"""
    st.markdown("### 🎮 Active Challenge")
    
    st.markdown(f"""
    <div class="challenge-card">
        <h2>{challenge['title']}</h2>
        <p><strong>Points:</strong> {challenge['points']} | <strong>Difficulty:</strong> {challenge['difficulty']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Challenge Description:**\n{challenge['description']}")
    
    # Flag submission
    st.markdown("#### 🚩 Submit Your Flag")
    
    flag_input = st.text_input("Enter the flag you found:", key="flag_input")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("✅ Submit Flag", use_container_width=True):
            # Submit flag to API
            response = make_api_request(
                f"/api/v1/challenges/{challenge['id']}/submit",
                method="POST",
                data={
                    "challenge_id": challenge['id'],
                    "flag": flag_input
                }
            )
            
            if response:
                if response.get('success'):
                    st.markdown(f"""
                    <div class="success-message">
                        🎉 {response['message']}
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    
                    # Show meme
                    if response.get('meme'):
                        st.image(response['meme'], width=300)
                else:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ {response['message']}
                    </div>
                    """, unsafe_allow_html=True)


def show_practice_lab():
    """Practice vulnerability exploitation"""
    st.subheader("🔥 Live Vulnerability Lab")
    
    st.info("🎯 Practice exploiting real vulnerabilities in a safe environment!")
    
    vuln_type = st.selectbox(
        "Choose vulnerability to practice:",
        [
            "SQL Injection",
            "Cross-Site Scripting (XSS)",
            "Command Injection",
            "Path Traversal",
            "XXE (XML External Entity)"
        ]
    )
    
    if vuln_type == "SQL Injection":
        st.markdown("#### 💉 SQL Injection Practice")
        st.code("""
# Vulnerable endpoint: /api/v1/vulnerabilities/sql-injection/search
# Try injecting: ' OR '1'='1' --
        """)
        
        username_input = st.text_input("Search username:", key="sqli_input")
        
        if st.button("🔍 Search"):
            response = make_api_request(
                "/api/v1/vulnerabilities/sql-injection/search",
                params={"username": username_input}
            )
            
            if response:
                st.json(response)
                
                if response.get('success'):
                    st.success("✅ Exploitation successful!")
                    if response.get('meme'):
                        st.image(response['meme'], width=400)
    
    elif vuln_type == "Cross-Site Scripting (XSS)":
        st.markdown("#### 📜 XSS Practice")
        st.code("""
# Try injecting: <script>alert('XSS')</script>
# Or: <img src=x onerror=alert('XSS')>
        """)
        
        comment_input = st.text_area("Post a comment:", key="xss_input")
        
        if st.button("💬 Post Comment"):
            response = make_api_request(
                "/api/v1/vulnerabilities/xss/comment",
                method="POST",
                data={"comment": comment_input}
            )
            
            if response:
                st.json(response)


def show_steganography():
    """Steganography challenges"""
    st.subheader("🎨 Steganography & Encoding Lab")
    
    st.markdown("""
    Master the art of hidden messages! 🕵️
    
    Available challenges:
    - 🔤 Base64 Encoding (Multiple layers!)
    - 🖼️ Image Steganography (LSB)
    - 📡 Morse Code
    - 🔢 Binary & Hexadecimal
    - 🗝️ Classical Ciphers
    """)
    
    challenge_type = st.selectbox(
        "Choose challenge type:",
        ["Base64", "Hex", "Binary", "Morse Code", "Caesar Cipher"]
    )
    
    if st.button("🎲 Generate Challenge"):
        endpoint_map = {
            "Base64": "/api/v1/stego/base64/easy",
            "Hex": "/api/v1/stego/hex/challenge",
            "Binary": "/api/v1/stego/binary/challenge",
            "Morse Code": "/api/v1/stego/morse/challenge",
            "Caesar Cipher": "/api/v1/stego/cipher/caesar"
        }
        
        response = make_api_request(endpoint_map[challenge_type])
        
        if response:
            st.success("🎯 Challenge Generated!")
            st.json(response)
            
            # Show encoded data
            encoded_key = next((k for k in response.keys() if 'encoded' in k or 'cipher' in k or 'morse' in k or 'hex' in k or 'binary' in k), None)
            if encoded_key:
                st.code(response[encoded_key], language="text")
            
            # Decode submission
            st.markdown("#### 🔓 Submit Decoded Flag")
            decoded_input = st.text_input("Enter decoded flag:")
            
            if st.button("✅ Submit"):
                verify_response = make_api_request(
                    "/api/v1/stego/submit-decoded",
                    method="POST",
                    data={
                        "challenge_id": challenge_type.lower(),
                        "decoded_flag": decoded_input
                    }
                )
                
                if verify_response and verify_response.get('success'):
                    st.balloons()
                    st.success(verify_response['message'])


def show_leaderboard():
    """Display leaderboard"""
    st.subheader("🏆 Global Leaderboard")
    
    response = make_api_request("/api/v1/leaderboard/")
    
    if response and 'top_users' in response:
        leaderboard_data = []
        
        for user in response['top_users']:
            leaderboard_data.append({
                "Rank": f"#{user['rank']}",
                "Username": user['username'],
                "Score": user['total_score'],
                "Solved": user['solved_challenges'],
                "Badge": "🥇" if user['rank'] == 1 else "🥈" if user['rank'] == 2 else "🥉" if user['rank'] == 3 else "🏅"
            })
        
        df = pd.DataFrame(leaderboard_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.info(f"📊 Total registered hackers: {response.get('total_users', 'N/A')}")


def show_ai_assistant():
    """AI-powered assistant"""
    st.subheader("🧠 AI Assistant - Google Gemini")
    
    st.markdown("""
    Ask me anything about:
    - 🎯 Challenge hints
    - 🔍 Vulnerability explanations
    - 🛠️ Tools and techniques
    - 📚 Learning resources
    """)
    
    # Conversation history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                response = make_api_request(
                    "/api/v1/genai/help",
                    method="POST",
                    data={"question": prompt}
                )
                
                if response and response.get('response'):
                    ai_response = response['response']
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    error_msg = "Sorry, I couldn't process that. Try again!"
                    st.error(error_msg)


def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://media.giphy.com/media/YQitE4YNQNahy/giphy.gif", width=200)
        st.title("🎯 CTF Lab")
        
        if st.session_state.access_token:
            st.success(f"👤 {st.session_state.username}")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.access_token = None
                st.session_state.username = None
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            st.metric("Score", st.session_state.user_stats['score'])
            st.metric("Solved", st.session_state.user_stats['solved'])
            
            st.markdown("---")
            st.markdown("### 🎓 Resources")
            st.markdown("- [OWASP Top 10](https://owasp.org/www-project-top-ten/)")
            st.markdown("- [PortSwigger Academy](https://portswigger.net/web-security)")
            st.markdown("- [HackTheBox](https://www.hackthebox.com/)")
        else:
            st.info("👋 Welcome! Please login to start hacking!")
    
    # Main content
    if st.session_state.access_token:
        dashboard_page()
    else:
        login_page()


if __name__ == "__main__":
    main()
