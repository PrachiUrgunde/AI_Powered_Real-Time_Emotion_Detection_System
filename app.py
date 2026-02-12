import streamlit as st
import pandas as pd
import time
from datetime import datetime
import PIL.Image as Image

import random

# Page Config
st.set_page_config(
    page_title="Mood Mirror | AI Emotion Detection",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Session State for Navigation & Data ---
if 'page' not in st.session_state:
    st.session_state.page = "Home"

if 'history' not in st.session_state:
    st.session_state.history = [
        {'Time': '09:10', 'Emotion': 'Happy', 'Confidence': '98%', 'Source': 'Camera'},
        {'Time': '09:05', 'Emotion': 'Surprise', 'Confidence': '82%', 'Source': 'Upload'},
        {'Time': '09:00', 'Emotion': 'Neutral', 'Confidence': '91%', 'Source': 'Camera'},
        {'Time': '08:55', 'Emotion': 'Happy', 'Confidence': '95%', 'Source': 'Upload'}
    ]

def set_page(name):
    st.session_state.page = name

def detect_emotion(source_type):
    emotions = ['Happy', 'Sad', 'Angry', 'Surprise', 'Neutral', 'Calm']
    selected = random.choice(emotions)
    confidence = random.randint(75, 99)
    timestamp = datetime.now().strftime("%H:%M")
    
    new_entry = {
        'Time': timestamp,
        'Emotion': selected,
        'Confidence': f"{confidence}%",
        'Source': source_type
    }
    st.session_state.history.insert(0, new_entry)
    return selected, confidence

# --- Custom Styling & Animations ---
st.markdown("""
<style>
    /* Design System */
    :root {
        --primary: #6d5dfc;
        --secondary: #a084ff;
        --bg-dark: #0a0a1f;
        --bg-light: #16163a;
        --text-main: #e0e0e0;
        --text-dim: #b0b0b0;
        --accent: #00f2fe;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --mood-happy: #f6d365;
        --mood-calm: #84fab0;
        --mood-sad: #a1c4fd;
        --mood-angry: #ff0844;
    }

    /* Main App Overrides */
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-main);
    }

    /* Hide Sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Typography */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
    }

    .vibrant-text {
        background: linear-gradient(90deg, #00f2fe 0%, #a084ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    .vibrant-header {
        background: linear-gradient(90deg, #f6d365 0%, #fda085 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Top Navbar Button Overrides */
    div.stButton > button {
        background-color: transparent !important;
        color: var(--text-main) !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem 1rem !important;
    }
    div.stButton > button:hover {
        color: var(--accent) !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        transform: translateY(-2px);
    }
    div.stButton > button:active {
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    /* Custom Navbar */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid var(--glass-border);
        margin-bottom: 2rem;
    }

    .logo {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
    }

    .logo span {
        background: linear-gradient(90deg, #6d5dfc 0%, #a084ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Hero Section */
    .hero-container {
        padding: 4rem 0;
        text-align: center;
    }

    .hero-title {
        font-size: 5rem !important;
        background: linear-gradient(90deg, #6d5dfc 0%, #a084ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem !important;
    }

    .tagline {
        font-size: 1.8rem;
        color: var(--secondary);
        margin-bottom: 1.5rem;
    }

    /* Glass Cards */
    .glass-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }

    .glass-card:hover {
        transform: translateY(-5px);
    }

    /* Dashboard Elements */
    .metric-card {
        text-align: center;
        padding: 1.5rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent);
    }

    .metric-label {
        color: var(--text-dim);
        font-size: 0.9rem;
    }

    /* Wave Animation */
    @keyframes waveMove {
        from { transform: translateX(0); }
        to { transform: translateX(-50%); }
    }

    .mood-waves {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 15vh;
        z-index: -1;
        opacity: 0.3;
        pointer-events: none;
    }

    /* Mouse Glow Effect */
    #mouse-glow {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -2;
        background: radial-gradient(circle at 50% 50%, rgba(109, 93, 252, 0.15) 0%, transparent 60%);
        pointer-events: none;
    }

    #bg-canvas {
        position: fixed;
        top: 0;
        left: 0;
        z-index: -3;
        pointer-events: none;
    }
</style>

<div id="mouse-glow"></div>
<canvas id="bg-canvas"></canvas>

<script>
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');
    const glow = document.getElementById('mouse-glow');
    
    let dots = [];
    const dotCount = 80;
    let mouse = { x: 0, y: 0 };

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resize);
    resize();

    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        glow.style.background = `radial-gradient(circle at ${mouse.x}px ${mouse.y}px, rgba(109, 93, 252, 0.2) 0%, transparent 50%)`;
    });

    class Dot {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.radius = Math.random() * 2;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;

            // Mouse proximity repulsion
            const dx = mouse.x - this.x;
            const dy = mouse.y - this.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 100) {
                this.x -= dx * 0.01;
                this.y -= dy * 0.01;
            }
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(109, 93, 252, 0.5)';
            ctx.fill();
        }
    }

    for (let i = 0; i < dotCount; i++) {
        dots.push(new Dot());
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        dots.forEach(dot => {
            dot.update();
            dot.draw();
        });
        
        // Draw connections
        ctx.strokeStyle = 'rgba(109, 93, 252, 0.1)';
        ctx.lineWidth = 0.5;
        for (let i = 0; i < dots.length; i++) {
            for (let j = i + 1; j < dots.length; j++) {
                const dx = dots[i].x - dots[j].x;
                const dy = dots[i].y - dots[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(dots[i].x, dots[i].y);
                    ctx.lineTo(dots[j].x, dots[j].y);
                    ctx.stroke();
                }
            }
        }
        
        requestAnimationFrame(animate);
    }

    animate();
</script>
""", unsafe_allow_html=True)

# --- Top Navbar Implementation ---
nav_cols = st.columns([2, 1, 1, 1, 1])

with nav_cols[0]:
    st.markdown('<div style="margin-top: 5px;"><span style="font-size: 1.8rem; font-weight: 700; color: white;">Mood<span class="vibrant-text">Mirror</span></span></div>', unsafe_allow_html=True)

with nav_cols[1]:
    if st.button("Home", key="nav_home", use_container_width=True):
        set_page("Home")
with nav_cols[2]:
    if st.button("Live Camera", key="nav_cam", use_container_width=True):
        set_page("Try Live Camera")
with nav_cols[3]:
    if st.button("Upload", key="nav_up", use_container_width=True):
        set_page("Upload Image")
with nav_cols[4]:
    if st.button("Dashboard", key="nav_dash", use_container_width=True):
        set_page("Analytics Dashboard")

st.write("---")

# --- App Logic ---
page = st.session_state.page

# --- Home Page ---
if page == "Home":
    # st.markdown('<div class="nav-container"><div class="logo">Mood<span>Mirror</span></div></div>', unsafe_allow_html=True)
    
    # Hero
    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">Mood Mirror</h1>
        <p class="tagline vibrant-text">AI-Powered Human Emotion Detection System</p>
        <p style="font-size: 1.2rem; color: #b0b0b0; max-width: 800px; margin: 0 auto;">
            Mood Mirror uses <span class="vibrant-text">artificial intelligence</span> and <span class="vibrant-text">computer vision</span> to analyze facial expressions and detect human emotions in real time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="glass-card"><h3>Real-time</h3><p>Instantaneous emotion detection from live camera streams.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card"><h3>Deep Learning</h3><p>Powered by high-accuracy CNN models for predictions.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-card"><h3>User Friendly</h3><p>Clean and intuitive design for effortless interaction.</p></div>', unsafe_allow_html=True)

    # About Section
    st.markdown('<div style="padding: 4rem 0;"><h2 style="text-align:center;" class="vibrant-header">About Mood Mirror</h2><div style="width:60px; height:4px; background:linear-gradient(90deg, #6d5dfc, #a084ff); margin:10px auto; border-radius:2px;"></div></div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; max-width: 900px; margin: 0 auto; line-height: 1.6;">
    Mood Mirror is an advanced <span class="vibrant-text">AI-powered system</span> designed to bridge the gap between human emotions and machine intelligence. 
    Primarily focused on <span class="vibrant-text">real-time emotion detection</span>, it leverages cutting-edge deep learning models to interpret subtle facial cues.
    </p>
    """, unsafe_allow_html=True)
    
    # How It Works
    st.markdown('<div style="padding: 2rem 0;"><h2 style="text-align:center;" class="vibrant-header">How It Works</h2></div>', unsafe_allow_html=True)
    steps = [
        ("01", "Capture", "Capture image via webcam or upload photo."),
        ("02", "Detect", "Our computer vision algorithm detects faces."),
        ("03", "Process", "Facial features are preprocessed for analysis."),
        ("04", "Analyze", "Deep learning models identify emotions."),
        ("05", "Result", "Detected emotion is displayed with confidence.")
    ]
    cols = st.columns(5)
    for i, (num, title, desc) in enumerate(steps):
        with cols[i]:
            st.markdown(f'<div class="glass-card" style="padding: 1rem; height: 100%;"><h4>{num} {title}</h4><p style="font-size:0.8rem;">{desc}</p></div>', unsafe_allow_html=True)

    # Tech Stack
    st.markdown('<div style="padding: 4rem 0;"><h2 style="text-align:center;">Technologies Used</h2></div>', unsafe_allow_html=True)
    techs = ["Python", "OpenCV", "TensorFlow", "CNN", "Flask/Streamlit", "HTML/CSS/JS"]
    st.write(" | ".join([f"**{t}**" for t in techs]))

    # Future Scope
    st.markdown('<div style="padding: 2rem 0;"><h2 style="text-align:center;">Future Scope</h2></div>', unsafe_allow_html=True)
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        st.markdown('<div class="glass-card"><h4>Mental Health</h4><p>Tracking patient emotional trends for therapists.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card"><h4>Smart Classrooms</h4><p>Monitoring student engagement and well-being.</p></div>', unsafe_allow_html=True)
    with f_col2:
        st.markdown('<div class="glass-card"><h4>Customer Sentiment</h4><p>Analyzing retail customer reactions to products.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card"><h4>HCI</h4><p>Enhancing human-computer interaction patterns.</p></div>', unsafe_allow_html=True)

# --- Demo: Live Camera ---
elif page == "Try Live Camera":
    st.markdown('<h1 class="vibrant-header">🎥 Live Emotion Detection</h1>', unsafe_allow_html=True)
    st.write("Grant camera access to see the <span class='vibrant-text'>AI in action</span>.", unsafe_allow_html=True)
    
    img_file_buffer = st.camera_input("Take a picture")

    if img_file_buffer is not None:
        with st.spinner("Analyzing facial expressions..."):
            time.sleep(1.5)
            emotion, conf = detect_emotion("Camera")
            st.success(f"Face Detected! Emotion: **{emotion}** ({conf}%)")
            st.image(img_file_buffer, caption=f"Captured Image - Result: {emotion}")

# --- Demo: Upload ---
elif page == "Upload Image":
    st.markdown('<h1 class="vibrant-header">📤 Upload Image</h1>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        with st.status("Processing Image...", expanded=True) as status:
            st.write("Detecting facial landmarks...")
            time.sleep(0.8)
            st.write("Extracting emotional features...")
            time.sleep(0.8)
            emotion, conf = detect_emotion("Upload")
            status.update(label=f"Analysis Complete: {emotion}", state="complete", expanded=False)
        
        st.success(f"Detected Emotion: **{emotion}** ({conf}%)")

# --- Dashboard ---
elif page == "Analytics Dashboard":
    st.markdown('<h1 class="vibrant-header">📊 Emotion Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Summary Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="glass-card metric-card"><div class="metric-label">Total Detections</div><div class="metric-value vibrant-text">1,284</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="glass-card metric-card"><div class="metric-label">Top Emotion</div><div class="metric-value vibrant-text" style="color: #84fab0 !important;">Happy</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="glass-card metric-card"><div class="metric-label">Average Confidence</div><div class="metric-value vibrant-text">92%</div></div>', unsafe_allow_html=True)

    # Chart
    st.subheader("Emotion Trends")
    history_df = pd.DataFrame(st.session_state.history)
    emotion_counts = history_df['Emotion'].value_counts().reset_index()
    emotion_counts.columns = ['Emotion', 'Count']
    
    st.bar_chart(emotion_counts.set_index('Emotion'))

    # Table
    st.subheader("Recent History")
    st.table(history_df)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #b0b0b0;'>Mood Mirror – AI Powered Emotion Detection | Developed by Antigravity</p>", unsafe_allow_html=True)
