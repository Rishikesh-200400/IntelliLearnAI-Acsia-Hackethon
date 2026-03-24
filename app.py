"""
IntelliLearn AI - Main Streamlit Application
AI-Driven Employee Skill Development Platform
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, get_db_context
from app.modules.data_collection import DataCollector
from app.modules.skill_gap_predictor import SkillGapPredictor
from app.modules.llm_assistant import LLMAssistant
from app.modules.recommender import HybridRecommender
from app.modules.analytics import AnalyticsEngine
from app.models.base import Employee, Course
from app.config import config

# Page configuration - Single Page App
st.set_page_config(
    page_title="IntelliLearn AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Sleek Futuristic Design
st.markdown("""
<style>
    /* Import Modern Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Root Variables */
    :root {
        --primary-blue: #2563eb;
        --primary-teal: #06b6d4;
        --primary-violet: #7c3aed;
        --primary-indigo: #4f46e5;
        --accent-bright: #f59e0b;
        --dark-bg: #0f172a;
        --dark-secondary: #1e293b;
        --light-bg: #f8fafc;
        --card-bg: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
        --shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
        --shadow-xl: 0 12px 48px rgba(0,0,0,0.16);
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Main Container with Gradient */
    .main {
        background: linear-gradient(135deg, #f1f5f9 0%, #e0e7ff 25%, #dbeafe 50%, #e0f2fe 75%, #f0f9ff 100%);
        background-attachment: fixed;
        padding: 0;
        min-height: 100vh;
    }
    
    .block-container {
        padding: 1.5rem 2.5rem;
        max-width: 1440px;
        animation: fadeIn 0.4s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Hide Sidebar */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Sticky Top Navbar */
    .top-navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
        padding: 0.75rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        animation: slideDown 0.4s ease-out;
    }
    
    @keyframes slideDown {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .navbar-logo {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Poppins', sans-serif;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .navbar-logo:hover {
        transform: scale(1.05);
    }
    
    .navbar-center {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .nav-tab {
        padding: 0.625rem 1.25rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.875rem;
        color: #64748b;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        background: transparent;
        text-decoration: none;
    }
    
    .nav-tab:hover {
        background: rgba(59, 130, 246, 0.08);
        color: #2563eb;
        border-color: rgba(59, 130, 246, 0.2);
    }
    
    .nav-tab.active {
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    .navbar-right {
        display: flex;
        gap: 0.75rem;
        align-items: center;
    }
    
    .nav-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
        background: rgba(0, 0, 0, 0.03);
        color: #64748b;
        font-size: 1.125rem;
    }
    
    .nav-icon:hover {
        background: rgba(59, 130, 246, 0.1);
        color: #2563eb;
        transform: scale(1.1);
    }
    
    /* Adjust main content padding */
    .main .block-container {
        padding-top: 5rem !important;
    }
    
    /* Modern Header */
    .main-header {
        font-family: 'Poppins', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        animation: fadeInDown 0.6s ease-out;
    }
    
    .sub-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.25rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Premium Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.95) 100%);
        backdrop-filter: blur(20px);
        padding: 1.75rem;
        border-radius: 20px;
        margin: 0.75rem 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid rgba(255,255,255,0.8);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #06b6d4 0%, #3b82f6 50%, #7c3aed 100%);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(37,99,235,0.15), 0 4px 16px rgba(0,0,0,0.08);
        border-color: rgba(37,99,235,0.2);
    }
    
    /* Modern Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.01em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(37,99,235,0.3), 0 2px 8px rgba(37,99,235,0.2);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(37,99,235,0.4), 0 4px 12px rgba(37,99,235,0.3);
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Glassmorphic Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
        backdrop-filter: blur(20px);
        padding: 1.75rem 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 8px 32px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.8);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 16px 48px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.9);
        border-color: rgba(59,130,246,0.3);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Poppins', sans-serif;
        letter-spacing: -0.02em;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: #475569;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    
    /* Info & Success Boxes */
    .stAlert {
        background: linear-gradient(135deg, rgba(6,182,212,0.08) 0%, rgba(59,130,246,0.08) 100%);
        border-left: 4px solid #06b6d4;
        border-radius: 12px;
        padding: 1.25rem;
        backdrop-filter: blur(10px);
        animation: slideInLeft 0.4s ease-out;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif;
        color: #1e293b;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    
    h1 { font-size: 2.25rem; margin-bottom: 1rem; }
    h2 { font-size: 1.875rem; margin-bottom: 0.875rem; }
    h3 { font-size: 1.5rem; margin-bottom: 0.75rem; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255,255,255,0.6);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 0.5rem;
        border: 1px solid rgba(226,232,240,0.8);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #64748b;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 0.875rem 1.25rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 4px rgba(37,99,235,0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.9) 100%);
        border-radius: 12px;
        font-weight: 600;
        color: #1e293b;
        padding: 1rem 1.25rem;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #2563eb;
        box-shadow: 0 4px 12px rgba(37,99,235,0.1);
    }
    
    /* Data Tables */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        font-weight: 600;
        padding: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(37,99,235,0.05);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #06b6d4 0%, #2563eb 50%, #7c3aed 100%);
        border-radius: 8px;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #2563eb !important;
        border-right-color: #06b6d4 !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #0891b2 100%);
    }
    
    /* Mobile Responsive Design */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.75rem;
        }
        
        .main-header {
            font-size: 2rem;
        }
        
        .sub-header {
            font-size: 0.95rem;
        }
        
        [data-testid="stMetric"] {
            padding: 1.25rem 1rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem;
        }
        
        section[data-testid="stSidebar"] {
            width: 240px !important;
        }
    }
    
    /* Tablet Responsive */
    @media (min-width: 769px) and (max-width: 1024px) {
        .block-container {
            padding: 1.5rem 1.5rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2.25rem;
        }
    }
    
    /* Smooth Animations */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 20px rgba(59,130,246,0.3);
        }
        50% {
            box-shadow: 0 0 30px rgba(59,130,246,0.5);
        }
    }
    
    /* Feature Card Styles */
    .feature-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        backdrop-filter: blur(16px);
        border-radius: 24px;
        padding: 2rem;
        border: 1px solid rgba(255,255,255,0.3);
        box-shadow: 0 8px 32px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .feature-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(0,0,0,0.1);
        border-color: rgba(59,130,246,0.2);
    }
    
    /* Smooth Scroll */
    html {
        scroll-behavior: smooth;
    }
    
    .page-section {
        min-height: 90vh;
        padding: 3rem 0;
        animation: fadeInSection 0.6s ease-out;
        scroll-margin-top: 80px;
    }
    
    @keyframes fadeInSection {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Back to Top Button */
    .back-to-top {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.4);
        transition: all 0.3s ease;
        z-index: 9998;
        font-size: 1.5rem;
        animation: bounceIn 0.5s ease-out;
        text-decoration: none;
    }
    
    .back-to-top:hover {
        transform: translateY(-5px) scale(1.1);
        box-shadow: 0 12px 32px rgba(37, 99, 235, 0.5);
    }
    
    @keyframes bounceIn {
        0% { transform: scale(0); opacity: 0; }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .top-navbar {
            padding: 0.5rem 1rem;
        }
        
        .navbar-center {
            display: none;
        }
        
        .navbar-logo {
            font-size: 1.25rem;
        }
        
        .nav-icon {
            width: 32px;
            height: 32px;
            font-size: 1rem;
        }
        
        .page-section {
            min-height: auto;
            padding: 2rem 0;
        }
    }
    
    /* Home Page Animations */
    @keyframes fadeInScale {
        0% {
            opacity: 0;
            transform: scale(0.8) translateX(-50px);
        }
        100% {
            opacity: 1;
            transform: scale(1) translateX(0);
        }
    }
    
    @keyframes gradientShift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-20px);
        }
    }
    
    @keyframes fadeInUp {
        0% {
            opacity: 0;
            transform: translateY(30px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .home-hero {
        min-height: 85vh !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        padding-right: 8% !important;
    }
    
    .home-content {
        text-align: right !important;
        max-width: 700px !important;
    }
    
    .home-icon {
        font-size: 1.5rem !important;
        color: #64748b !important;
        margin-bottom: 1.5rem !important;
        font-weight: 500 !important;
        animation: float 3s ease-in-out infinite !important;
    }
    
    .home-title {
        font-size: 6.5rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 25%, #7c3aed 50%, #ec4899 75%, #f59e0b 100%) !important;
        background-size: 200% 200% !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin: 0 !important;
        letter-spacing: -0.04em !important;
        animation: fadeInScale 1.2s ease-out, gradientShift 8s ease infinite !important;
        line-height: 1.1 !important;
    }
    
    .home-description {
        font-size: 1.5rem !important;
        color: #64748b !important;
        margin-top: 1.5rem !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        animation: fadeInUp 1.5s ease-out !important;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'db_initialized' not in st.session_state:
        st.session_state.db_initialized = False
    if 'selected_employee' not in st.session_state:
        st.session_state.selected_employee = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def initialize_database():
    """Initialize database and create tables"""
    try:
        init_db()
        st.session_state.db_initialized = True
        return True
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return False


def main():
    """Main single-page application with top navbar"""
    init_session_state()
    
    # Initialize database if not done
    if not st.session_state.db_initialized:
        with st.spinner("Initializing database..."):
            initialize_database()
    
    # Top Navigation Bar with inline styles
    st.markdown("""
    <style>
        .main-navbar {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            z-index: 999999 !important;
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(20px) !important;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08) !important;
            padding: 0.75rem 2rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
        }
        .navbar-brand {
            font-size: 1.5rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            font-family: 'Poppins', sans-serif !important;
        }
        .navbar-links {
            display: flex !important;
            gap: 0.5rem !important;
            align-items: center !important;
        }
        .navbar-links a {
            padding: 0.625rem 1.25rem !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            color: #64748b !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
        }
        .navbar-links a:hover {
            background: rgba(59, 130, 246, 0.1) !important;
            color: #2563eb !important;
        }
        .navbar-icons {
            display: flex !important;
            gap: 0.75rem !important;
        }
        .navbar-icon {
            width: 36px !important;
            height: 36px !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: rgba(0, 0, 0, 0.03) !important;
            font-size: 1.125rem !important;
        }
        .back-top-btn {
            position: fixed !important;
            bottom: 2rem !important;
            right: 2rem !important;
            width: 50px !important;
            height: 50px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%) !important;
            color: white !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.4) !important;
            z-index: 99999 !important;
            font-size: 1.5rem !important;
            text-decoration: none !important;
        }
    </style>
    
    <div class="main-navbar">
        <div class="navbar-brand">🎓 IntelliLearn AI</div>
        <div class="navbar-links">
            <a href="#home">Home</a>
            <a href="#employees">Employees</a>
            <a href="#ai-assistant">AI Assistant</a>
            <a href="#courses">Courses</a>
            <a href="#analytics">Analytics</a>
            <a href="#admin">Admin</a>
        </div>
        <div class="navbar-icons">
            <div class="navbar-icon">⚙️</div>
            <div class="navbar-icon">🌙</div>
            <div class="navbar-icon">👤</div>
        </div>
    </div>
    
    <a href="#home" class="back-top-btn">↑</a>
    """, unsafe_allow_html=True)
    
    # Single Page with Scrollable Sections
    # Section 1: Home
    show_home_page()
    
    # Section 2: Employee Dashboard
    show_employee_dashboard()
    
    # Section 3: AI Assistant
    show_ai_assistant()
    
    # Section 4: Course Recommendations
    show_recommendations()
    
    # Section 5: Analytics
    show_analytics()
    
    # Section 6: Admin Panel
    show_admin_panel()


def show_home_page():
    """Minimal animated home page with project name"""
    
    # Animated hero section - right middle with description
    st.markdown("""
    <div id='home' class='home-hero'>
        <div class='home-content'>
            <div class='home-icon'>🎓</div>
            <h1 class='home-title'>IntelliLearn AI</h1>
            <p class='home-description'>AI-Powered Employee Skill<br/>Development & Training Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_employee_dashboard():
    """Employee-specific dashboard"""
    st.markdown("""
    <div id='employees' style='text-align: center; padding: 2rem 0 1.5rem 0;'>
        <h2 style='font-size: 2.5rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;'>👤 Employee Dashboard</h2>
        <p style='color: #64748b; font-size: 1.125rem;'>View and manage employee skills and progress</p>
    </div>
    """, unsafe_allow_html=True)
    
    with get_db_context() as db:
        # Employee selection
        employees = db.query(Employee).all()
        
        if not employees:
            st.warning("No employees found. Please add employees in the Admin Panel.")
            return
        
        employee_options = {f"{emp.name} ({emp.employee_id})": emp.id for emp in employees}
        selected_name = st.selectbox("Select Employee", list(employee_options.keys()), key="employee_dashboard_select")
        employee_id = employee_options[selected_name]
        
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        # Employee info
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Name", employee.name)
        with col2:
            st.metric("Role", employee.role or "N/A")
        with col3:
            st.metric("Department", employee.department or "N/A")
        with col4:
            st.metric("Experience", f"{employee.years_of_experience or 0} years")
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["Skills Overview", "Skill Gaps", "Training Progress"])
        
        with tab1:
            show_skills_overview(db, employee_id)
        
        with tab2:
            show_skill_gaps(db, employee_id)
        
        with tab3:
            show_training_progress(db, employee_id)


def show_skills_overview(db, employee_id):
    """Display employee skills"""
    from app.models.base import EmployeeSkill
    
    skills = db.query(EmployeeSkill).filter(
        EmployeeSkill.employee_id == employee_id
    ).all()
    
    if not skills:
        st.info("No skills recorded for this employee yet.")
        return
    
    # Create DataFrame
    skill_data = [{
        'Skill': s.skill.name,
        'Category': s.skill.category,
        'Proficiency': s.proficiency_level,
        'Last Assessed': s.last_assessed.strftime('%Y-%m-%d') if s.last_assessed else 'N/A'
    } for s in skills]
    
    df = pd.DataFrame(skill_data)
    
    # Visualization
    fig = px.bar(
        df.sort_values('Proficiency', ascending=True),
        x='Proficiency',
        y='Skill',
        orientation='h',
        color='Category',
        title='Skill Proficiency Levels',
        labels={'Proficiency': 'Proficiency Level (0-10)'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.dataframe(df, use_container_width=True)


def show_skill_gaps(db, employee_id):
    """Display skill gaps"""
    from app.models.base import SkillGapPrediction
    
    gaps = db.query(SkillGapPrediction).filter(
        SkillGapPrediction.employee_id == employee_id,
        SkillGapPrediction.is_active == True
    ).order_by(SkillGapPrediction.gap_score.desc()).all()
    
    if not gaps:
        # Try to predict gaps
        if st.button("🔮 Predict Skill Gaps", key="predict_skill_gaps_btn"):
            with st.spinner("Analyzing skill gaps..."):
                try:
                    predictor = SkillGapPredictor()
                    predictor.load_models()
                    predicted_gaps = predictor.predict_skill_gaps(db, employee_id)
                    
                    if predicted_gaps:
                        predictor.save_predictions_to_db(db, employee_id, predicted_gaps)
                        st.success(f"Identified {len(predicted_gaps)} skill gaps!")
                        st.rerun()
                    else:
                        st.info("No significant skill gaps identified.")
                except Exception as e:
                    st.warning(f"Unable to predict skill gaps: {e}. Please train the model first.")
        return
    
    # Display gaps
    gap_data = [{
        'Skill': g.skill_name,
        'Current Level': g.current_level,
        'Required Level': g.required_level,
        'Gap Score': g.gap_score,
        'Priority': g.priority,
        'Confidence': f"{g.confidence_score:.2f}"
    } for g in gaps]
    
    df = pd.DataFrame(gap_data)
    
    # Priority breakdown
    col1, col2, col3 = st.columns(3)
    high = len([g for g in gaps if g.priority == 'High'])
    medium = len([g for g in gaps if g.priority == 'Medium'])
    low = len([g for g in gaps if g.priority == 'Low'])
    
    with col1:
        st.metric("High Priority", high, delta=None, delta_color="inverse")
    with col2:
        st.metric("Medium Priority", medium)
    with col3:
        st.metric("Low Priority", low)
    
    # Visualization
    fig = px.scatter(
        df,
        x='Current Level',
        y='Required Level',
        size='Gap Score',
        color='Priority',
        hover_data=['Skill'],
        title='Skill Gap Analysis',
        color_discrete_map={'High': 'red', 'Medium': 'orange', 'Low': 'green'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.dataframe(df, use_container_width=True)


def show_training_progress(db, employee_id):
    """Display training progress"""
    from app.models.base import Training
    
    trainings = db.query(Training).filter(
        Training.employee_id == employee_id
    ).order_by(Training.enrollment_date.desc()).all()
    
    if not trainings:
        st.info("No training records found.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(trainings)
    completed = sum(1 for t in trainings if t.status == 'Completed')
    in_progress = sum(1 for t in trainings if t.status == 'In Progress')
    avg_score = sum(t.assessment_score for t in trainings if t.assessment_score) / max(completed, 1) if completed > 0 else 0
    
    with col1:
        st.metric("Total Trainings", total)
    with col2:
        st.metric("Completed", completed)
    with col3:
        st.metric("In Progress", in_progress)
    with col4:
        st.metric("Avg Assessment Score", f"{avg_score:.1f}/100")
    
    # Training list
    training_data = [{
        'Course': t.course.title if t.course else 'N/A',
        'Status': t.status,
        'Enrolled': t.enrollment_date.strftime('%Y-%m-%d') if t.enrollment_date else 'N/A',
        'Completed': t.completion_date.strftime('%Y-%m-%d') if t.completion_date else 'N/A',
        'Progress': f"{t.progress_percentage}%",
        'Score': t.assessment_score if t.assessment_score else 'N/A'
    } for t in trainings]
    
    df = pd.DataFrame(training_data)
    st.dataframe(df, use_container_width=True)


def show_ai_assistant():
    """AI Learning Assistant chatbot"""
    st.markdown("""
    <div id='ai-assistant' style='text-align: center; padding: 2rem 0 1.5rem 0;'>
        <h2 style='font-size: 2.5rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;'>💬 AI Learning Assistant</h2>
        <p style='color: #64748b; font-size: 1.125rem;'>Ask me anything about your learning path, skill gaps, or career development</p>
    </div>
    """, unsafe_allow_html=True)
    
    with get_db_context() as db:
        # Employee selection
        employees = db.query(Employee).all()
        
        if not employees:
            st.warning("No employees found. Please add employees in the Admin Panel.")
            return
        
        employee_options = {f"{emp.name} ({emp.employee_id})": emp.id for emp in employees}
        selected_name = st.selectbox("Select Employee", list(employee_options.keys()), key="ai_assistant_select")
        employee_id = employee_options[selected_name]
        
        st.markdown("---")
        
        # Chat interface
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # Chat input
        user_input = st.chat_input("Ask me anything...")
        
        if user_input:
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.spinner("Thinking..."):
                try:
                    assistant = LLMAssistant(db)
                    response = assistant.chat(employee_id, user_input)
                    
                    answer = response.get('answer', response.get('fallback_answer', 'I apologize, but I encountered an issue. Please try again.'))
                    
                    # Add assistant message
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Quick actions
        st.markdown("---")
        st.subheader("Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Get Personalized Guidance", key="get_guidance_btn"):
                try:
                    assistant = LLMAssistant(db)
                    guidance = assistant.get_personalized_guidance(employee_id)
                    
                    st.markdown("### 📋 Your Personalized Learning Guidance")
                    st.write(guidance.get('recommendations', ''))
                    
                    if guidance.get('learning_path'):
                        st.markdown("### 🗺️ Recommended Learning Path")
                        for phase in guidance['learning_path']:
                            with st.expander(f"Phase {phase['phase']}: {phase['name']}"):
                                st.write(f"**Duration**: {phase['duration_weeks']} weeks")
                                st.write(f"**Focus**: {phase['focus']}")
                                st.write(f"**Skills**: {', '.join(phase['skills'])}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            if st.button("🔄 Clear Chat History", key="clear_chat_btn"):
                st.session_state.chat_history = []
                st.rerun()


def show_recommendations():
    """Course recommendations page"""
    st.markdown("""
    <div id='courses' style='text-align: center; padding: 2rem 0 1.5rem 0;'>
        <h2 style='font-size: 2.5rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;'>📚 Course Recommendations</h2>
        <p style='color: #64748b; font-size: 1.125rem;'>AI-powered personalized course suggestions for skill development</p>
    </div>
    """, unsafe_allow_html=True)
    
    with get_db_context() as db:
        # Employee selection
        employees = db.query(Employee).all()
        
        if not employees:
            st.warning("No employees found.")
            return
        
        employee_options = {f"{emp.name} ({emp.employee_id})": emp.id for emp in employees}
        selected_name = st.selectbox("Select Employee", list(employee_options.keys()), key="recommendations_select")
        employee_id = employee_options[selected_name]
        
        # Number of recommendations
        top_n = st.slider("Number of recommendations", 5, 20, 10, key="recommendations_slider")
        
        if st.button("🔍 Generate Recommendations", key="generate_recommendations_btn"):
            with st.spinner("Analyzing and generating recommendations..."):
                try:
                    recommender = HybridRecommender(db)
                    recommendations = recommender.get_recommendations(
                        employee_id, 
                        top_n=top_n,
                        include_reasoning=True
                    )
                    
                    if not recommendations:
                        st.info("No recommendations available. Please ensure courses and skills are loaded.")
                        return
                    
                    st.success(f"Generated {len(recommendations)} personalized recommendations!")
                    
                    # Display recommendations
                    for i, rec in enumerate(recommendations, 1):
                        with st.expander(f"{i}. {rec['course_title']} ({rec['difficulty_level']})"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Provider**: {rec['provider']}")
                                st.write(f"**Category**: {rec['category']}")
                                st.write(f"**Duration**: {rec['duration_hours']} hours")
                                st.write(f"**Rating**: {'⭐' * int(rec['rating'] or 0)}")
                                
                                if rec.get('reasoning'):
                                    st.markdown("**Why this course?**")
                                    st.write(rec['reasoning'])
                            
                            with col2:
                                st.metric("Match Score", f"{rec['recommendation_score']:.2f}")
                                
                                if rec.get('url'):
                                    st.markdown(f"[🔗 View Course]({rec['url']})")
                    
                    # Learning path
                    st.markdown("---")
                    st.subheader("🗺️ Structured Learning Path")
                    
                    learning_path = recommender.get_learning_path(employee_id)
                    
                    for stage in learning_path:
                        with st.expander(f"Stage: {stage['stage']} ({stage['level']})"):
                            st.write(f"**Estimated Duration**: {stage['estimated_duration_weeks']:.1f} weeks")
                            st.write(f"**Courses**: {len(stage['courses'])}")
                            
                            for course in stage['courses']:
                                st.write(f"- {course['course_title']}")
                    
                except Exception as e:
                    st.error(f"Error generating recommendations: {e}")


def show_analytics():
    """Analytics and ROI dashboard"""
    st.markdown("""
    <div id='analytics' style='text-align: center; padding: 2rem 0 1.5rem 0;'>
        <h2 style='font-size: 2.5rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;'>📊 Analytics & ROI</h2>
        <p style='color: #64748b; font-size: 1.125rem;'>Track training effectiveness and return on investment</p>
    </div>
    """, unsafe_allow_html=True)
    
    with get_db_context() as db:
        analytics = AnalyticsEngine(db)
        
        # Tabs for different analytics
        tab1, tab2, tab3, tab4 = st.tabs([
            "Workforce Readiness",
            "Training ROI",
            "Department Comparison",
            "Trends"
        ])
        
        with tab1:
            show_workforce_readiness(analytics)
        
        with tab2:
            show_training_roi(analytics)
        
        with tab3:
            show_department_comparison(analytics)
        
        with tab4:
            show_trends(analytics)


def show_workforce_readiness(analytics):
    """Workforce readiness metrics"""
    st.subheader("Workforce Readiness Analysis")
    
    readiness = analytics.calculate_workforce_readiness()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Readiness", f"{readiness['readiness_score']:.1f}/10")
    with col2:
        st.metric("Total Employees", readiness['total_employees'])
    with col3:
        st.metric("Avg Skill Coverage", f"{readiness['avg_skill_coverage']:.1f}%")
    
    # Distribution
    dist = readiness['distribution']
    
    fig = go.Figure(data=[go.Pie(
        labels=['High Readiness', 'Medium Readiness', 'Low Readiness'],
        values=[dist['high_readiness'], dist['medium_readiness'], dist['low_readiness']],
        marker_colors=['green', 'orange', 'red']
    )])
    
    fig.update_layout(title="Readiness Distribution")
    st.plotly_chart(fig, use_container_width=True)


def show_training_roi(analytics):
    """Training ROI metrics"""
    st.subheader("Training ROI Analysis")
    
    period = st.selectbox("Time Period", [30, 60, 90, 180, 365], key="training_roi_period")
    
    roi = analytics.calculate_training_roi(time_period_days=period)
    
    if roi['total_trainings'] == 0:
        st.info("No training data available for the selected period.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("ROI", f"{roi['roi_percentage']:.1f}%")
    with col2:
        st.metric("Total Cost", f"${roi['total_cost']:,.0f}")
    with col3:
        st.metric("Estimated Benefit", f"${roi['estimated_benefit']:,.0f}")
    with col4:
        st.metric("Trainings", roi['total_trainings'])
    
    # Details
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Employees Trained", roi['employees_trained'])
        st.metric("Avg Skill Improvement", f"{roi['avg_skill_improvement']:.2f} points")
    
    with col2:
        st.metric("Total Training Hours", f"{roi['total_training_hours']:.0f} hours")
        st.metric("Avg Performance Improvement", f"{roi['avg_performance_improvement']:.1f}%")


def show_department_comparison(analytics):
    """Department comparison"""
    st.subheader("Department Comparison")
    
    comparison = analytics.get_department_comparison()
    
    if not comparison:
        st.info("No department data available.")
        return
    
    df = pd.DataFrame(comparison)
    
    fig = px.bar(
        df,
        x='department',
        y='readiness_score',
        color='readiness_score',
        title='Readiness Score by Department',
        labels={'readiness_score': 'Readiness Score', 'department': 'Department'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df, use_container_width=True)


def show_trends(analytics):
    """Skill gap trends"""
    st.subheader("Skill Gap Trends")
    
    trends_data = analytics.get_skill_gap_trends(time_periods=6)
    
    if not trends_data['trends']:
        st.info("No trend data available.")
        return
    
    df = pd.DataFrame(trends_data['trends'])
    
    fig = px.line(
        df,
        x='period',
        y='avg_gap_score',
        markers=True,
        title='Average Skill Gap Score Over Time'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # High priority trends
    fig2 = px.bar(
        df,
        x='period',
        y='high_priority_count',
        title='High Priority Skill Gaps Over Time'
    )
    
    st.plotly_chart(fig2, use_container_width=True)


def show_admin_panel():
    """Admin panel for data management"""
    st.markdown("""
    <div id='admin' style='text-align: center; padding: 2rem 0 1.5rem 0;'>
        <h2 style='font-size: 2.5rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;'>⚙️ Admin Panel</h2>
        <p style='color: #64748b; font-size: 1.125rem;'>Manage data, load samples, and train models</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Data Import", "Model Training", "System Info"])
    
    with tab1:
        show_data_import()
    
    with tab2:
        show_model_training()
    
    with tab3:
        show_system_info()


def show_data_import():
    """Data import interface"""
    st.subheader("Data Import")
    
    st.info("Click the button below to automatically load all sample data into the system.")
    
    # Show data summary
    with get_db_context() as db:
        collector = DataCollector()
        summary = collector.get_employee_data_summary(db)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Employees", summary['total_employees'])
        with col2:
            st.metric("Skills", summary['total_skills'])
        with col3:
            st.metric("Courses", summary['total_courses'])
        with col4:
            st.metric("Trainings", summary['total_trainings'])
        with col5:
            st.metric("Avg Skills/Emp", f"{summary['avg_skills_per_employee']:.1f}")
    
    st.markdown("---")
    
    if st.button("📊 Load Sample Data", type="primary", key="load_sample_data_btn"):
        with st.spinner("Loading sample data... Please wait."):
            try:
                collector = DataCollector()
                
                # Define sample data paths
                sample_dir = Path("data/sample")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Import in order
                total_imported = 0
                
                # 1. Employees
                status_text.text("Importing employees...")
                progress_bar.progress(0.2)
                count = collector.import_employees_from_csv(str(sample_dir / "employees.csv"))
                total_imported += count
                st.success(f"✅ Imported {count} employees")
                
                # 2. Skills
                status_text.text("Importing skills...")
                progress_bar.progress(0.4)
                count = collector.import_skills_from_csv(str(sample_dir / "skills.csv"))
                total_imported += count
                st.success(f"✅ Imported {count} skills")
                
                # 3. Employee Skills
                status_text.text("Importing employee skills...")
                progress_bar.progress(0.6)
                count = collector.import_employee_skills_from_csv(str(sample_dir / "employee_skills.csv"))
                total_imported += count
                st.success(f"✅ Imported {count} employee skill records")
                
                # 4. Courses
                status_text.text("Importing courses...")
                progress_bar.progress(0.8)
                count = collector.import_courses_from_csv(str(sample_dir / "courses.csv"))
                total_imported += count
                st.success(f"✅ Imported {count} courses")
                
                # 5. Training History
                status_text.text("Importing training history...")
                progress_bar.progress(1.0)
                count = collector.import_training_history_from_csv(str(sample_dir / "training_history.csv"))
                total_imported += count
                st.success(f"✅ Imported {count} training records")
                
                status_text.empty()
                progress_bar.empty()
                
                st.balloons()
                st.success(f"🎉 Successfully imported {total_imported} total records!")
                st.info("💡 Next step: Go to 'Model Training' tab to train the ML models.")
                
                # Refresh the page to show updated metrics
                st.rerun()
                
            except Exception as e:
                st.error(f"Import error: {e}")
                st.exception(e)


def show_model_training():
    """Model training interface"""
    st.subheader("Model Training")
    
    st.write("Train the skill gap prediction models using the available data.")
    
    if st.button("🚀 Train Models", key="train_models_btn"):
        with st.spinner("Training models... This may take a few minutes."):
            try:
                with get_db_context() as db:
                    predictor = SkillGapPredictor()
                    results = predictor.train_models(db)
                    
                    if results['status'] == 'success':
                        st.success("Models trained successfully!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### Random Forest")
                            st.metric("R² Score", f"{results['random_forest']['r2_score']:.3f}")
                            st.metric("RMSE", f"{results['random_forest']['rmse']:.3f}")
                        
                        with col2:
                            st.markdown("### XGBoost")
                            st.metric("R² Score", f"{results['xgboost']['r2_score']:.3f}")
                            st.metric("RMSE", f"{results['xgboost']['rmse']:.3f}")
                        
                        st.info(f"Training samples: {results['training_samples']}, Test samples: {results['test_samples']}")
                    else:
                        st.warning(f"Training skipped: {results['status']}")
                        
            except Exception as e:
                st.error(f"Training error: {e}")


def show_system_info():
    """System information"""
    st.subheader("System Information")
    
    with get_db_context() as db:
        collector = DataCollector()
        summary = collector.get_employee_data_summary(db)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Employees", summary['total_employees'])
            st.metric("Total Skills", summary['total_skills'])
            st.metric("Total Courses", summary['total_courses'])
        
        with col2:
            st.metric("Total Trainings", summary['total_trainings'])
            st.metric("Avg Skills per Employee", f"{summary['avg_skills_per_employee']:.1f}")
    
    st.markdown("---")
    
    st.markdown("### Configuration")
    st.write(f"**App Name**: {config.APP_NAME}")
    st.write(f"**Version**: {config.APP_VERSION}")
    st.write(f"**LLM Provider**: {config.LLM_PROVIDER}")
    st.write(f"**Embedding Model**: {config.EMBEDDING_MODEL}")


if __name__ == "__main__":
    main()
