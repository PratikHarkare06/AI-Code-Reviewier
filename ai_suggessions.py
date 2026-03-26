from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from dotenv import load_dotenv
import os

# --------------------------------------------------
# Environment Setup
# --------------------------------------------------

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in environment variables")

# --------------------------------------------------
# Model Initialization
# --------------------------------------------------

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    temperature=0.1,  # Very low temperature = factual, consistent output
    huggingfacehub_api_token=HF_TOKEN,
)

model = ChatHuggingFace(llm=llm)

# --------------------------------------------------
# AI Code Review Function
# --------------------------------------------------

def get_ai_suggestion(code_string: str, language: str = "Python") -> str:
    """
    Perform a strict, accurate AI-based code review for multiple languages.
    """

    lang_lower = language.lower()
    
    # Language specific standards
    standards = {
        "python": "PEP8",
        "javascript": "ESLint / Airbnb Style Guide",
        "typescript": "TSLint / Airbnb Style Guide",
        "java": "Google Java Style Guide",
        "c++": "Google C++ Style Guide",
        "go": "Gofmt / Uber Go Style Guide",
        "rust": "Rustfmt"
    }.get(lang_lower, "standard coding practices")

    prompt = f"""
You are a **senior {language} engineer and professional code reviewer**.

Your output MUST be:
- Factually correct
- Internally consistent
- Based ONLY on the code provided
- Free from hallucinations or assumptions

STRICT RULES (DO NOT BREAK):
- Do NOT invent issues
- Do NOT contradict yourself
- Do NOT analyze code that is not shown
- Do NOT flag variables/imports as unused if they are used
- Static analysis must be based ONLY on the improved code

--------------------------------------------------

STEP 1: ANALYZE ORIGINAL CODE

Identify ONLY real issues and classify them correctly (use {language} terminology):
- Syntax Error → invalid {language} syntax
- Runtime Error → potential errors during execution
- Style Issue → formatting according to {standards}
- Unused Code → ONLY if never referenced

--------------------------------------------------

STEP 2: WRITE IMPROVED CODE

Rules:
- Fix ONLY the issues identified
- Remove ALL unused imports/dependencies and variables
- Do NOT introduce new logic
- Use modern {language} best practices
- Keep the code minimal and clean
- The improved code MUST be valid {language}
- CRITICAL: Analyze the improved code and remove any parts that are not used
- IMPORTANT: Use proper {language} indentation (usually 4 spaces or 2 spaces)
- IMPORTANT: Preserve line breaks and code structure

--------------------------------------------------

STEP 3: DETAILED EXPLANATIONS

For each improvement made, provide detailed explanations:

**Scalability Impact:**
- How the change affects code scalability
- Performance implications for larger datasets
- Memory usage optimization
- Resource management improvements

**Time/Space Complexity:**
- Algorithm efficiency improvements
- Big O notation impact
- Memory allocation optimization
- Computational cost reduction

**Readability & Maintainability:**
- Code clarity improvements
- Documentation benefits
- Team collaboration advantages
- Future maintenance considerations

**Best Practices & Standards:**
- {language} coding standards compliance ({standards})
- Industry best practices
- Security implications
- Error handling improvements

--------------------------------------------------

STEP 4: FINAL STATIC ANALYSIS (ON IMPROVED CODE ONLY)

Report:
- Unused Imports/Dependencies: List ALL unused imports in improved code
- Unused Variables: List ALL unused variables in improved code
- Syntax Errors: List ALL syntax errors in improved code
- Runtime Risks: List ALL potential runtime issues in improved code

IMPORTANT: Be thorough and accurate in your analysis. If no issues exist in a category, explicitly say "None".

--------------------------------------------------

REQUIRED OUTPUT FORMAT (EXACT)

## Analysis Summary
[Short, factual summary]

## Original Code
```{lang_lower}
{code_string}
```

## Issues Found
- Issue: Why it matters
(If none: No critical issues found.)

## Improved Code
```{lang_lower}
[Write ONLY the improved code here with proper {language} indentation and formatting]
```

## Detailed Explanations

### 🚀 Scalability Impact
[Explain how each change affects scalability, performance for larger datasets, memory usage, and resource management]

### ⏱️ Time/Space Complexity
[Explain algorithm efficiency improvements, Big O notation impact, memory allocation optimization, and computational cost reduction]

### 📖 Readability & Maintainability
[Explain code clarity improvements, documentation benefits, team collaboration advantages, and future maintenance considerations]

### 📋 Best Practices & Standards
[Explain {language} coding standards compliance, industry best practices, security implications, and error handling improvements]

## Recommendations
- Clear, actionable recommendation

## Overall Quality Score
X/10 (Based on Correctness, Efficiency, Security, & Readability)

## Static Analysis Results
- Unused Imports/Dependencies: [List the unused imports found in improved code, or "None"]
- Unused Variables: [List the unused variables found in improved code, or "None"]
- Syntax Errors: [List syntax errors in improved code, or "None"]
- Runtime Risks: [List runtime risks in improved code, or "None"]

--------------------------------------------------

CODE TO ANALYZE
<{lang_lower}>
{code_string}
</{lang_lower}>
"""

    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as error:
        return f"Error getting AI suggestions: {str(error)}"

