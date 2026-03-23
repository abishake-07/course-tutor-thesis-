"""
Streamlit frontend for the Course Tutor System
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import yaml

from core import CourseTutor, TutorLogger

# Page config
st.set_page_config(
    page_title="Data Science Course Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .stats-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    /* Make chat input always visible at bottom */
    .stChatInput {
        position: sticky;
        bottom: 0;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'tutor' not in st.session_state:
        st.session_state.tutor = CourseTutor("config.yaml")
    
    if 'logger' not in st.session_state:
        st.session_state.logger = TutorLogger(
            log_dir="logs/streamlit_sessions",
            session_id=f"streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'interaction_count' not in st.session_state:
        st.session_state.interaction_count = 0
    
    if 'blocked_count' not in st.session_state:
        st.session_state.blocked_count = 0


def display_chat_history():
    """Display chat history"""
    if not st.session_state.messages:
        st.info("Welcome! Ask me anything about data science, Python, pandas, machine learning, or submit code for review.")
        return
    
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.write(msg['content'])
        else:
            with st.chat_message("assistant"):
                st.write(msg['content'])
                
                # Show defense info if blocked or defenses applied
                if msg.get('blocked', False):
                    st.warning("This message was blocked by security defenses")
                
                if msg.get('defense_log') and msg['defense_log'].get('defenses_applied'):
                    with st.expander("Defense Details"): 
                        st.json(msg['defense_log'])


def save_conversation_history():
    """Save conversation to file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    history_dir = Path("logs/streamlit_sessions/conversations")
    history_dir.mkdir(parents=True, exist_ok=True)
    
    history_file = history_dir / f"conversation_{timestamp}.json"
    
    with open(history_file, 'w') as f:
        json.dump({
            "session_id": st.session_state.logger.session_id,
            "timestamp": timestamp,
            "messages": st.session_state.messages,
            "stats": {
                "total_interactions": st.session_state.interaction_count,
                "blocked_interactions": st.session_state.blocked_count
            }
        }, f, indent=2)
    
    return str(history_file)


