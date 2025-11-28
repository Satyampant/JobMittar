# 💼 JobMittar - AI-Powered Job Search Assistant

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51.0-FF4B4B.svg)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0.3-00ADD8.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **A smarter way to get hired** - Analyze your resume, find the right roles, and practice interviews — all powered by LangGraph orchestration and AI.

---

## 🌟 Overview

**JobMittar** is an intelligent job search assistant that leverages **LangGraph** for sophisticated workflow orchestration, combining resume analysis, job matching, and interactive interview preparation into a seamless experience. Built for the modern job seeker, it uses state-of-the-art AI models to provide personalized career guidance.

### 🎯 Key Features

- **📄 AI-Powered Resume Analysis**
  - Intelligent parsing of PDF, DOCX, and TXT formats
  - Comprehensive quality assessment with actionable feedback
  - ATS optimization recommendations
  - Skills extraction and gap analysis

- **🔍 Smart Job Search**
  - Real-time job discovery across multiple platforms (LinkedIn, Indeed, Glassdoor)
  - Resume-based intelligent job matching
  - Compatibility scoring with detailed gap analysis
  - Job bookmarking and management

- **🎙️ Interactive Interview Preparation**
  - AI-generated role-specific interview questions
  - **Live voice-based interview practice** with real-time transcription
  - Instant AI feedback with confidence and accuracy scoring
  - Text-to-speech question delivery for realistic practice
  - Comprehensive performance analytics and downloadable reports

- **🧠 LangGraph-Powered Architecture**
  - Stateful workflow orchestration with checkpoint persistence
  - Intelligent routing between resume analysis, job search, and interview prep
  - Session resumption across page refreshes
  - Modular subgraph design for scalability

---

## 🏗️ Architecture

### LangGraph Workflow Structure

