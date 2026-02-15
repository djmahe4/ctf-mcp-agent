# 🎯 CTF Security Lab - Comprehensive Documentation

> **Latest Update:** Migrated to google-genai, added comprehensive test suite, vulnerability sandboxing, and CI/CD pipeline

## 📚 Documentation Index

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete guide for users on finding flags and scoring
- **[README.md](README.md)** - Quick start and overview
- **This Document** - Technical architecture and admin guide

## 🌟 Overview

**CTF Security Lab** is a production-ready Capture The Flag (CTF) platform designed for cybersecurity education and training. It combines multiple vulnerability types, AI-powered assistance (optional), secure flag systems, and gamification elements to create an engaging learning environment.

### ✨ Key Features

- 🔥 **16+ Vulnerability Types**: SQL Injection, XSS, Command Injection, Path Traversal, XXE, and more
- 🔒 **Secure Flag System**: Dynamically generated, encrypted flags with proof-of-exploitation
- 🎨 **Steganography Challenges**: Image LSB, Multi-layer encoding, Classical ciphers
- 🤖 **Admin MCP Agent** (Optional): Llama.cpp powered orchestration tool for challenge management
- 🧠 **Google GenAI Integration** (Optional): Context-aware help and code analysis
- 📊 **Eisenhower Matrix**: Task prioritization for learning paths
- 🏆 **Gamification**: Leaderboards, achievements, memes, and GIFs
- ⚡ **High Performance**: Rate limiting, caching, concurrent user support
- 🎨 **Dynamic Frontend**: Customizable Streamlit interface for users
- 🔐 **Vulnerability Sandboxing**: NO real file/command access - all simulated safely
- 🧪 **Comprehensive Testing**: 80+ tests ensuring security and functionality
- 🚀 **CI/CD Pipeline**: Automated testing, security scanning, and deployment

### 🎯 Design Philosophy

1. **Security First**: Flags protected from network sniffing, all vulnerabilities sandboxed
2. **Optional AI**: Platform works perfectly without AI - GenAI is enhancement only
3. **Educational**: Realistic vulnerabilities with explanations and learning resources
4. **Scalable**: Designed for concurrent users with MongoDB and caching
5. **Fun**: Memes, GIFs, achievements make learning enjoyable

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CTF SECURITY LAB                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐         ┌──────────────────┐                │
│  │   User Frontend  │────────▶│   FastAPI Server │                │
│  │   (Streamlit)    │         │   (Uvicorn)      │                │
│  └──────────────────┘         └────────┬─────────┘                │
│                                         │                           │
│                          ┌──────────────┼──────────────┐           │
│                          │              │              │           │
│                    ┌─────▼────┐  ┌─────▼────┐  ┌─────▼────┐      │
│                    │   Auth   │  │   API    │  │  Admin   │      │
│                    │  System  │  │ Routers  │  │  Panel   │      │
│                    └─────┬────┘  └─────┬────┘  └─────┬────┘      │
│                          │              │              │           │
│            ┌─────────────┴──────────────┴──────────────┴─────┐   │
│            │            Security & Business Logic            │   │
│            ├──────────────────────────────────────────────────┤   │
│            │  • Secure Flags (Encryption)                    │   │
│            │  • Vulnerability Sandbox (NO real access)       │   │
│            │  • Rate Limiting & Caching                      │   │
│            │  • RBAC (Role-Based Access Control)             │   │
│            │  • Performance Monitoring                        │   │
│            └────────┬──────────────┬────────────┬────────────┘   │
│                     │              │            │                 │
│          ┌──────────▼─┐    ┌──────▼───┐   ┌───▼─────────────┐  │
│          │  MongoDB   │    │  GenAI   │   │  Llama.cpp MCP  │  │
│          │  (Atlas)   │    │(Optional)│   │    (Optional)   │  │
│          └────────────┘    └──────────┘   └─────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Flag Security Flow

```
USER EXPLOITS → PROOF GENERATED → FLAG ENCRYPTED → STORED
                     ↓                    ↓            ↓
              HMAC SIGNATURE      USER-SPECIFIC KEY   MONGODB
                     ↓                    ↓            ↓
              VERIFICATION        DECOY DATA ADDED    CACHED
                     ↓                    ↓            ↓
           SUBMIT WITH PROOF    DECRYPT REQUIRED    VERIFY
                     ↓                    ↓            ↓
           TIMING-SAFE CHECK   HMAC VERIFICATION   UPDATE SCORE
```

### Database Schema

