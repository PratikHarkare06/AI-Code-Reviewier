import streamlit as st
from code_parser import parse_code
from ai_suggessions import get_ai_suggestion, get_chat_response, get_unit_tests
from error_detector import get_all_errors
import time
try:
    from streamlit_ace import st_ace
    HAS_ACE = True
except ImportError:
    HAS_ACE = False

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
            <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Elevate Your Code Quality</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    if "nav_selection" not in st.session_state:
        st.session_state.nav_selection = "Code Editor"
        
    st.subheader("📍 Navigation")
    pages = ["Code Editor", "Analysis Report", "AI Assistant", "Dashboard", "CI/CD Setup", "History"]
    page_selection = st.radio(
        "Go to:", 
        pages, 
        index=pages.index(st.session_state.nav_selection),
        key="nav_radio",
        label_visibility="collapsed"
    )
    # Sync radio with session state manually if needed, or rely on key
    if st.session_state.nav_radio != st.session_state.nav_selection:
        st.session_state.nav_selection = st.session_state.nav_radio
        st.rerun()

    st.markdown("---")
    
    st.subheader("⚙️ Configuration")
    language = st.selectbox("Source Language", ["Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust"], index=0)
    
    st.markdown("### Focus Areas")
    check_security = st.checkbox("Security Audit", value=True)
    check_perf = st.checkbox("Performance Audit", value=True)
    check_style = st.checkbox("Style & Standards", value=True)
    check_bugs = st.checkbox("Logic & Bugs", value=True)
    
    st.markdown("---")
    st.markdown("### 🛡️ Advanced Analysis")
    deep_scan = st.toggle("Deep Vulnerability Scan", value=False)
    complex_analysis = st.toggle("Code Complexity Analysis", value=False)


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
if 'unit_tests' not in st.session_state:
    st.session_state.unit_tests = None

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

