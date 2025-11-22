# NIYAMR-AI-48-Hour-Internship-Assignment-AI-Agent-Development-
Build a mini AI agent that can read, summarise, and analyse the Universal Credit Act 2025 and return a structured JSON report.

AI Agent that analyzes legislative documents using Ollama (local LLM)

What It Does
Analyzes the Universal Credit Act 2025 PDF and generates a structured JSON report:
Task 1: Extract text from PDF
Task 2: Summarize in 5-10 bullet points
Task 3: Extract key sections (definitions, eligibility, payments, etc.)
Task 4: Check 6 compliance rules with evidence

Quick Start
1. Install Ollama
Download from ollama.ai
Pull the model
ollama pull llama3.2
2. Install Dependencies
pip install -r requirements.txt
3. Run the Analyzer

Output Format
The analyzer creates output_report.json:
json{
  "metadata": {
    "document": "Universal Credit Act 2025",
    "analyzer": "NIYAMR AI Agent",
    "model": "llama3.2"
  },
  "task2_summary": [
    "- The Act establishes Universal Credit...",
    "- Eligibility requires..."
  ],
  "task3_sections": {
    "definitions": "...",
    "eligibility": "...",
    "payments": "..."
  },
  "task4_rule_checks": [
    {
      "rule": "Act must define key terms",
      "status": "pass",
      "evidence": "Section 2",
      "confidence": 85
    }
  ]
}

How It Works
PDF → PyPDF2 → Extract Text
            ↓
       Ollama LLM → Summarize (Task 2)
            ↓
     Keyword Search → Extract Sections (Task 3)
            ↓
    Rule Validation → Check Compliance (Task 4)
            ↓
        JSON Report

Key Design Choices:

Ollama for free, local LLM processing
Keyword matching for reliable section extraction
Simple logic for fast, accurate rule checks

Technologies

Python 3.8+
PyPDF2 - PDF text extraction
Ollama - Local LLM (llama3.2)