```
MongoDB Collections:
├── users
│   ├── user_id (unique)
│   ├── username, email, password_hash
│   ├── role (user/admin/moderator)
│   ├── stats: {total_score, challenges_solved, rank, badges}
│   └── created_at, last_login
├── challenges  
│   ├── challenge_id (unique)
│   ├── title, description, vulnerability_type
│   ├── difficulty, points, category
│   ├── flag_hash (never plaintext!)
│   └── solver_count, created_by
├── submissions
│   ├── submission_id (unique)
│   ├── user_id, challenge_id
│   ├── is_correct, points_earned
│   ├── exploitation_proof
│   └── submitted_at, time_taken
└── leaderboard (cached)
    ├── user_id, username
    ├── total_score, rank
    └── last_solve, updated_at
```

---
    └── Flag Generation System
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- MongoDB Atlas account (or local MongoDB)
- Google API Key (for GenAI)
- Llama.cpp model file (optional, for admin MCP)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/djmahe4/ctf-mcp-agent.git
cd ctf-mcp-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

**.env Configuration:**
```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=ctf_lab

# Security
SECRET_KEY=your-super-secret-jwt-key-min-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google GenAI
GOOGLE_API_KEY=your-google-api-key-here

# Llama.cpp (Admin MCP - Optional)
LLAMA_MODEL_PATH=models/llama-2-7b-chat.gguf
LLAMA_CTX_SIZE=2048
LLAMA_THREADS=4
LLAMA_GPU_LAYERS=0

# Server
PORT=8000
WORKERS=4
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000,http://localhost:8501

# API Base URL (for frontend)
API_BASE_URL=http://localhost:8000
```

5. **Start the backend server**
```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

6. **Start the user frontend (in another terminal)**
```bash
streamlit run frontend_user.py --server.port 8501
```

7. **Access the platform**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- User Frontend: http://localhost:8501

---

## 📚 Core Concepts

### 🔐 Secure Flag System

Flags are **NOT** simply stored or returned in API responses. Instead:

1. **Dynamic Generation**: Each user gets a unique flag based on:
   - User ID
   - Challenge ID
   - Challenge name
   - Timestamp
   - Multi-layer hashing

2. **Encryption**: Flags are encrypted with user-specific keys

3. **Proof-of-Exploitation**: Users must prove they actually exploited the vulnerability

4. **Challenge-Response**: Users receive a challenge token and must submit exploitation proof

**Flow:**
```
User exploits vulnerability
  ↓
Receives encrypted flag + challenge token
  ↓
Submits exploitation proof (payload hash)
  ↓
System verifies genuine exploitation
  ↓
User decrypts flag with verification
  ↓
Success! Flag revealed
```

### 🤖 MCP Agent (Admin Only)

The **Model Context Protocol (MCP) Agent** powered by Llama.cpp is an **admin orchestration tool**, NOT for end users.

**Admin Use Cases:**
- 🎯 Generate new challenges automatically
- 📊 Analyze challenge difficulty
- 💡 Create progressive hints
- ✅ Review challenge quality
- 📝 Generate solution guides
- 🔄 Batch create multiple challenges
- 📈 Analyze user solving patterns

**Access:** Only users with `admin` role can use `/api/v1/mcp-orchestration` endpoints.

### 🧠 Google GenAI (User Helper)

Context-aware AI assistant for **end users**:
- Provides hints without spoiling solutions
- Explains vulnerability concepts
- Suggests tools and techniques
- Personalizes help based on user progress
- Maintains conversation history

---

## 🎯 User Guide

### Registration & Login

1. Open the frontend: http://localhost:8501
2. Click "Register" tab
3. Create account with strong password (8+ chars, uppercase, digit)
4. Login with credentials

### Solving Challenges

1. **Browse Challenges**: View available challenges by difficulty/type
2. **Start Challenge**: Click "Start" to activate
3. **Practice**: Use the live vulnerability lab to test exploits
4. **Exploit**: Find and exploit the vulnerability
5. **Verify**: Submit exploitation proof
6. **Decrypt**: Get your unique flag
7. **Submit**: Enter the decrypted flag
8. **Celebrate**: Earn points and climb the leaderboard! 🎉

### Using AI Assistant

1. Go to "AI Assistant" tab
2. Ask questions about:
   - Challenge hints
   - Vulnerability concepts
   - Tools and techniques
3. Get personalized, context-aware responses

### Steganography Challenges

1. Navigate to "Steganography" tab
2. Choose encoding type (Base64, Hex, Morse, etc.)
3. Generate challenge
4. Decode the message
5. Submit decoded flag

---

## 👨‍💼 Admin Guide

### Setting Up MCP Agent

1. Download a compatible Llama model (e.g., Llama-2-7B)
2. Place in `models/` directory
3. Update `.env` with model path
4. Restart server
5. Verify at `/api/v1/mcp-orchestration/status`

### Generating Challenges

```bash
POST /api/v1/mcp-orchestration/orchestrate/create-challenge
{
  "vulnerability_type": "sql_injection",
  "difficulty": "medium",
  "description": "Banking application with user search"
}
```

### Reviewing Challenges

```bash
POST /api/v1/mcp-orchestration/orchestrate/review-challenge
{
  "challenge": {
    "title": "SQL Injection in Login",
    "vulnerability_type": "sql_injection",
    ...
  }
}
```

### Analyzing User Patterns

```bash
POST /api/v1/mcp-orchestration/orchestrate/analyze-user-patterns
{
  "challenge_id": "sql_001",
  "solve_times": [20, 35, 42, 18, 55],
  "attempt_counts": [3, 5, 2, 1, 8]
}
```

---

## 🔧 API Reference

### Authentication

#### Register
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "hacker123",
  "email": "hacker@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=hacker123&password=SecurePass123
```

