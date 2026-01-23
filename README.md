# AI Code Reviewer 🤖

An intelligent, AI-powered code analysis tool designed to help developers write better, cleaner, and more secure code. This application leverages **Streamlit** for the frontend and **Hugging Face models** (Qwen 2.5) via **LangChain** to provide deep insights, refactoring suggestions, and security audits.

## 🚀 Features

*   **🔍 Intelligent Analysis**: Automated checks for syntax errors, potential bugs, and code style issues.
*   **🛡️ Security & Performance**: Identifies security vulnerabilities and performance bottlenecks.
*   **🆚 Visual Code Diff**: Side-by-side comparison of your original code versus the AI-improved version with highlighted changes.
*   **💬 AI Chat Assistant**: Interactive chat to ask follow-up questions about the code review.
*   **📜 History Log**: Saves your last 10 analysis sessions locally for quick reference.
*   **📥 Export Reports**: Download detailed analysis reports in Markdown format.

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.8+
*   A Hugging Face Account & Access Token

### 1. Clone the Repository
```bash
git clone https://github.com/PratikHarkare06/AI-Code-Reviewier.git
cd AI-Code-Reviewier
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add your Hugging Face token:
```ini
HF_TOKEN=your_huggingface_access_token_here
```

## 🏃‍♂️ Usage

Run the Streamlit application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

1.  **Paste Code**: Enter your code into the editor on the left.
2.  **Run Analysis**: Click the **⚡ Run Analysis** button.
3.  **Review Results**: View the quality score, issues, and AI recommendations.
4.  **Compare**: Use the "Compare Changes" view to see differences.
5.  **Chat**: Switch to the **AI Assistant** tab to discuss the feedback.

## 📂 Project Structure

```
├── app.py                 # Main application entry point & UI
├── ai_suggessions.py      # AI model interaction logic
├── code_parser.py         # Syntax checkers and AST parsing
├── error_detector.py      # Static analysis (unused vars, imports)
├── history.json           # Local storage for analysis history
├── requirement.txt        # Python dependencies
└── .env                   # API keys (Not committed)
```

## 🧠 Tech Stack

*   **Frontend**: Streamlit
*   **LLM Integration**: LangChain, Hugging Face Hub
*   **Model**: Qwen/Qwen2.5-7B-Instruct
*   **Static Analysis**: Python `ast` module
*   **Utils**: `difflib` for diffs, `dotenv` for config

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
Made with ❤️ by Pratik
