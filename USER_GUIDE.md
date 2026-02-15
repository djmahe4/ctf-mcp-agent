# 🎮 CTF Lab User Guide - Finding Flags & Scoring

## 📋 Table of Contents
- [User Registration & Login](#user-registration--login)
- [How to Find Flags](#how-to-find-flags)
- [Flag Submission & Verification](#flag-submission--verification)
- [Score System](#score-system)
- [Database Operations](#database-operations)

---

## 👤 User Registration & Login

### Step 1: Register a New Account

**Endpoint:** `POST /api/v1/auth/register`

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "hacker123",
    "email": "hacker@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "user_abc123",
  "username": "hacker123"
}
```

### Step 2: Login to Get Access Token

**Endpoint:** `POST /api/v1/auth/login`

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "hacker123",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "user_abc123",
  "username": "hacker123"
}
```

**💡 Important:** Save the `access_token` - you'll need it for all subsequent requests!

### Step 3: Use Token in Requests

For all authenticated endpoints, include the token:

```bash
curl -X GET http://localhost:8000/api/v1/challenges \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## 🔍 How to Find Flags

### The Flag Discovery Process

```
┌─────────────────────────────────────────────────────────────┐
│  1. LIST CHALLENGES → 2. SELECT CHALLENGE → 3. EXPLOIT      │
│  4. GET ENCRYPTED FLAG → 5. DECRYPT → 6. SUBMIT → 7. SCORE! │
└─────────────────────────────────────────────────────────────┘
```

### Step 1: Browse Available Challenges

**Endpoint:** `GET /api/v1/challenges`

```bash
curl -X GET http://localhost:8000/api/v1/challenges \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "challenges": [
    {
      "id": "sqli_basic_001",
      "title": "SQL Injection - Login Bypass",
      "description": "Bypass the login form using SQL injection",
      "vulnerability_type": "sql_injection",
      "difficulty": "easy",
      "points": 100,
      "category": "web",
      "solved_by_user": false
    },
    {
      "id": "xss_reflected_001",
      "title": "Reflected XSS",
      "description": "Find and exploit reflected XSS vulnerability",
      "vulnerability_type": "xss",
      "difficulty": "medium",
      "points": 150,
      "category": "web",
      "solved_by_user": false
    }
  ]
}
```

### Step 2: Start a Challenge

**Endpoint:** `POST /api/v1/challenges/{challenge_id}/start`

```bash
curl -X POST http://localhost:8000/api/v1/challenges/sqli_basic_001/start \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "message": "Challenge started!",
  "challenge_id": "sqli_basic_001",
  "vulnerability_endpoint": "/api/v1/vulnerabilities/sql-injection/login",
  "hint": "🔍 Try common SQL injection payloads in the username field",
  "started_at": "2026-02-13T12:00:00Z"
}
```

### Step 3: Exploit the Vulnerability

**Example: SQL Injection**

**Endpoint:** `POST /api/v1/vulnerabilities/sql-injection/login`

```bash
# Normal attempt (won't work)
curl -X POST http://localhost:8000/api/v1/vulnerabilities/sql-injection/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'

# Exploitation attempt (SQL injection)
curl -X POST http://localhost:8000/api/v1/vulnerabilities/sql-injection/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin'\'' OR '\''1'\''='\''1'\'' --",
    "password": "anything"
  }'
```

**Response (when exploited successfully):**
```json
{
  "success": true,
  "message": "💉 SQL Injection successful!",
  "exploitation_proof": "7f3d9e8a2b...",
  "flag_system": {
    "encrypted_flag": "Z0FBQUFBQnBq...",
    "timestamp": "1707829200",
    "verification_hash": "a8f5f167c3...",
    "challenge_token": "3kR9mL2pQ...",
    "requires_exploitation": true,
    "decoy_data": ["fake1...", "fake2...", "fake3..."],
    "message": "🔒 Exploit vulnerability to reveal flag"
  },
  "meme": "https://media.giphy.com/media/YQitE4YNQNahy/giphy.gif"
}
```

### Step 4: Decrypt the Flag

**CRITICAL:** The flag is ENCRYPTED! You must prove exploitation to decrypt it.

**Endpoint:** `POST /api/v1/challenges/{challenge_id}/decrypt-flag`

```bash
curl -X POST http://localhost:8000/api/v1/challenges/sqli_basic_001/decrypt-flag \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "encrypted_flag": "Z0FBQUFBQnBq...",
    "exploitation_proof": "7f3d9e8a2b...",
    "timestamp": "1707829200",
    "verification_hash": "a8f5f167c3..."
  }'
