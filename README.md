# AI Code Reviewer 🤖

An intelligent, AI-powered code analysis tool designed to help developers write better, cleaner, and more secure code. This application leverages **Streamlit** for the frontend and **Hugging Face models** (Qwen 2.5) via **LangChain** to provide deep insights, refactoring suggestions, and security audits.

## 🚀 Key Features

*   **🌍 Multi-Language Support**: Professional-grade reviews for **Python, JavaScript, TypeScript, Java, C++, Go, and Rust**.
*   **💻 Ace Code Editor**: Integrated professional editor with syntax highlighting, themes (Monokai), and VS Code keybindings.
*   **✨ One-Click AI Refactoring**: Automatically optimizes your code for performance, readability, and DRY principles.
*   **🧪 Automated Unit Test Generation**: Generates comprehensive unit tests tailored to your specific language and framework (e.g., `pytest`, `Jest`, `JUnit`).
*   **📊 Visual Analytics Dashboard**: Interactive charts (powered by Plotly) to track quality trends, language distribution, and score history.
*   **📝 PR Summary Generator**: Automatically writes professional GitHub/GitLab Pull Request descriptions.
*   **📖 Junior-Friendly Explainer**: Break down complex logic line-by-line for easier learning and onboarding.
*   **⚙️ CI/CD Workflow Builder**: Generate GitHub Actions YAML files to automate reviews in your repository.
*   **🛡️ Security & Performance Audit**: Deep scans for OWASP vulnerabilities and performance bottlenecks.
*   **🆚 Visual Code Diff**: Side-by-side comparison of your original code versus the AI-improved version.
*   **🔍 Context Search**: Direct links to StackOverflow and Google Documentation for identified issues.
*   **💬 AI Assistant (with Memory)**: Multi-turn chat to ask follow-up questions about the code review.

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.8+
*   A Hugging Face Account & Access Token

### 1. Clone the Repository
```bash
git clone https://github.com/PratikHarkare06/AI-Code-Reviewier.git
cd AI-Code-Reviewier
```

### 2. Create a Virtual Environment (Optional)
```bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```ini
HF_TOKEN=your_huggingface_access_token_here
```

## 🏃‍♂️ Usage

1.  **Launch App**: `streamlit run app.py`
2.  **Select Language**: Choose your programming language from the sidebar.
3.  **Input Code**: Paste your code or upload a file directly into the **Ace Editor**.
4.  **Run Analysis**: Click **⚡ Run Analysis** to get a quality grade and line-by-line feedback.
5.  **Explore Tools**: Use the sidebar to navigate to:
    *   **Dashboard**: Visualize your codebase health.
    *   **CI/CD Setup**: Generate automated workflows.
    *   **AI Assistant**: Discuss the analysis in-depth.

## 📂 Project Structure

```
├── app.py                 # Main application UI and multi-page routing
├── ai_suggessions.py      # Core AI logic (Refactoring, Tests, Chat, PRs)
├── code_parser.py         # Multi-language syntax checkers
├── error_detector.py      # Static analysis (unused vars/imports for Python)
├── history.json           # Local session history storage
├── requirements.txt       # Project dependencies (Streamlit, Plotly, Ace, etc.)
└── .env                   # Sensitive API keys (Not committed)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
Made with ❤️ by Pratik
