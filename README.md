# 🎯 CTF Security Lab - Comprehensive Cybersecurity Training Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.47.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Learn. Hack. Conquer. 🚀**

A full-featured Capture The Flag (CTF) platform with **13+ vulnerability types**, **AI-powered assistance**, **dynamic flags**, and **gamification**. Perfect for cybersecurity education, training, and competitions!

## ✨ Key Features

### 🔥 For Users
- **13+ Vulnerability Types**: SQL Injection, XSS, Command Injection, Path Traversal, LFI, RFI, XXE, CSRF, IDOR, and more!
- **Dynamic Secure Flags**: Each user gets unique, encrypted flags that require actual exploitation
- **Live Practice Lab**: Interactive vulnerable endpoints to practice exploitation safely
- **Steganography Challenges**: Image LSB, Base64, Morse Code, Classical Ciphers, Multi-layer encoding
- **AI Assistant**: Context-aware help powered by Google Gemini (remembers your progress!)
- **Gamification**: Leaderboards, achievements, memes, GIFs, and encouraging messages 🎉
- **Dynamic Frontend**: Beautiful Streamlit interface with real-time updates

### 👨‍💼 For Admins
- **MCP Orchestration Agent**: Llama.cpp powered tool to generate and manage challenges
- **Automated Challenge Creation**: AI generates complete challenges with code, hints, and solutions
- **Quality Review**: AI reviews challenges before deployment
- **User Analytics**: Analyze solving patterns and adjust difficulty
- **Batch Operations**: Create multiple challenges at once
- **Full Control Panel**: User management, statistics, cache control, maintenance mode

### 🔒 Security Features
- **Proof-of-Exploitation**: Users must prove they actually exploited the vulnerability
- **Multi-Layer Encryption**: Flags encrypted with user-specific keys
- **Rate Limiting**: Prevents abuse and ensures fair play
- **RBAC**: Role-based access control for admin functions
- **JWT Authentication**: Secure token-based auth with bcrypt

### ⚡ Performance
- **High Concurrency**: Designed for simultaneous users with rate limiting and caching
- **MongoDB Atlas**: Scalable cloud database
- **Async/Await**: Full async implementation for best performance
- **Connection Pooling**: Optimized database connections

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/djmahe4/ctf-mcp-agent.git
cd ctf-mcp-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required Configuration:**
- `MONGODB_URI`: MongoDB Atlas connection string
- `SECRET_KEY`: Random 32+ character string for JWT
- `GOOGLE_API_KEY`: Google API key for GenAI

**Optional:**
- `LLAMA_MODEL_PATH`: Path to Llama model for admin MCP (can skip for now)

### 3. Run the Platform

```bash
# Start backend server (Terminal 1)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (Terminal 2)
streamlit run frontend_user.py --server.port 8501
```

### 4. Access

- **Frontend**: http://localhost:8501 (User Interface)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 Comprehensive Documentation

See **[DOCUMENTATION.md](DOCUMENTATION.md)** for:
- 🏗️ Architecture Overview
- 🎯 User Guide (How to solve challenges)
- 👨‍💼 Admin Guide (How to manage platform)
- 🔧 API Reference (All endpoints)
- 🎨 Customization Guide
- 🔒 Security Best Practices
- 🐛 Troubleshooting

## 🎮 Available Vulnerabilities

| Vulnerability | Difficulty | Endpoints |
|---------------|-----------|-----------|
| SQL Injection | Easy-Medium | `/api/v1/vulnerabilities/sql-injection/*` |
| XSS (Reflected) | Medium | `/api/v1/vulnerabilities/xss/search` |
| XSS (Stored) | Medium | `/api/v1/vulnerabilities/xss/comment` |
| Command Injection | Hard | `/api/v1/vulnerabilities/command-injection/ping` |
| Path Traversal | Medium | `/api/v1/vulnerabilities/path-traversal/file` |
| Directory Traversal | Medium | `/api/v1/vulnerabilities/directory-traversal/read` |
| LFI | Medium-Hard | `/api/v1/vulnerabilities/lfi/include` |
| RFI | Hard | `/api/v1/vulnerabilities/rfi/load` |
| File Upload | Medium | `/api/v1/vulnerabilities/file-upload/vulnerable` |
| XXE | Hard | `/api/v1/vulnerabilities/xxe/parse` |
| IDOR | Easy-Medium | `/api/v1/vulnerabilities/idor/user/{id}` |
| Insecure Deserialization | Hard | `/api/v1/vulnerabilities/deserialization/vulnerable` |
| Open Redirect | Easy | `/api/v1/vulnerabilities/open-redirect/redirect` |
| Race Condition | Expert | `/api/v1/vulnerabilities/race-condition/transfer` |
| Clickjacking | Easy | `/api/v1/vulnerabilities/clickjacking/vulnerable-page` |
| HTTP Parameter Pollution | Medium | `/api/v1/vulnerabilities/hpp/search` |