# --------------------------------------------------
# Chat Functionality 
# --------------------------------------------------

def get_chat_response(code_context: str, analysis_result: str, user_question: str, chat_history: list = None, language: str = "Python") -> str:
    """
    Handle user follow-up questions with full conversation history.
    """
    lang_lower = language.lower()
    
    # Format chat history for the prompt
    history_text = ""
    if chat_history:
        for msg in chat_history[-5:]: # Include last 5 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    prompt = f"""
You are a **senior {language} expert and helpful coding assistant**.
The user is asking questions about their code and a previously provided code review.

### TARGET LANGUAGE: {language}

### CODE CONTEXT:
```{lang_lower}
{code_context}
```

### RECENT ANALYSIS SUMMARY:
{analysis_result[:1500]}...

### CONVERSATION HISTORY:
{history_text}

### USER'S NEW QUESTION:
{user_question}

### YOUR INSTRUCTIONS:
- Answer the question specifically in the context of the provided code.
- If the user asks for more code, provide it in ```{lang_lower} blocks.
- Be concise but thorough.
- Mention specific line numbers or patterns if relevant.
- STICK TO {language} best practices.

YOUR RESPONSE:
"""
    try:
        response = model.invoke(prompt)
        # Clean up response if it echoes back the prompt
        content = response.content
        if "YOUR RESPONSE:" in content:
            content = content.split("YOUR RESPONSE:")[-1].strip()
        return content
    except Exception as error:
        return f"Error getting chat response: {str(error)}"


# --------------------------------------------------
# Unit Test Generation Function
# --------------------------------------------------

def get_unit_tests(code_string: str, language: str = "Python") -> str:
    """
    Generate unit tests for the provided code.
    """
    lang_lower = language.lower()
    framework = {
        "python": "pytest",
        "javascript": "Jest",
        "typescript": "Jest",
        "java": "JUnit",
        "c++": "Google Test",
        "go": "testing package",
        "rust": "built-in test modules"
    }.get(lang_lower, "standard testing framework")

    prompt = f"""
You are a **senior QA engineer and testing expert**.
The user wants to generate unit tests for the following {language} code.

{language} Source Code:
```{lang_lower}
{code_string}
```

STRICT RULES:
- Use the **{framework}** framework.
- Write comprehensive, isolated unit tests.
- Cover edge cases, success scenarios, and failure scenarios.
- Do NOT include the original code in your output, ONLY the test code.
- Ensure the test code is valid {language} and ready to run.
- Include necessary imports for the testing framework.

REQUIRED OUTPUT FORMAT:
## Unit Tests ({framework})
```{lang_lower}
[Write the test code here]
```

## How to Run
[Short instructions on how to install and run the tests]
"""
    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as error:
        return f"Error generating unit tests: {str(error)}"

def get_refactored_code(code: str, language: str = "Python") -> str:
    """
    Provide a fully refactored and optimized version of the code.
    """
    lang_lower = language.lower()
    prompt = f"""
You are an **Expert {language} Refactorer**. 
Take the following code and provide a clean, optimized, and best-practice version:

```{lang_lower}
{code}
```

### GOALS:
- DRY (Don't Repeat Yourself)
- SOLID principles
- Performance optimization
- Improved readability and naming
- Output ONLY the improved code.

REFACTORED CODE:
"""
    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as error:
        return f"Error refactoring code: {str(error)}"

def get_code_explanation(code: str, language: str = "Python") -> str:
    """
    Explain the code line-by-line for a junior developer.
    """
    lang_lower = language.lower()
    prompt = f"""
You are a **Patient Technical Mentor**. 
Explain the following {language} code to a junior developer:

```{lang_lower}
{code}
```

### STYLE:
- Use bullet points.
- Explain *why* certain patterns are used.
- Keep it friendly and clear.

EXPLANATION:
"""
    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as error:
        return f"Error explaining code: {str(error)}"

def get_pr_summary(code: str, language: str = "Python") -> str:
    """
    Generate a professional Pull Request description.
    """
    prompt = f"""
You are a **Senior Developer**. 
Write a professional GitHub Pull Request summary for the following {language} code changes:

```{language.lower()}
{code}
```

### FOLDER STRUCTURE:
- **Title**: A concise title
- **Summary**: What was changed?
- **Impact**: Why was this change made?
- **Checklist**: Standard PR checklist items

PR SUMMARY (Markdown):
"""
    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as error:
        return f"Error generating PR summary: {str(error)}"

# --------------------------------------------------
# Local Test (Optional)
# --------------------------------------------------

if __name__ == "__main__":
    sample_code = """
import os
import json
import sys  # This is unused
import datetime  # This is also unused

x = 10
y = 20
z = 30  # This variable is unused

def add(a, b):
    result = a + b
    return reslt  # Typo here

value = add(x, 5)
print("Sum is: " + value)
"""
    print(get_ai_suggestion(sample_code))