```

**Response:**
```json
{
  "success": true,
  "flag": "CTF{sql_1nj3ct10n_m4st3r}",
  "message": "🎉 Flag decrypted! Submit it to earn points!"
}
```

### Step 5: Submit the Flag

**Endpoint:** `POST /api/v1/challenges/{challenge_id}/submit`

```bash
curl -X POST http://localhost:8000/api/v1/challenges/sqli_basic_001/submit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "flag": "CTF{sql_1nj3ct10n_m4st3r}"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "🎉 Correct flag! You earned 100 points!",
  "points_earned": 100,
  "total_score": 100,
  "rank": 42,
  "badge": "SQL Ninja 🥷",
  "fun_fact": "SQL injection has been in the OWASP Top 10 since 2003!"
}
```

---

## 🔐 Flag Security & Network Sniffing Protection

### Why Flags Are Encrypted

```
┌──────────────────────────────────────────────────────────────┐
│  🚫 PROBLEM: Simple API flags can be stolen via network     │
│             sniffing or API interception                     │
│                                                              │
│  ✅ SOLUTION: Multi-layer encrypted flags that require      │
│             actual exploitation proof to decrypt             │
└──────────────────────────────────────────────────────────────┘
```

### Flag Protection Layers

1. **User-Specific Encryption**
   - Each user gets a different encrypted flag
   - Prevents flag sharing between users
   - Keys derived from: `hash(user_id + challenge_id + timestamp + master_secret)`

2. **Exploitation Proof Required**
   - Must prove you actually exploited the vulnerability
   - Cannot decrypt without valid exploitation proof
   - Proof is generated during actual exploit

3. **Time-Based Validity**
   - Flags have 1-hour decryption window
   - Prevents replay attacks
   - Forces fresh exploitation

4. **HMAC Verification**
   - All requests verified with HMAC signatures
   - Prevents tampering
   - Timing-safe comparisons

5. **Decoy Data Injection**
   - Real encrypted flag mixed with decoy data
   - Confuses network sniffers
   - Multiple fake flags returned

6. **Noise Addition**
   - Random noise added to encrypted data
   - Prevents pattern analysis
   - Makes flags non-deterministic

### Example: Why Simple API Flags Fail

**❌ BAD (Old Way):**
```json
{
  "flag": "CTF{easy_to_steal}"
}
```
→ Attacker can sniff network and steal flag without exploitation!

**✅ GOOD (Our Way):**
```json
{
  "encrypted_flag": "Z0FBQUFBQnBq...",
  "requires_exploitation": true,
  "decoy_data": ["fake1", "fake2", "fake3"],
  "message": "Exploit to decrypt"
}
```
→ Attacker sees encrypted data, cannot decrypt without exploitation proof!

---

## 📊 Score System

### How Scoring Works

```
                    EXPLOIT → DECRYPT → SUBMIT → VERIFY → UPDATE SCORE
                       ↓         ↓         ↓        ↓          ↓
Database:        START_TIME  PROOF   CHECK_FLAG  VALIDATE  +POINTS
```

### Score Calculation

**Formula:**
```python
base_points = challenge.points  # e.g., 100
time_bonus = max(0, 50 - (solve_time_minutes / 2))  # Faster = more points
first_blood_bonus = 50 if first_to_solve else 0