## 🎨 Steganography Challenges

- **Base64**: Single, double, triple encoding + mixed (Base32, Base85)
- **Image Steganography**: LSB (Least Significant Bit) method
- **Classical Ciphers**: Caesar, ROT13
- **Encoding**: Binary, Hexadecimal, Morse Code
- **Multi-Layer**: Up to 7 encoding layers!

## 🤖 Admin MCP Agent

The **Model Context Protocol Agent** powered by Llama.cpp helps admins:

```bash
# Generate a challenge
POST /api/v1/mcp-orchestration/orchestrate/create-challenge
{
  "vulnerability_type": "sql_injection",
  "difficulty": "medium",
  "description": "E-commerce search function"
}

# Review challenge quality
POST /api/v1/mcp-orchestration/orchestrate/review-challenge

# Analyze user patterns
POST /api/v1/mcp-orchestration/orchestrate/analyze-user-patterns
```

## 🧠 Google GenAI Integration

Context-aware AI assistant for users:

```bash
POST /api/v1/genai/help
{
  "question": "How do I test for SQL injection?",
  "challenge_id": "sql_001"
}
```

The AI remembers:
- Your current challenge
- Previous questions
- Your skill level
- Challenges you've solved

## 📊 Project Structure

```
ctf-mcp-agent/
├── main.py                 # FastAPI application
├── frontend_user.py        # Streamlit user interface
├── models.py              # Pydantic models (50+ models!)
├── routers/               # API endpoints
│   ├── auth.py           # Authentication
│   ├── challenges.py     # Challenge management
│   ├── vulnerabilities.py # Vulnerable endpoints
│   ├── stego.py          # Steganography challenges
│   ├── admin.py          # Admin panel
│   ├── mcp_agent.py      # MCP orchestration
│   ├── eisenhower.py     # Task prioritization
│   └── leaderboard.py    # Rankings
├── auth_utils.py          # JWT & password hashing
├── flag_generator.py      # Dynamic flag generation
├── secure_flags.py        # Flag encryption & verification
├── genai_service.py       # Google GenAI integration
├── llama_service.py       # Llama.cpp MCP service
├── performance.py         # Rate limiting & caching
├── rbac.py               # Role-based access control
├── stego_utils.py        # Steganography utilities
├── stego_models.py       # Stego-specific models
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── DOCUMENTATION.md      # Full documentation
```

## 🛠️ Technology Stack

- **Backend**: FastAPI 0.115.0
- **Database**: MongoDB Atlas (Motor async driver)
- **Frontend**: Streamlit 1.47.0
- **AI**: Google Gemini 2.0 + Llama.cpp
- **Auth**: JWT with bcrypt
- **Security**: Cryptography, python-jose
- **Validation**: Pydantic 2.11.7
- **Image Processing**: Pillow (for steganography)

## 🎓 Learning Resources

Integrated in the platform:
- 💡 Progressive hints system
- 🧠 AI-powered explanations
- 📚 Vulnerability documentation
- 🛠️ Tool recommendations
- 🎯 Challenge walkthroughs (for admins)