Response:
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### Challenges

#### List Challenges
```bash
GET /api/v1/challenges/
Authorization: Bearer <token>
```

#### Submit Flag
```bash
POST /api/v1/challenges/{challenge_id}/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "challenge_id": "sql_001",
  "flag": "FLAG{SQL_abc123def456}"
}
```

### Vulnerabilities (Practice Lab)

#### SQL Injection
```bash
POST /api/v1/vulnerabilities/sql-injection/search?username=' OR '1'='1' --
Authorization: Bearer <token>
```

#### XSS
```bash
POST /api/v1/vulnerabilities/xss/comment
Authorization: Bearer <token>
Content-Type: application/json

{
  "comment": "<script>alert('XSS')</script>"
}
```

---

## 🎨 Customization

### Adding New Vulnerability Types

1. **Define Pydantic Model** in `models.py`:
```python
class NewVulnChallenge(BaseModel):
    challenge_id: str
    vuln_specific_field: str
    ...
```

2. **Create Router Endpoint** in `routers/vulnerabilities.py`:
```python
@router.post("/new-vuln/exploit", response_model=dict)
async def new_vuln_endpoint(...):
    # Implementation
    pass
```

3. **Add Frontend Interface** in `frontend_user.py`:
```python
def show_new_vuln_lab():
    st.subheader("New Vulnerability Practice")
    ...
```

### Customizing UI Theme

Edit `frontend_user.py` CSS:
```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(your-colors);
        ...
    }
</style>
""", unsafe_allow_html=True)
```

---

## 🔒 Security Best Practices

### For Deployment

1. **Environment Variables**: Never commit `.env` to version control
2. **Secret Key**: Generate strong random secret: `openssl rand -hex 32`
3. **CORS**: Restrict to specific origins in production
4. **Rate Limiting**: Already configured, adjust limits as needed
5. **HTTPS**: Always use HTTPS in production
6. **Database**: Use MongoDB Atlas with IP whitelist
7. **Admin Access**: Strictly limit admin role assignments

### MongoDB Security

```bash
# Create admin user
use admin
db.createUser({
  user: "ctf_admin",
  pwd: "strong_password",
  roles: ["readWrite", "dbAdmin"]
})
```

---

## 📊 Performance Tuning

### Rate Limiting

Configure in `.env`:
```bash
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Caching

Default TTL: 5 minutes (300 seconds)

Adjust in `performance.py`:
```python
cache_manager = CacheManager(default_ttl=300)
```

### Database Indexing

Indexes are created automatically on startup:
- `users.username` (unique)
- `users.email` (unique)
- `challenges.vulnerability_type`
- `submissions.user_id + challenge_id`

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: MongoDB connection failed
```
Solution: Check MONGODB_URI in .env, ensure MongoDB is running
```

**Issue**: Llama.cpp not loading
```
Solution: Check model path, ensure llama-cpp-python is installed correctly
For CPU-only: pip install llama-cpp-python
For GPU: CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

**Issue**: Frontend can't connect to backend
```
Solution: Ensure API_BASE_URL in .env matches backend address
Check CORS_ORIGINS includes frontend URL
```

**Issue**: Flag decryption fails
```
Solution: Ensure exploitation was verified first
Check that user actually exploited the vulnerability
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🎓 Learning Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **PortSwigger Academy**: https://portswigger.net/web-security
- **HackTheBox**: https://www.hackthebox.com/
- **TryHackMe**: https://tryhackme.com/
- **PicoCTF**: https://picoctf.org/

---

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@ctflab.example.com

---

## 🎉 Have Fun & Happy Hacking! 🚀

Remember: **Learn responsibly. Only hack systems you have permission to test!**