def main():  
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">Data Science Course Tutor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI Teaching Assistant for DS101</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # Defense controls
        st.subheader("Security Defenses")
        defenses_cfg = st.session_state.tutor.config.get('defenses', {})
        
        defenses_enabled = st.checkbox(
            "Enable Defenses",
            value=defenses_cfg.get('enabled', True),
            help="Master switch for all defense mechanisms"
        )
        
        delimiter_isolation = st.checkbox(
            "Delimiter Isolation",
            value=defenses_cfg.get('delimiter_isolation', True),
            disabled=not defenses_enabled,
            help="Wrap user input in XML delimiters"
        )
        
        pdf_sanitization = st.checkbox(
            "PDF Sanitization",
            value=defenses_cfg.get('pdf_sanitization', True),
            disabled=not defenses_enabled,
            help="Remove metadata and suspicious content from PDFs"
        )
        
        prompt_detection = st.checkbox(
            "Prompt Injection Detection",
            value=defenses_cfg.get('prompt_injection_detection', True),
            disabled=not defenses_enabled,
            help="Detect and block injection attempts"
        )

        trigger_detection = st.checkbox(
            "Trigger Phrase Detection",
            value=defenses_cfg.get('trigger_phrase_detection', True),
            disabled=not defenses_enabled,
            help="Fast phrase-level blocking for known jailbreak patterns"
        )

        text_normalization = st.checkbox(
            "Text Normalization",
            value=defenses_cfg.get('text_normalization', True),
            disabled=not defenses_enabled,
            help="Normalize formatting and remove common obfuscation markers"
        )

        semantic_detection = st.checkbox(
            "Semantic Risk Detection",
            value=defenses_cfg.get('semantic_risk_detection', True),
            disabled=not defenses_enabled,
            help="Weighted multi-signal risk scoring for attacks that evade exact rules"
        )

        semantic_block_threshold = st.slider(
            "Semantic Block Threshold",
            min_value=0.50,
            max_value=1.00,
            step=0.05,
            value=float(defenses_cfg.get('semantic_block_threshold', 0.70)),
            disabled=not defenses_enabled or not semantic_detection,
            help="Messages with semantic risk score >= this value are blocked"
        )

        semantic_review_threshold = st.slider(
            "Semantic Review Threshold",
            min_value=0.20,
            max_value=0.95,
            step=0.05,
            value=float(defenses_cfg.get('semantic_review_threshold', 0.45)),
            disabled=not defenses_enabled or not semantic_detection,
            help="Messages above this score are flagged in defense logs"
        )
        
        # Update defense config
        if st.button("Apply Defense Settings"):
            st.session_state.tutor.config['defenses'] = {
                'enabled': defenses_enabled,
                'delimiter_isolation': delimiter_isolation,
                'pdf_sanitization': pdf_sanitization,
                'prompt_injection_detection': prompt_detection,
                'trigger_phrase_detection': trigger_detection,
                'text_normalization': text_normalization,
                'semantic_risk_detection': semantic_detection,
                'semantic_block_threshold': semantic_block_threshold,
                'semantic_review_threshold': semantic_review_threshold
            }
            from core import DefenseManager
            st.session_state.tutor.defense_manager = DefenseManager(
                st.session_state.tutor.config['defenses']
            )
            st.success("Defense settings updated")
        
        st.divider()
        
        # Session stats
        st.subheader("Session Statistics")
        st.markdown(f"""
        <div class="stats-box">
            <strong>Interactions:</strong> {st.session_state.interaction_count}<br>
            <strong>Blocked:</strong> {st.session_state.blocked_count}<br>
            <strong>Session ID:</strong> {st.session_state.logger.session_id[:20]}...
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Actions
        st.subheader("Actions")
        
        if st.button("Save Conversation"):
            file_path = save_conversation_history()
            st.success(f"Saved to: {Path(file_path).name}")
        
        if st.button("Reset Session"):
            st.session_state.tutor.reset_session()
            st.session_state.messages = []
            st.session_state.interaction_count = 0
            st.session_state.blocked_count = 0
            st.session_state.logger = TutorLogger(
                log_dir="logs/streamlit_sessions",
                session_id=f"streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            st.rerun()
        
        if st.button("View Logs"):
            st.session_state.show_logs = True
        
        st.divider()
        
        # Model info
        st.subheader("Model Configuration")
        st.info(f"""
        **Provider:** {st.session_state.tutor.config['model']['provider']}  
        **Model:** {st.session_state.tutor.config['model']['name']}  
        **Temperature:** {st.session_state.tutor.config['model']['temperature']}
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Chat with Your Tutor")
        
        # Chat container with scrolling
        chat_container = st.container(height=500)
        
        with chat_container:
            # Display chat history
            display_chat_history()
        
        # Chat input (outside container so it's always visible)
        user_input = st.chat_input("Ask a question about data science, submit code for review, or request help...")
        
        if user_input:
            # Add user message to history
            st.session_state.messages.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Get response from tutor
            with st.spinner("Processing..."):
                response = st.session_state.tutor.process_message(user_input)
                
                # Update counters
                st.session_state.interaction_count += 1
                if response['blocked']:
                    st.session_state.blocked_count += 1
                
                # Log the interaction
                st.session_state.logger.log_interaction(
                    user_message=user_input,
                    assistant_response=response['response'],
                    blocked=response['blocked'],
                    defense_log=response['defense_log']
                )
                
                # Add assistant message to history
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response['response'],
                    'timestamp': datetime.now().isoformat(),
                    'blocked': response['blocked'],
                    'defense_log': response['defense_log']
                })
            
            st.rerun()
    
    with col2:
        st.subheader("Quick Actions")
        
        # Code review
        with st.expander("Submit Code for Review"):
            code_input = st.text_area(
                "Paste your Python code here:",
                height=200,
                placeholder="import pandas as pd\n\ndef analyze_data(df):\n    ..."
            )
            
            context_input = st.text_input(
                "Context (optional):",
                placeholder="Homework problem 3..."
            )
            
            if st.button("Get Code Review"):
                if code_input:
                    with st.spinner("Reviewing code..."):
                        review = st.session_state.tutor.analyze_code(code_input, context_input)
                        
                        st.session_state.interaction_count += 1
                        
                        # Log
                        st.session_state.logger.log_feedback(
                            feedback_type="code_review",
                            submission_content=code_input,
                            feedback_generated=review['review'],
                            metadata={"context": context_input}
                        )
                        
                        # Add to chat
                        st.session_state.messages.append({
                            'role': 'user',
                            'content': f"[Code Review Request]\n```python\n{code_input[:100]}...\n```",
                            'timestamp': datetime.now().isoformat()
                        })
                        st.session_state.messages.append({
                            'role': 'assistant',
                            'content': review['review'],
                            'timestamp': datetime.now().isoformat(),
                            'blocked': False,
                            'defense_log': review.get('defense_log', {})
                        })
                    
                    st.rerun()
                else:
                    st.warning("Please enter some code to review")
        
        # Example questions
        st.subheader("Example Questions")
        
        example_questions = [
            "Explain what pandas DataFrames are",
            "What's the difference between .loc and .iloc?",
            "How do I handle missing values in a dataset?",
            "Can you help me debug a KeyError?",
            "What's linear regression in simple terms?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question[:20]}"):
                st.session_state.messages.append({
                    'role': 'user',
                    'content': question,
                    'timestamp': datetime.now().isoformat()
                })
                
                with st.spinner("Processing..."):
                    response = st.session_state.tutor.process_message(question)
                    
                    st.session_state.interaction_count += 1
                    if response['blocked']:
                        st.session_state.blocked_count += 1
                    
                    st.session_state.logger.log_interaction(
                        user_message=question,
                        assistant_response=response['response'],
                        blocked=response['blocked'],
                        defense_log=response['defense_log']
                    )
                    
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': response['response'],
                        'timestamp': datetime.now().isoformat(),
                        'blocked': response['blocked'],
                        'defense_log': response['defense_log']
                    })
                
                st.rerun()
    
    # Show logs if requested
    if st.session_state.get('show_logs', False):
        st.divider()
        st.subheader("Session Logs")
        
        log_stats = st.session_state.logger.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Interactions", log_stats['statistics']['total_interactions'])
        with col2:
            st.metric("Blocked", log_stats['statistics']['blocked_interactions'])
        with col3:
            st.metric("Attacks Detected", log_stats['statistics']['attacks_detected'])
        with col4:
            st.metric("Feedback Generated", log_stats['statistics']['feedback_generated'])
        
        st.json(log_stats)
        
        if st.button("Hide Logs"):
            st.session_state.show_logs = False
            st.rerun()


if __name__ == "__main__":
    main()
