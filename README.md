# AI Code Reviewer 🤖

An intelligent, AI-powered code analysis tool designed to help developers write better, cleaner, and more secure code. This application leverages **Streamlit** for the frontend and **Hugging Face models** (Qwen 2.5) via **LangChain** to provide professional-grade insights across multiple languages.

## 🚀 Key Features

*   **🌍 Multi-Language Support**: Professional reviews for **Python, JavaScript, TypeScript, Java, C++, Go, and Rust**.
*   **🎨 Customizable Ace Editor**: Integrated professional editor with **10+ Themes** (Monokai, Nord, Solarized), dynamic **Font Resizing**, and **Keybindings** (VS Code, Vim, Emacs).
*   **✨ One-Click AI Refactoring**: Automatically optimizes your code for performance, readability, and DRY principles.
*   **🧪 Automated Unit Test Generation**: Generates comprehensive tests tailored to your specific language and framework (e.g., `pytest`, `Jest`, `JUnit`).
*   **📊 Visual Analytics Dashboard**: Interactive charts (Plotly) to track quality trends, language distribution, and score history.
*   **📝 PR Summary Generator**: Automatically writes professional GitHub/GitLab Pull Request descriptions.
*   **📖 Junior-Friendly Explainer**: Break down complex logic line-by-line for easier learning and onboarding.
*   **⚙️ CI/CD Workflow Builder**: Generate GitHub Actions YAML files to automate reviews in your repository.
*   **🛡️ Security & Performance Audit**: Deep scans for OWASP vulnerabilities and performance bottlenecks.
*   **🔍 Context Search**: Direct links to StackOverflow and Google Documentation for identified issues.
*   **💬 AI Assistant (with Memory)**: Multi-turn chat to ask follow-up questions about the code review.

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.8+
*   A Hugging Face Account & Access Token

### 1. Clone & Setup
```bash
git clone https://github.com/PratikHarkare06/AI-Code-Reviewier.git
cd AI-Code-Reviewier
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```ini
HF_TOKEN=your_huggingface_access_token_here
```

## 🏃‍♂️ Usage

1.  **Launch App**: `streamlit run app.py`
2.  **Pick Theme & Language**: Adjust your editor settings and source language in the sidebar.
3.  **Run Analysis**: Click **⚡ Run Analysis** to get a quality grade and line-by-line feedback.
4.  **Explore Tabs**: Navigate through the **Assistant**, **Dashboard**, and **CI/CD Build** tabs to take full control of your codebase.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

---
Made with ❤️ by Pratik
