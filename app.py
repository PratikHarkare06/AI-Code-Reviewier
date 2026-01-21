import streamlit as st
from code_parser import parse_code
from ai_suggessions import get_ai_suggestion, get_chat_response
from error_detector import get_all_errors
import time

# Configure page settings - Must be first streamlit command
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Professional UI Styling (CSS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* BASE THEME */
    .stApp {
        background-color: #0f1116;
        color: #e6edf3;
        font-family: 'Inter', sans-serif;
    }

    /* TYPOGRAPHY */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: -0.025em;
        color: #ffffff !important;
    }

    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace;
    }

    /* SIDEBAR styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    
    /* CUSTOM COMPONENTS */
    
    /* Card Container */
    .css-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Primary Button */
    div.stButton > button {
        background: linear-gradient(180deg, #238636 0%, #2ea043 100%);
        color: white;
        border: 1px solid rgba(240, 246, 252, 0.1);
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        text-shadow: 0 1px 0 rgba(0,0,0,0.1);
    }
    
    div.stButton > button:hover {
        background: #2ea043;
        border-color: #8b949e;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    
    div.stButton > button:active {
        transform: translateY(0);
    }

    /* Secondary/Action Button */
    div.stButton > button[kind="secondary"] {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
    }

    /* Text Area */
    .stTextArea textarea {
        background-color: #0d1117;
        border: 1px solid #30363d;
        color: #e6edf3;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .stTextArea textarea:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3);
    }

    /* Metrics */
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        padding: 1rem;
        border-radius: 6px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #58a6ff;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Headers */
    .header-container {
        padding: 1rem 0 2rem 0;
        border-bottom: 1px solid #30363d;
        margin-bottom: 2rem;
    }
    
    .status-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    .status-badge.success { background: rgba(46, 160, 67, 0.15); color: #3fb950; border: 1px solid rgba(46, 160, 67, 0.4); }
    .status-badge.error { background: rgba(248, 81, 73, 0.15); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.4); }

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar & Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/2920/2920277.png" width="60" style="margin-bottom: 10px;">
            <h1 style="margin-top: 0; font-size: 1.8rem; padding-bottom: 5px;">AI Code Reviewer</h1>
            <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Made with ❤️ by Pratik</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    if "nav_selection" not in st.session_state:
        st.session_state.nav_selection = "Code Editor"
        
    st.subheader("📍 Navigation")
    page_selection = st.radio(
        "Go to:", 
        ["Code Editor", "Analysis Report", "AI Assistant", "History"], 
        index=["Code Editor", "Analysis Report", "AI Assistant", "History"].index(st.session_state.nav_selection),
        key="nav_radio",
        label_visibility="collapsed"
    )
    # Sync radio with session state manually if needed, or rely on key
    if st.session_state.nav_radio != st.session_state.nav_selection:
        st.session_state.nav_selection = st.session_state.nav_radio
        st.rerun()

    st.markdown("---")
    
    st.subheader("⚙️ Configuration")
    language = st.selectbox("Source Language", ["Python", "JavaScript", "TypeScript", "Go", "Rust"], index=0)
    
    st.markdown("### Focus Areas")
    check_security = st.checkbox("Security", value=True)
    check_perf = st.checkbox("Performance", value=True)
    check_style = st.checkbox("PEP8 / Style", value=True)
    check_bugs = st.checkbox("Potential Bugs", value=True)


# -----------------------------------------------------------------------------
# Session State & Logic
# -----------------------------------------------------------------------------

# (Keep existing session state init)
if 'code_input' not in st.session_state:
    st.session_state.code_input = ""
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'ai_suggestions' not in st.session_state:
    st.session_state.ai_suggestions = None
if 'last_analyzed' not in st.session_state:
    st.session_state.last_analyzed = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
st.title("Intelligent Code Analysis")
st.markdown("Automated code review, security auditing, and optimization recommendations.")
st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)


# ... (Keep existing imports)
import json
import os
import difflib

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_to_history(entry):
    history = load_history()
    history.insert(0, entry)  # Add new entry to top
    history = history[:10]    # Keep only latest 10 entries
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def extract_improved_code(ai_text):
    """Simple regex to extract code block after 'Improved Code'."""
    import re
    # Look for python code block after "Improved Code"
    match = re.search(r"## Improved Code\s*```python\s*(.*?)```", ai_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def generate_diff_html(original, improved):
    """Generate a simple side-by-side div diff."""
    d = difflib.HtmlDiff()
    # clean up the table slightly for dark mode
    html = d.make_file(original.splitlines(), improved.splitlines(), fromdesc="Original", todesc="Improved", context=True, numlines=3)
    # Inject some CSS to make it look decent in the dark app
    style = """
    <style>
        body { background-color: white; margin: 0; padding: 10px; }
        table.diff {font-family: 'JetBrains Mono', monospace; border: none; font-size: 16px; width: 100%; color: #333;}
        .diff_header {background-color: #e0e0e0;}
        .diff_next, .diff_add, .diff_chg, .diff_sub {white-space: pre-wrap;}
    </style>
    """
    return style + html


# -----------------------------------------------------------------------------
# PAGE 1: CODE EDITOR
# -----------------------------------------------------------------------------
if st.session_state.nav_selection == "Code Editor":
    st.markdown("### 💻 Source Code Input")
    code = st.text_area(
        "Code Editor",
        value=st.session_state.code_input,
        height=500,
        placeholder=f"Paste your {language} code here...",
        label_visibility="collapsed",
        key="code_editor_area"
    )
    st.session_state.code_input = code
    
    col_btn, col_empty = st.columns([1, 4])
    with col_btn:
        if st.button("⚡ Run Analysis", use_container_width=True, type="primary"):
            if code.strip():
                # 1. Clear State
                st.session_state.chat_history = []
                st.session_state.last_analyzed = time.strftime("%H:%M:%S")
                
                # 2. Run Analysis
                with st.spinner("🔍  Analyzing code structure and safety..."):
                    # Static
                    if language == "Python":
                        parse_result = parse_code(code)
                        static_errors = get_all_errors(code)
                        st.session_state.analysis_result = {"parse": parse_result, "static": static_errors}
                    else:
                        st.session_state.analysis_result = {"parse": {"success": True}, "static": {}}
                    
                    # AI
                    config_context = f"\n# ANALYSIS CONFIG: Security={check_security}, Performance={check_perf}"
                    suggestion = get_ai_suggestion(code)
                    st.session_state.ai_suggestions = suggestion
                
                # 3. Save to History
                # Extract score for history
                import re
                score_match = re.search(r"Overall Quality Score\n(\d+)/10", st.session_state.ai_suggestions)
                grade = f"{score_match.group(1)}/10" if score_match else "N/A"
                
                history_entry = {
                    "timestamp": st.session_state.last_analyzed,
                    "date": time.strftime("%Y-%m-%d"),
                    "language": language,
                    "quality_grade": grade,
                    "code_snippet": code[:100] + "..." if len(code) > 100 else code
                    # We could save full report but might get large. Keeping it simple.
                }
                save_to_history(history_entry)

                # 4. Redirect
                st.session_state.nav_selection = "Analysis Report"
                st.rerun()
            else:
                st.warning("Please paste some code first!")

# -----------------------------------------------------------------------------
# PAGE 2: ANALYSIS REPORT
# -----------------------------------------------------------------------------
elif st.session_state.nav_selection == "Analysis Report":
    
    # Header
    r_col1, r_col2 = st.columns([0.7, 0.3], vertical_alignment="center")
    with r_col1:
        img_col, txt_col = st.columns([0.15, 0.85], vertical_alignment="center")
        with img_col:
            # Lucide 'Bot' icon SVG
            st.markdown("""
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#58a6ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 8V4H8"/>
                <rect width="16" height="12" x="4" y="8" rx="2"/>
                <path d="M2 14h2"/>
                <path d="M20 14h2"/>
                <path d="M15 13v2"/>
                <path d="M9 13v2"/>
            </svg>
            """, unsafe_allow_html=True)
        with txt_col:
            st.markdown("### Analysis Report")
            
    with r_col2:
        if st.session_state.ai_suggestions:
            if st.button("🔄 Regenerate", type="primary", use_container_width=True, help="Get new AI suggestions"):
                 with st.spinner("🤖 Generating fresh insights..."):
                    suggestion = get_ai_suggestion(st.session_state.code_input)
                    st.session_state.ai_suggestions = suggestion
                    st.rerun()

    # Empty State check
    if not st.session_state.ai_suggestions:
        st.info("No analysis available yet. Go to 'Code Editor' and run an analysis.")
    else:
        # Metrics
        try:
            issue_count = st.session_state.ai_suggestions.count("- Issue:")
            if "No critical issues found" in st.session_state.ai_suggestions: issue_count = 0
        except: issue_count = 0
        
        import re
        score_match = re.search(r"Overall Quality Score\n(\d+)/10", st.session_state.ai_suggestions)
        quality_grade = f"{score_match.group(1)}/10" if score_match else "N/A"
        
        static_issues_count = 0
        if st.session_state.analysis_result:
            static_data = st.session_state.analysis_result.get("static", {})
            static_issues_count += len(static_data.get('unused_variables', []))
            static_issues_count += len(static_data.get('unused_imports', []))
        total_issues = issue_count + static_issues_count

        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="metric-card"><div class="metric-value">{quality_grade}</div><div class="metric-label">Quality Grade</div></div>', unsafe_allow_html=True)
        with m2: 
            color = "#f85149" if total_issues > 0 else "#2ea043"
            st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {color};">{total_issues}</div><div class="metric-label">Issues Found</div></div>', unsafe_allow_html=True)
        with m3: st.markdown('<div class="metric-card"><div class="metric-value" style="color: #a371f7;">AI</div><div class="metric-label">Reviewer</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- NEW: Action Bar (Diff + Export) ---
        ac1, ac2 = st.columns([1, 1])
        
        improved_code = extract_improved_code(st.session_state.ai_suggestions)
        
        # --- NEW: Action Bar (Export) ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Download Report Button
        d_col1, d_col2 = st.columns([1, 4])
        with d_col1:
             report_text = f"""# AI Code Analysis Report
Date: {time.strftime("%Y-%m-%d %H:%M:%S")}
Quality Grade: {quality_grade}
Issues Found: {total_issues}

## Original Code
```python
{st.session_state.code_input}
```

## Review Findings
{st.session_state.ai_suggestions}
             """
             st.download_button(
                 label="📥 Download Report (MD)",
                 data=report_text,
                 file_name="code_analysis_report.md",
                 mime="text/markdown",
                 use_container_width=True
             )

        # --- Diff View (Full Width) ---
        improved_code = extract_improved_code(st.session_state.ai_suggestions)
        
        if improved_code:
             st.markdown("<br>", unsafe_allow_html=True)
             with st.expander("🆚 Compare Changes (Diff View)", expanded=True):
                 st.markdown("##### Side-by-Side Comparison")
                 html_diff = generate_diff_html(st.session_state.code_input, improved_code)
                 st.components.v1.html(html_diff, height=800, scrolling=True)

        # Static Analysis Findings
        if st.session_state.analysis_result:
            parse_res = st.session_state.analysis_result.get("parse", {})
            static = st.session_state.analysis_result.get("static", {})
            
            if not parse_res.get("success", True):
                st.error(f"❌ Syntax Error: {parse_res.get('error', {}).get('message', 'Unknown Error')}")
            
            if static.get('unused_variables') or static.get('unused_imports'):
                with st.expander("🔎 Static Analysis Findings", expanded=True):
                    if static.get('unused_variables'):
                        st.markdown("**Unused Variables:**")
                        for v in static['unused_variables']:
                            if isinstance(v, dict):
                                st.markdown(f"- <span style='color:#f85149'>{v['name']}</span> (Line {v['line']})", unsafe_allow_html=True)
                            else:
                                st.markdown(f"- {str(v)}")
                    
                    if static.get('unused_imports'):
                        st.markdown("**Unused Imports:**")
                        for i in static['unused_imports']:
                            if isinstance(i, dict):
                                st.markdown(f"- <span style='color:#f85149'>{i['name']}</span> (from {i['full_name']})", unsafe_allow_html=True)
                            else:
                                st.markdown(f"- {str(i)}")

        # AI Report
        with st.expander("🤖 Deep Code Review", expanded=True):
            st.markdown(st.session_state.ai_suggestions)

# -----------------------------------------------------------------------------
# PAGE 3: AI ASSISTANT
# -----------------------------------------------------------------------------
elif st.session_state.nav_selection == "AI Assistant":
    st.markdown("### 💬 AI Assistant")
    
    if not st.session_state.ai_suggestions:
         st.warning("⚠️ Please run a code analysis first so the AI has context to answer your questions.")
    else:
        st.caption("Ask questions about your code, the analysis, or improvement strategies.")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a follow-up question..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_chat_response(
                        st.session_state.code_input, 
                        st.session_state.ai_suggestions, 
                        prompt
                    )
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

# -----------------------------------------------------------------------------
# PAGE 4: HISTORY
# -----------------------------------------------------------------------------
elif st.session_state.nav_selection == "History":
    st.markdown("### 📜 Analysis History")
    
    history_data = load_history()
    
    if not history_data:
        st.info("No history found. Run an analysis to see it here.")
    else:
        # Display as a table or cards
        for i, entry in enumerate(history_data):
            with st.expander(f"{entry['date']} at {entry['timestamp']} - Grade: {entry['quality_grade']}"):
                st.write(f"**Language:** {entry.get('language', 'N/A')}")
                st.code(entry.get('code_snippet', ''), language=entry.get('language', 'python').lower())