```mermaid
graph TB
    Start([Start]) --> Intent[Intent Classifier]
    Intent --> Resume[Resume Subgraph]
    Intent --> JobSearch[Job Search Subgraph]
    Intent --> Interview[Interview Subgraph]
    
    Resume --> Parse[Parse Resume]
    Parse --> Analyze[Analyze Quality]
    Analyze --> Validate[Validate Data]
    Validate --> Complete1[Complete]
    
    JobSearch --> Search[Search Jobs]
    Search --> Select[Select Job]
    Select --> Match[Analyze Match]
    Match --> Complete2[Complete]
    
    Interview --> Generate[Generate Questions]
    Generate --> Init[Initialize Session]
    Init --> Conduct[Conduct Question]
    Conduct --> Record[Record Response]
    Record --> Transcribe[Transcribe Audio]
    Transcribe --> Feedback[Generate Feedback]
    Feedback --> Next{More Questions?}
    Next -->|Yes| Conduct
    Next -->|No| Finalize[Finalize Interview]
    Finalize --> Complete3[Complete]
    
    Complete1 --> End([End])
    Complete2 --> End
    Complete3 --> End
    
    style Intent fill:#6C63FF
    style Resume fill:#4A90E2
    style JobSearch fill:#FFB81C
    Style Interview fill:#7B68EE
```

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Resume   │  │   Job    │  │Interview │  │  Saved   │   │
│  │ Analysis │  │  Search  │  │   Prep   │  │   Jobs   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
┌───────▼─────────────▼─────────────▼─────────────▼──────────┐
│              LangGraph Master Orchestrator                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Intent Classification & Routing             │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │   Resume     │ │     Job      │ │   Interview      │   │
│  │  Subgraph    │ │  Subgraph    │ │   Subgraph       │   │
│  └──────────────┘ └──────────────┘ └──────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Checkpoint Persistence Layer               │   │
│  │         (MemorySaver / SQLite Saver)                │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                     Tool Execution Layer                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │   Groq     │  │  SERP API  │  │    Deepgram STT/TTS   │ │
│  │    LLM     │  │ Job Search │  │  (Audio Processing)    │ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.12+** (recommended)
- **uv** package manager ([Installation guide](https://github.com/astral-sh/uv))
- API Keys for:
  - [Groq](https://console.groq.com/) (LLM inference)
  - [SerpAPI](https://serpapi.com/) (job search)
  - [Deepgram](https://deepgram.com/) (speech-to-text/text-to-speech)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/SatyamPant/JobMittar.git
   cd JobMittar
   ```

2. **Install dependencies using uv**
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e . # OR uv sync
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   SERPAPI_API_KEY=your_serpapi_api_key_here
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   ENVIRONMENT=dev  # or prod
   ```

4. **Run the application**
   ```bash
   # Standard mode (without LangGraph workflow visualization)
   streamlit run app.py
   
   # OR with full LangGraph orchestration
   streamlit run workflow.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:8501`

---

## 📖 Usage Guide

### 1️⃣ Resume Analysis

1. **Upload your resume** (PDF, DOCX, or TXT format)
2. The system will:
   - Extract structured information (contact, skills, experience, education)
   - Analyze resume quality with AI feedback
   - Provide ATS optimization recommendations
   - Identify strengths and improvement areas

**Example Output:**
```
✅ Strengths:
  • Strong technical skills in Python, Machine Learning, and AWS
  • Quantified achievements with measurable impact
  • Clear career progression demonstrated

⚠️ Areas to Improve:
  • Add more industry-specific keywords for ATS optimization
  • Include certifications to strengthen credentials
  • Expand leadership experience descriptions
```

### 2️⃣ Job Search

#### Resume-Based Search
- Automatically extracts top skills from your resume
- Searches across multiple job platforms
- Returns personalized job matches

#### Custom Search
- Select from 25+ common job titles
- Choose from global locations (Remote, US, India, UK, etc.)
- Filter by platform (LinkedIn, Indeed, Glassdoor, etc.)

#### Match Analysis
- **Match Score** (0-100%): Overall compatibility rating
- **Key Matches**: Skills and qualifications you possess
- **Gaps**: Missing requirements and areas to develop
- **Recommendations**: Actionable steps to improve candidacy

### 3️⃣ Interview Preparation

#### Question Generation
- Role-specific questions tailored to the job description
- Categories: Technical, Behavioral, Situational, General
- Difficulty levels: Easy, Medium, Hard
- Suggested answers and key points for each question

#### Live Interview Mode 🎙️
1. Click **"Start Live Interview"**
2. System generates audio for each question
3. **Record your response** using the microphone
4. Receive instant AI feedback:
   - **Confidence Score** (0-10): Delivery and composure
   - **Accuracy Score** (0-10): Content quality and correctness
   - Specific strengths and weaknesses
   - Actionable improvement suggestions

5. Navigate between questions and track progress
6. Download comprehensive interview report (Markdown format)

**Sample Feedback:**
```
Confidence: 8/10 | Accuracy: 7/10

Strengths:
✅ Clear articulation of technical concepts
✅ Good use of specific examples
✅ Demonstrated problem-solving approach

Weaknesses:
⚠️ Could expand on team collaboration aspects
⚠️ Missed discussing scalability considerations

Suggestions:
💡 Use the STAR method for more structured responses
💡 Prepare specific metrics to quantify achievements
```

---

## 🛠️ Technology Stack

### Core Framework
- **LangGraph 1.0.3**: Stateful workflow orchestration
- **LangChain**: LLM integration and prompt management
- **Streamlit 1.51.0**: Interactive web interface

### AI/ML Services
- **Groq (Llama 3.3 70B)**: Lightning-fast LLM inference
- **Instructor**: Structured output parsing with Pydantic
- **Deepgram Nova-2**: High-accuracy speech recognition and TTS

### Data & APIs
- **SerpAPI**: Real-time job search aggregation
- **PDFPlumber**: Intelligent PDF text extraction
- **python-docx**: DOCX file parsing

### Audio Processing
- **streamlit-mic-recorder**: Browser-based audio recording
- **Deepgram TTS/STT**: Professional voice synthesis and transcription

### State Management
- **LangGraph Checkpoints**: Persistent session state
- **Pydantic**: Type-safe data validation

---

## 🎨 Configuration

### Environment Modes

The application supports two configuration modes:

#### Development (`dev.yaml`)
- Optimized for testing and debugging
- Higher temperature for creative responses
- Detailed logging
- Shorter token limits

#### Production (`prod.yaml`)
- Optimized for accuracy and consistency
- Lower temperature for reliable outputs
- Extended token limits for comprehensive analysis
- Professional prompt templates

### Customizing Prompts

All prompts are centralized in `config/dev.yaml` and `config/prod.yaml`:

```yaml
prompts:
  resume_extraction: |
    Extract ALL information from this resume...
  
  interview_questions_generation: |
    Generate {question_count} high-quality interview questions...
  
  interview_feedback_generation: |
    Provide structured feedback with scores...
```

---

## 🔧 Advanced Features

### LangGraph Checkpointing

JobMittar uses LangGraph's checkpoint system for:
- **Session Persistence**: Resume workflows across page refreshes
- **State Recovery**: Pick up where you left off in interviews
- **Debugging**: Inspect workflow state at any point
- **Thread Management**: Isolated user sessions

```python
# Example: Checkpoint usage in interview workflow
thread_id = generate_interview_thread_id(job_title, user_id)
config = {"configurable": {"thread_id": thread_id}}

for state_update in graph.stream(initial_state, config=config):
    # Process each node execution
    # State automatically persisted at each step
```

### Structured Output with Instructor

All LLM responses are validated using Pydantic models:

```python
from models.interview import InterviewFeedback

feedback: InterviewFeedback = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    response_model=InterviewFeedback,  # Ensures type safety
    temperature=0.5
)
```

### Multi-Platform Job Search

Aggregates results from multiple sources:
- **LinkedIn**: Professional network jobs
- **Indeed**: Comprehensive job board
- **Glassdoor**: Company reviews + jobs
- **ZipRecruiter**: AI-matched positions
- **Monster**: Traditional job listings

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Follow existing code style (PEP 8)
   - Add tests for new features
   - Update documentation

4. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**

### Development Guidelines

- Use **uv** for dependency management
- Follow **Pydantic** models for data validation
- Add **docstrings** to all functions
- Keep **LangGraph nodes** modular and single-purpose
- Test **audio features** with real microphone input


---

## 🙏 Acknowledgments

- **LangChain Team**: For the powerful LangGraph framework
- **Groq**: For blazing-fast Llama 3.3 inference
- **Deepgram**: For state-of-the-art speech recognition
- **Streamlit**: For the intuitive web framework
- **SerpAPI**: For comprehensive job search aggregation

---

**Built with ❤️ using LangGraph, Streamlit, and AI**
