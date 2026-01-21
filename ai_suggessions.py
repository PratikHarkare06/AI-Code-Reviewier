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

def get_ai_suggestion(code_string: str) -> str:
    """
    Perform a strict, accurate AI-based Python code review.
    """

    prompt = f"""
You are a **senior Python engineer and professional code reviewer**.

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
- NameError / TypeError are NOT syntax errors
- Static analysis must be based ONLY on the improved code

--------------------------------------------------

STEP 1: ANALYZE ORIGINAL CODE

Identify ONLY real issues and classify them correctly:
- Syntax Error → invalid Python syntax
- Runtime Error → NameError, TypeError, etc.
- PEP8 Issue → formatting/style only
- Unused Code → ONLY if never referenced

--------------------------------------------------

STEP 2: WRITE IMPROVED CODE

Rules:
- Fix ONLY the issues identified
- Remove ALL unused imports and variables
- Do NOT introduce new logic
- Use f-strings instead of string concatenation
- Keep the code minimal and clean
- The improved code MUST be valid Python
- CRITICAL: Analyze the improved code and remove any imports/variables that are not used
- IMPORTANT: Use proper Python indentation (4 spaces) and formatting
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

**Best Practices & PEP8:**
- Python coding standards compliance
- Industry best practices
- Security implications
- Error handling improvements

--------------------------------------------------

STEP 4: FINAL STATIC ANALYSIS (ON IMPROVED CODE ONLY)

Report:
- Unused Imports: List ALL unused imports in improved code
- Unused Variables: List ALL unused variables in improved code
- Syntax Errors: List ALL syntax errors in improved code
- Runtime Risks: List ALL potential runtime issues in improved code

IMPORTANT: Be thorough and accurate in your analysis. If no issues exist in a category, explicitly say "None".

--------------------------------------------------

REQUIRED OUTPUT FORMAT (EXACT)

## Analysis Summary
[Short, factual summary]

## Original Code
```python
{code_string}
```

## Issues Found
- Issue: Why it matters
(If none: No critical issues found.)

## Improved Code
```python
[Write ONLY the improved code here with proper Python indentation and formatting]
```

## Detailed Explanations

### 🚀 Scalability Impact
[Explain how each change affects scalability, performance for larger datasets, memory usage, and resource management]

### ⏱️ Time/Space Complexity
[Explain algorithm efficiency improvements, Big O notation impact, memory allocation optimization, and computational cost reduction]

### 📖 Readability & Maintainability
[Explain code clarity improvements, documentation benefits, team collaboration advantages, and future maintenance considerations]

### 📋 Best Practices & PEP8
[Explain Python coding standards compliance, industry best practices, security implications, and error handling improvements]

## Recommendations
- Clear, actionable recommendation

## Overall Quality Score
X/10 (Based on Correctness, Efficiency, Security, & Readability)

## Static Analysis Results
- Unused Imports: [List the unused imports found in improved code, or "None"]
- Unused Variables: [List the unused variables found in improved code, or "None"]
- Syntax Errors: [List syntax errors in improved code, or "None"]
- Runtime Risks: [List runtime risks in improved code, or "None"]

--------------------------------------------------

CODE TO ANALYZE
<python>
{code_string}
</python>
"""

    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as error:
        return f"Error getting AI suggestions: {str(error)}"

# --------------------------------------------------
# Chat Functionality 
# --------------------------------------------------

def get_chat_response(code_context: str, analysis_result: str, user_question: str) -> str:
    """
    Handle user follow-up questions based on the code and analysis.
    """
    prompt = f"""
You are a helpful AI coding assistant. The user has some code and an analysis of that code. 
They are asking a follow-up question. Answer their question clearly and concisely.

CONTEXT:
Code:
```python
{code_context}
```

Analysis Summary provided to user:
{analysis_result[:2000]}... (truncated)

USER QUESTION:
{user_question}

YOUR ANSWER:
"""
    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as error:
        return f"Error getting chat response: {str(error)}"


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
