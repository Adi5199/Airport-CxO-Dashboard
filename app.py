"""
BIAL Airport Operations Dashboard - Main Application
GenAI-Powered Executive Dashboard for Airport Top Management
"""
import streamlit as st
import yaml
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.data_loader import DataLoader
from src.utils.calculations import MetricsCalculator
from src.ai.reasoning_engine import OperationsReasoningEngine
from src.ai.chatbot import AirportChatbot
from src.dashboard.components.filters import render_global_filters

# Page config
st.set_page_config(
    page_title="BIAL Operations Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
@st.cache_resource
def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Initialize data loader and AI components
@st.cache_resource
def initialize_components(_config):
    """Initialize all dashboard components"""
    data_loader = DataLoader()
    reasoning_engine = OperationsReasoningEngine(data_loader)
    chatbot = AirportChatbot(reasoning_engine, _config, provider="openai")
    return data_loader, reasoning_engine, chatbot

data_loader, reasoning_engine, chatbot = initialize_components(config)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<div class="main-header">✈️ BIAL Airport Operations Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">GenAI-Powered Executive Insights | Bangalore International Airport</div>', unsafe_allow_html=True)

# Global filters in sidebar
filters = render_global_filters(config)

# Display selected date range
st.sidebar.info(f"📅 **Viewing:** {filters['start_date'].strftime('%d %b %Y')} to {filters['end_date'].strftime('%d %b %Y')}")

# Navigation
st.sidebar.markdown("---")
st.sidebar.title("📊 Navigation")

page = st.sidebar.radio(
    "Select View",
    options=[
        "🏠 Executive Overview",
        "⏱️ Queue Compliance (Demo)",
        "🔒 Security & Operations",
        "💬 AI Insights Chat",
        "📈 Trends & Analytics"
    ],
    index=0
)

# Load the selected page
if page == "🏠 Executive Overview":
    from src.dashboard.pages import executive_overview
    executive_overview.render(data_loader, reasoning_engine, filters, config)

elif page == "⏱️ Queue Compliance (Demo)":
    from src.dashboard.pages import queue_compliance
    queue_compliance.render(data_loader, reasoning_engine, filters, config)

elif page == "🔒 Security & Operations":
    from src.dashboard.pages import security_operations
    security_operations.render(data_loader, reasoning_engine, filters, config)

elif page == "💬 AI Insights Chat":
    from src.dashboard.pages import ai_chat
    ai_chat.render(chatbot, data_loader, filters, config)

elif page == "📈 Trends & Analytics":
    from src.dashboard.pages import trends_analytics
    trends_analytics.render(data_loader, reasoning_engine, filters, config)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    <p><strong>BIAL Operations Dashboard</strong></p>
    <p>Powered by GenAI & Real-time Analytics</p>
    <p>© 2026 Bangalore International Airport</p>
</div>
""", unsafe_allow_html=True)