def extract_improved_code(ai_text, language="Python"):
    """Simple regex to extract code block after 'Improved Code'."""
    import re
    lang_lower = language.lower()
    # Look for code block after "Improved Code" with the specific language tag
    pattern = rf"## Improved Code\s*```{lang_lower}\s*(.*?)```"
    match = re.search(pattern, ai_text, re.DOTALL)
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
    # 🆕 NEW: File Upload Support
    st.markdown("### 📁 File Upload (Optional)")
    uploaded_file = st.file_uploader("Upload a source file", type=["py", "js", "ts", "java", "cpp", "go", "rs", "txt"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        try:
            # Auto-detect language from extension
            ext = uploaded_file.name.split(".")[-1].lower()
            ext_map = {
                "py": "Python",
                "js": "JavaScript",
                "ts": "TypeScript",
                "java": "Java",
                "cpp": "C++",
                "go": "Go",
                "rs": "Rust"
            }
            if ext in ext_map:
                language = ext_map[ext]
                # Update language in session state if needed, but for now we just show a hint
                st.info(f"Detected {language} file: `{uploaded_file.name}`")
            
            code_content = uploaded_file.getvalue().decode("utf-8")
            st.session_state.code_input = code_content
        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.markdown("### 💻 Source Code Editor")
    if HAS_ACE:
        code = st_ace(
            value=st.session_state.code_input,
            language=language.lower(),
            theme="monokai",
            keybinding="vscode",
            font_size=14,
            tab_size=4,
            height=500,
            key="ace_editor"
        )
    else:
        code = st.text_area(
            "Code Editor",
            value=st.session_state.code_input,
            height=500,
            placeholder=f"Paste your {language} code or upload a file above...",
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
                st.session_state.unit_tests = None
                st.session_state.last_analyzed = time.strftime("%H:%M:%S")
                
                # 2. Run Analysis
                with st.spinner("🔍  Analyzing code structure and safety..."):
                    # Static
                    if language == "Python":
                        parse_result = parse_code(code, language=language)
                        static_errors = get_all_errors(code, language=language)
                        st.session_state.analysis_result = {"parse": parse_result, "static": static_errors}
                    else:
                        st.session_state.analysis_result = {"parse": {"success": True}, "static": {}}
                    
                    # AI
                    suggestion = get_ai_suggestion(code, language=language)
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
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔄 Regenerate", type="primary", use_container_width=True, help="Get new AI suggestions"):
                     with st.spinner("🤖 Generating fresh insights..."):
                        suggestion = get_ai_suggestion(st.session_state.code_input, language=language)
                        st.session_state.ai_suggestions = suggestion
                        st.rerun()
            with btn_col2:
                if st.button("🧪 Generate Unit Tests", type="secondary", use_container_width=True):
                    with st.spinner("🧪 Crafting comprehensive tests..."):
                        tests = get_unit_tests(st.session_state.code_input, language=language)
                        st.session_state.unit_tests = tests
                        st.success("Tests generated!")

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
        
        improved_code = extract_improved_code(st.session_state.ai_suggestions, language=language)
        
        # --- NEW: Action Bar (Export) ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Download Report Button
        d_col1, d_col2 = st.columns([1, 4])
        with d_col1:
             report_text = f"""# AI Code Analysis Report ({language})
Date: {time.strftime("%Y-%m-%d %H:%M:%S")}
Quality Grade: {quality_grade}
Issues Found: {total_issues}

## Original Code
```{language.lower()}
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
        improved_code = extract_improved_code(st.session_state.ai_suggestions, language=language)
        
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

        # Unit Tests
        if st.session_state.unit_tests:
            with st.expander("🧪 Generated Unit Tests", expanded=True):
                st.markdown(st.session_state.unit_tests)

    # Search Integration
    st.markdown("---")
    st.subheader("🔍 Context Support")
    search_query = st.text_input("Search for help / Documentation", placeholder="Search for library docs, errors, etc.")
    if search_query:
        st.markdown(f"[Search on StackOverflow](https://stackoverflow.com/search?q={search_query.replace(' ', '+')}) | [Search on Google](https://www.google.com/search?q={search_query.replace(' ', '+')})")

# --------------------------------------------------
# PAGE 3: AI ASSISTANT
# --------------------------------------------------
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
                        prompt,
                        chat_history=st.session_state.chat_history[:-1],
                        language=language
                    )
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

# --------------------------------------------------
# PAGE 4: DASHBOARD
# --------------------------------------------------
elif st.session_state.nav_selection == "Dashboard":
    st.markdown("### 📊 Codebase Analytics")
    
    history_data = load_history()
    if not history_data:
        st.info("No data available. Run some analyses first!")
    else:
        import pandas as pd
        import plotly.express as px
        
        df = pd.DataFrame(history_data)
        # Parse scores
        df['score'] = df['quality_grade'].apply(lambda x: int(x.split('/')[0]) if '/' in str(x) and x.split('/')[0].isdigit() else 0)
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### Quality Trend")
            fig = px.line(df.iloc[::-1], x="timestamp", y="score", markers=True, 
                         labels={"score": "Quality Score", "timestamp": "Time"},
                         template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("##### Language Distribution")
            lang_counts = df['language'].value_counts().reset_index()
            lang_counts.columns = ['language', 'count']
            fig2 = px.pie(lang_counts, values='count', names='language', hole=0.3, template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("##### Score Distribution")
        fig3 = px.histogram(df, x="score", nbins=10, template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)

# --------------------------------------------------
# PAGE 5: CI/CD SETUP
# --------------------------------------------------
elif st.session_state.nav_selection == "CI/CD Setup":
    st.markdown("### ⚙️ CI/CD Workflow Generator")
    st.caption("Generate automated GitHub Actions to review your code on every push.")
    
    ci_lang = st.selectbox("Select Project Type", ["Python (Pytest)", "Node.js (Jest)", "Java (Maven)", "Go (Test)"])
    
    if st.button("🚀 Generate Workflow", type="primary"):
        workflows = {
            "Python (Pytest)": """name: Python Code Review
on: [push, pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest
      - name: Run Tests
        run: pytest""",
            "Node.js (Jest)": """name: Node.js Code Review
on: [push, pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Use Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install
      - run: npm test""",
            "Java (Maven)": """name: Java Maven Review
on: [push, pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven
      - name: Build with Maven
        run: mvn -B package --file pom.xml""",
            "Go (Test)": """name: Go Code Review
on: [push, pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.20'
      - name: Build
        run: go build -v ./...
      - name: Test
        run: go test -v ./..."""
        }
        
        st.code(workflows[ci_lang], language="yaml")
        st.download_button("📥 Download .yml", workflows[ci_lang], file_name="review-workflow.yml")

# --------------------------------------------------
# PAGE 6: HISTORY
# --------------------------------------------------
elif st.session_state.nav_selection == "History":
    st.markdown("### 📜 Analysis History")
    
    history_data = load_history()
    if not history_data:
        st.info("No history found. Run an analysis to see it here.")
    else:
        for i, entry in enumerate(history_data):
            with st.expander(f"{entry['date']} at {entry['timestamp']} - Grade: {entry['quality_grade']}"):
                st.write(f"**Language:** {entry.get('language', 'N/A')}")
                st.code(entry.get('code_snippet', ''), language=entry.get('language', 'python').lower())