total_points = base_points + time_bonus + first_blood_bonus
```

**Example:**
- Challenge: 100 base points
- Solved in 10 minutes: +45 time bonus
- First to solve: +50 first blood
- **Total: 195 points!**

### Point Values by Difficulty

| Difficulty | Base Points | Description |
|------------|-------------|-------------|
| Easy       | 100         | Beginner-friendly |
| Medium     | 200         | Requires knowledge |
| Hard       | 400         | Advanced techniques |
| Expert     | 800         | Elite skills |

### Achievements & Badges

Users earn badges for milestones:

| Badge | Requirement | Bonus |
|-------|-------------|-------|
| 🥉 First Blood | First to solve any challenge | +50 pts |
| 🥷 SQL Ninja | Solve 5 SQL injection challenges | +100 pts |
| 🎭 XSS Master | Solve 5 XSS challenges | +100 pts |
| 👑 CTF King | Top 10 on leaderboard | Title |
| 🔥 Speed Demon | Solve challenge in < 5 min | +75 pts |

---

## 💾 Database Operations

### MongoDB Collections

#### 1. **users** Collection

```javascript
{
  "_id": ObjectId("..."),
  "user_id": "user_abc123",
  "username": "hacker123",
  "email": "hacker@example.com",
  "password_hash": "$2b$12$...",  // bcrypt hashed
  "role": "user",  // or "admin", "moderator"
  "created_at": ISODate("2026-02-13T12:00:00Z"),
  "stats": {
    "total_score": 450,
    "challenges_solved": 3,
    "rank": 42,
    "badges": ["sql_ninja", "first_blood"]
  }
}
```

#### 2. **challenges** Collection

```javascript
{
  "_id": ObjectId("..."),
  "challenge_id": "sqli_basic_001",
  "title": "SQL Injection - Login Bypass",
  "description": "Bypass the login form",
  "vulnerability_type": "sql_injection",
  "difficulty": "easy",
  "points": 100,
  "category": "web",
  "flag_hash": "sha256_hash_of_flag",
  "created_by": "admin",
  "created_at": ISODate("2026-01-01T00:00:00Z"),
  "solver_count": 157
}
```

#### 3. **submissions** Collection

```javascript
{
  "_id": ObjectId("..."),
  "submission_id": "sub_xyz789",
  "user_id": "user_abc123",
  "challenge_id": "sqli_basic_001",
  "submitted_flag": "CTF{sql_1nj3ct10n_m4st3r}",
  "is_correct": true,
  "points_earned": 145,  // base + bonuses
  "time_taken_seconds": 600,  // 10 minutes
  "exploitation_proof": "7f3d9e8a2b...",
  "submitted_at": ISODate("2026-02-13T12:10:00Z"),
  "first_blood": false
}
```

#### 4. **leaderboard** Collection (Cached)

```javascript
{
  "_id": ObjectId("..."),
  "user_id": "user_abc123",
  "username": "hacker123",
  "total_score": 450,
  "challenges_solved": 3,
  "rank": 42,
  "badges": ["sql_ninja"],
  "last_solve": ISODate("2026-02-13T12:10:00Z"),
  "updated_at": ISODate("2026-02-13T12:10:01Z")
}
```

### Score Update Flow

```python
# Pseudo-code for score update
async def update_user_score(user_id: str, challenge_id: str, points: int):
    """
    Update user score in database after successful flag submission
    """
    
    # 1. Start transaction (atomic operation)
    async with db.start_session() as session:
        async with session.start_transaction():
            
            # 2. Update user stats
            await db.users.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "stats.total_score": points,
                        "stats.challenges_solved": 1
                    },
                    "$addToSet": {
                        "stats.solved_challenges": challenge_id
                    },
                    "$set": {
                        "stats.last_solve": datetime.utcnow()
                    }
                }
            )
            
            # 3. Create submission record
            await db.submissions.insert_one({
                "submission_id": generate_id(),
                "user_id": user_id,
                "challenge_id": challenge_id,
                "points_earned": points,
                "submitted_at": datetime.utcnow(),
                "is_correct": True
            })
            
            # 4. Update challenge solver count
            await db.challenges.update_one(
                {"challenge_id": challenge_id},
                {"$inc": {"solver_count": 1}}
            )
            
            # 5. Recalculate leaderboard
            await recalculate_leaderboard()
            
            # 6. Check for new badges
            new_badges = await check_badge_eligibility(user_id)
            if new_badges:
                await award_badges(user_id, new_badges)
            
    # 7. Invalidate cache
    await cache.delete(f"user_stats:{user_id}")
    await cache.delete("leaderboard:global")
    
    return {"success": True, "points": points}
```

### Database Queries

**Get User Stats:**
```python
user_stats = await db.users.find_one(
    {"user_id": user_id},
    {"stats": 1, "username": 1}
)
```

**Get Leaderboard:**
```python
leaderboard = await db.users.find(
    {},
    {"username": 1, "stats": 1}
).sort("stats.total_score", -1).limit(100).to_list(100)
```

**Check if User Solved Challenge:**
```python
solved = await db.submissions.find_one({
    "user_id": user_id,
    "challenge_id": challenge_id,
    "is_correct": True
})
```

**Get User's Solve History:**
```python
history = await db.submissions.find({
    "user_id": user_id,
    "is_correct": True
}).sort("submitted_at", -1).to_list(None)
```

---

## 🎯 Complete Example: Full User Flow

```bash
#!/bin/bash
# Complete CTF challenge solving flow

