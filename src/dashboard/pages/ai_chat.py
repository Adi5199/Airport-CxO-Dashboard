"""
AI Insights Chat Page - Conversational interface with the GenAI reasoning engine
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.ai.prompts import DEMO_PROMPTS


def render(chatbot, data_loader, filters, config):
    """Render the AI Chat page"""

    st.title("💬 AI Insights Chat")
    st.markdown("**Ask questions about airport operations and get AI-powered insights**")

    report_date = filters['report_date']

    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar: Quick Queries & Demo Prompts
    with st.sidebar:
        st.markdown("### 🚀 Demo Scenario Prompts")
        st.markdown("*Click to ask predefined questions for the demo use case:*")

        demo_buttons = {
            "1. Queue Compliance Drop": DEMO_PROMPTS['queue_compliance_analysis']['prompt'],
            "2. Drill to Terminal/Zone": DEMO_PROMPTS['drill_terminal_zone']['prompt'],
            "3. Airline Concentration": DEMO_PROMPTS['airline_concentration']['prompt'],
            "4. Security Lane Issues": DEMO_PROMPTS['security_lane_analysis']['prompt'],
            "5. Boarding Mode Impact": DEMO_PROMPTS['boarding_mode_correlation']['prompt'],
            "6. Customer Sentiment": DEMO_PROMPTS['customer_experience']['prompt'],
            "7. Get Recommendations": DEMO_PROMPTS['recommendations']['prompt']
        }

        selected_demo = None
        for button_label, prompt_text in demo_buttons.items():
            if st.button(button_label, use_container_width=True):
                selected_demo = prompt_text

        st.markdown("---")
        st.markdown("### 💡 Suggested Questions")
        quick_queries = chatbot.get_quick_queries()
        for query in quick_queries[:5]:
            if st.button(query, key=f"quick_{query[:20]}", use_container_width=True):
                selected_demo = query

        st.markdown("---")
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.chat_history = []
            chatbot.reset_conversation()
            st.rerun()

    # Info box
    st.info("""
🤖 **How to use:**
- Type your question in natural language
- Use the demo scenario prompts (sidebar) for guided analysis
- The AI will analyze operational data and provide contextual insights
- Ask follow-up questions to drill deeper

**Note:** If you haven't configured an OpenAI API key, the chatbot will use rule-based fallback analysis.
    """)

    # Check API key status
    import os
    api_key_status = "✅ Connected" if os.getenv("OPENAI_API_KEY") else "⚠️ Not configured (using fallback mode)"
    st.caption(f"**GenAI Status:** {api_key_status}")

    st.markdown("---")

    # Chat interface
    st.markdown("## 💭 Conversation")

    # Display chat history
    for message in st.session_state.chat_history:
        role = message['role']
        content = message['content']

        if role == 'user':
            st.markdown(f"""
<div style='background-color: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #2196f3;'>
    <strong>👤 You:</strong><br>{content}
</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div style='background-color: #f5f5f5; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #4caf50;'>
    <strong>🤖 AI Assistant:</strong><br>
</div>
            """, unsafe_allow_html=True)
            st.markdown(content)

    # Input area
    st.markdown("---")

    # If a demo button was clicked, set it as the query
    if selected_demo:
        user_query = selected_demo
        st.session_state.pending_query = user_query
    else:
        user_query = st.text_input(
            "Ask a question about airport operations:",
            placeholder="e.g., Why did queue compliance drop yesterday afternoon?",
            key="chat_input"
        )

    col1, col2 = st.columns([3, 1])

    with col1:
        submit_button = st.button("🚀 Ask AI", type="primary", use_container_width=True)

    with col2:
        if st.button("📊 Generate Summary", use_container_width=True):
            user_query = "Generate an executive summary of yesterday's operations"
            submit_button = True

    # Handle pending query from demo buttons
    if 'pending_query' in st.session_state:
        user_query = st.session_state.pending_query
        submit_button = True
        del st.session_state.pending_query

    # Process query
    if submit_button and user_query:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })

        # Get AI response
        with st.spinner("🤖 AI analyzing operational data..."):
            response = chatbot.chat(user_query, date=report_date)

        # Add AI response to history
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response
        })

        # Rerun to show updated conversation
        st.rerun()

    # Example queries section
    if len(st.session_state.chat_history) == 0:
        st.markdown("---")
        st.markdown("### 🎯 Example Questions to Get Started:")

        examples = [
            "What were the worst performing zones yesterday?",
            "Show me security lane reject rates",
            "Analyze peak hour patterns",
            "What's driving complaints at T2?",
            "Compare compliance across all checkpoints"
        ]

        for example in examples:
            st.markdown(f"• {example}")

        st.markdown("\n*Click any demo scenario button in the sidebar to start the guided analysis.*")

    # Export conversation
    if len(st.session_state.chat_history) > 0:
        st.markdown("---")
        conversation_text = "\n\n".join([
            f"{'User' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
            for msg in st.session_state.chat_history
        ])

        st.download_button(
            label="📥 Export Conversation",
            data=conversation_text,
            file_name=f"ai_chat_{report_date.strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