External resources linked:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PortSwigger Academy](https://portswigger.net/web-security)
- [HackTheBox](https://www.hackthebox.com/)

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

## 🔐 Security Note

This platform contains **intentionally vulnerable** code for educational purposes. 

⚠️ **DO NOT deploy vulnerable endpoints to production without proper isolation!**

Use in controlled environments for training purposes only.

## 🎉 Get Started Now!

```bash
# Quick start
git clone https://github.com/djmahe4/ctf-mcp-agent.git
cd ctf-mcp-agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn main:app --reload
# In another terminal:
streamlit run frontend_user.py
```

Visit http://localhost:8501 and start hacking! 🚀

---

**Made with ❤️ for the cybersecurity community**

**Remember: Learn responsibly. Only hack systems you have permission to test!**

<!-- [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gemini-pydantic.streamlit.app/) -->

## ✨ Key Features

*   **Multi-Use-Case Playground:** Explore several pre-built tasks to see different applications of GenAI.
*   **Dynamic Prompt Engineering:** See how prompts are tailored for specific tasks.
*   **Pydantic Data Validation:** Every output from the AI is rigorously validated against a Pydantic model, ensuring the data is structured, typed, and correct.
*   **Schema-Driven Generation:** The application sends the Pydantic model's JSON schema directly within the prompt, instructing the Gemini model to return a perfectly formatted response.
*   **Secure API Key Management:** Uses a `.env` file to safely manage your Google API key.
*   **Extensible by Design:** Easily add your own custom use cases by defining a new Pydantic model and a prompt template.

---

## 🚀 Use Cases Explored

This application comes with several pre-configured examples:

1.  **Text Summarization:** Condenses a long piece of text into a concise summary and extracts relevant keywords.
2.  **Sentiment Analysis:** Analyzes a block of text to determine if the sentiment is positive, negative, or neutral, and provides a confidence score.
3.  **Entity Extraction (NER):** Identifies and extracts named entities like people, organizations, and locations from text.
4.  **Recipe Generator:** Creates a complete recipe with a dish name, ingredient list, and step-by-step instructions from a simple prompt.
5.  **LLM Training Dataset Generation:** Converts a source text into a list of high-quality Question/Answer pairs, suitable for fine-tuning a language model.

 <!-- Replace with a real screenshot URL -->

---

## 🛠️ Tech Stack

*   **Language:** Python 3.9+
*   **Framework:** [Streamlit](https://streamlit.io/) - for the interactive web UI.
*   **Generative AI:** [Google Gemini Pro](https://deepmind.google/technologies/gemini/) via the `google-generativeai` library.
*   **Data Validation:** [Pydantic V2](https://docs.pydantic.dev/) - for defining data schemas and validating API outputs.
*   **Configuration:** `python-dotenv` - for managing environment variables.

---

## ⚙️ Setup and Installation

Follow these steps to run the application locally.

### 1. Prerequisites
*   Python 3.9 or higher.
*   A Google API Key for the Gemini model. You can obtain one from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 2. Clone the Repository
```bash
git clone https://github.com/djmahe4/gemini-pydantic
cd gemini-pydantic
```

### 3. Set Up Your Environment Variable
Create a file named `.env` in the root of the project directory. Add your Google API key to this file:
```
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```
**Note:** The `.env` file is included in `.gitignore` to prevent you from accidentally committing your secret key.

### 4. Install Dependencies
Install all the required Python libraries using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Once the setup is complete, you can run the Streamlit application with a single command:

```bash
streamlit run streamlit_app.py
```

This will start a local server and open the application in your default web browser.

---

## 💡 How It Works

The application follows a simple but powerful workflow for each use case:

1.  **Select a Use Case:** The user chooses a task from the sidebar (e.g., "Sentiment Analysis").
2.  **Load Configuration:** The app loads the corresponding Pydantic model (`SentimentAnalysis`), a prompt template, and UI labels from a central `USE_CASES` dictionary.
3.  **Inject Schema into Prompt:** The Pydantic model's JSON schema is generated using `.schema_json()`. This schema is embedded directly into the prompt sent to Gemini, instructing the AI on the exact format for its response.
4.  **API Call:** The formatted prompt, including the user's input text, is sent to the Gemini API.
5.  **Validate and Parse:** When Gemini returns a response, the application attempts to parse the JSON string directly into an instance of the `SentimentAnalysis` Pydantic model.
    *   **On Success:** If the response matches the schema, the data is successfully validated and a clean Python object is created.
    *   **On Failure:** If the JSON is malformed or misses required fields, Pydantic raises a validation error, which is caught and displayed to the user.
6.  **Display Results:** The validated, structured data object is displayed in the UI.

---

## 🧩 How to Add a New Use Case

The application is designed to be easily extensible. To add your own custom functionality, follow these two steps:

### Step 1: Define a New Pydantic Model
In `app.py`, define a new class that inherits from `BaseModel`. This class represents the data structure you want the AI to return.

**Example: A "Code Review" model**
```python
class CodeReview(BaseModel):
    is_clean: bool = Field(description="Whether the code follows best practices.")
    suggestions: List[str] = Field(description="A list of specific suggestions for improvement.")
    overall_rating: int = Field(description="A rating from 1 (poor) to 5 (excellent).")
```

### Step 2: Add the Configuration to `USE_CASES`
In `app.py`, add a new key-value pair to the `USE_CASES` dictionary. This entry links your new model to a prompt template and UI text.

```python
# Inside the USE_CASES dictionary
"Code Review": {
    "model": CodeReview,  # Link to your new Pydantic model
    "prompt_template": """
        Act as an expert code reviewer. Analyze the following code snippet.
        Your output must be a JSON object that strictly adheres to this schema:
        ```json
        {schema}
        ```
        Text to analyze:
        ---
        {user_input}
        ---
    """,
    "input_label": "Enter a code snippet for review...",
    "default_input": "def my_func(a,b):\n  return a+ b"
}
```

Save the file, and your Streamlit app will automatically reload with "Code Review" as a new, fully functional option in the dropdown menu.

---

## 📄 License

> _This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details._