API="http://localhost:8000"
TOKEN=""

# 1. Register
echo "1. Registering user..."
RESPONSE=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "hacker123",
    "email": "hacker@example.com",
    "password": "SecurePass123!"
  }')
echo $RESPONSE

# 2. Login
echo "2. Logging in..."
TOKEN=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "hacker123",
    "password": "SecurePass123!"
  }' | jq -r '.access_token')
echo "Token: $TOKEN"

# 3. List challenges
echo "3. Listing challenges..."
curl -s -X GET "$API/api/v1/challenges" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 4. Start challenge
echo "4. Starting SQL injection challenge..."
curl -s -X POST "$API/api/v1/challenges/sqli_basic_001/start" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 5. Exploit vulnerability
echo "5. Exploiting SQL injection..."
EXPLOIT=$(curl -s -X POST "$API/api/v1/vulnerabilities/sql-injection/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin'\'' OR '\''1'\''='\''1'\'' --",
    "password": "anything"
  }')
echo $EXPLOIT | jq '.'

# 6. Extract encrypted flag data
ENCRYPTED_FLAG=$(echo $EXPLOIT | jq -r '.flag_system.encrypted_flag')
TIMESTAMP=$(echo $EXPLOIT | jq -r '.flag_system.timestamp')
HASH=$(echo $EXPLOIT | jq -r '.flag_system.verification_hash')
PROOF=$(echo $EXPLOIT | jq -r '.exploitation_proof')

# 7. Decrypt flag
echo "6. Decrypting flag..."
FLAG_RESPONSE=$(curl -s -X POST "$API/api/v1/challenges/sqli_basic_001/decrypt-flag" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"encrypted_flag\": \"$ENCRYPTED_FLAG\",
    \"exploitation_proof\": \"$PROOF\",
    \"timestamp\": \"$TIMESTAMP\",
    \"verification_hash\": \"$HASH\"
  }")
echo $FLAG_RESPONSE | jq '.'

FLAG=$(echo $FLAG_RESPONSE | jq -r '.flag')

# 8. Submit flag
echo "7. Submitting flag..."
curl -s -X POST "$API/api/v1/challenges/sqli_basic_001/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"flag\": \"$FLAG\"}" | jq '.'

# 9. Check updated score
echo "8. Checking score..."
curl -s -X GET "$API/api/v1/users/me" \
  -H "Authorization: Bearer $TOKEN" | jq '.stats'

echo "✅ Complete!"
```

---

## 📱 Using the Streamlit Frontend

Alternatively, use the user-friendly Streamlit interface:

```bash
# Start the frontend
streamlit run frontend_user.py
```

Then navigate to http://localhost:8501 and:

1. **Login** with your credentials
2. **Browse challenges** in the dashboard
3. **Click on a challenge** to see details
4. **Try exploitation** in the interactive lab
5. **Submit flag** through the UI
6. **View leaderboard** and your rank

---

## 🎓 Tips for Finding Flags

1. **Read the challenge description carefully** - hints are embedded!
2. **Start with easy challenges** - build up your skills
3. **Use the AI assistant** - ask for hints when stuck
4. **Check the vulnerability type** - research common exploits
5. **Look for obvious patterns** - flags often follow predictable locations
6. **Try common payloads first** - most basic ones work on easy challenges
7. **Document your process** - learn from what works and doesn't
8. **Join the community** - discuss techniques (without sharing flags!)

---

## ❓ FAQ

**Q: Can I share flags with others?**
A: No! Each user gets a unique encrypted flag. Sharing won't work.

**Q: What if I can't decrypt my flag?**
A: Ensure you saved the exploitation_proof from the exploit response. It's required for decryption.

**Q: How long do I have to solve a challenge?**
A: No time limit! But faster solves earn time bonuses.

**Q: Can I solve challenges multiple times?**
A: You can only earn points once per challenge, but you can practice anytime.

**Q: What if my exploit works but I don't get a flag?**
A: Check the response - you should get exploitation_proof. If not, the exploit may not have triggered correctly.

---

**🎉 Happy Hacking! Good luck finding those flags!**
