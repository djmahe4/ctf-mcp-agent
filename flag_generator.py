"""
Dynamic Flag Generation Utilities
Generates unique flags for each user and challenge exploitation with enhanced randomness
"""

import hashlib
import secrets
import hmac
import base64
from datetime import datetime
from typing import Optional


def _multi_hash(data: str, salt: str = "") -> str:
    """
    Apply multiple hashing algorithms for enhanced security
    
    Args:
        data: Data to hash
        salt: Optional salt for hashing
    
    Returns:
        Multi-hashed string
    """
    # First pass: SHA256
    hash1 = hashlib.sha256((data + salt).encode()).hexdigest()
    
    # Second pass: SHA512 on result
    hash2 = hashlib.sha512(hash1.encode()).hexdigest()
    
    # Third pass: BLAKE2b for final hash
    hash3 = hashlib.blake2b(hash2.encode(), digest_size=32).hexdigest()
    
    return hash3


def _generate_random_component(user_id: str, challenge_name: str) -> str:
    """
    Generate a random component based on user ID and challenge name
    
    Args:
        user_id: User identifier
        challenge_name: Challenge name
    
    Returns:
        Random component string
    """
    # Create unique seed from user and challenge
    seed_data = f"{user_id}:{challenge_name}:{secrets.token_hex(8)}"
    
    # Use HMAC for deterministic but secure randomness
    hmac_key = hashlib.sha256(user_id.encode()).digest()
    hmac_result = hmac.new(hmac_key, challenge_name.encode(), hashlib.sha256).hexdigest()
    
    # Mix with timestamp-based entropy
    time_entropy = int(datetime.utcnow().timestamp() * 1000) % 999999
    
    # Combine for final random component
    combined = f"{hmac_result[:8]}{time_entropy:06d}"
    final_hash = hashlib.sha256(combined.encode()).hexdigest()[:12]
    
    return final_hash


def generate_dynamic_flag(
    user_id: str,
    challenge_id: str,
    vulnerability_type: str,
    challenge_name: str = "",
    timestamp: Optional[datetime] = None
) -> str:
    """
    Generate a unique flag for a user's successful exploitation with enhanced randomness
    
    Args:
        user_id: User's unique identifier
        challenge_id: Challenge identifier
        vulnerability_type: Type of vulnerability exploited
        challenge_name: Name of the challenge
        timestamp: Optional timestamp (defaults to now)
    
    Returns:
        Dynamically generated flag string with randomness
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # Create base seed from user, challenge, and time
    base_seed = f"{user_id}:{challenge_id}:{timestamp.strftime('%Y%m%d%H')}"
    
    # Add challenge name to seed for uniqueness
    if challenge_name:
        base_seed += f":{challenge_name}"
    
    # Generate multi-layer hash
    primary_hash = _multi_hash(base_seed, salt=vulnerability_type)[:16]
    
    # Generate random component based on user ID and challenge name
    random_component = _generate_random_component(user_id, challenge_name or challenge_id)
    
    # Create user-specific hash
    user_hash = hashlib.blake2b(user_id.encode(), digest_size=8).hexdigest()[:8]
    
    # Format based on vulnerability type
    vuln_prefix = {
        "sql_injection": "SQL",
        "xss": "XSS",
        "command_injection": "CMD",
        "path_traversal": "PATH",
        "csrf": "CSRF",
        "idor": "IDOR",
        "xxe": "XXE",
        "ssrf": "SSRF",
        "insecure_deserialization": "DESER"
    }.get(vulnerability_type, "CTF")
    
    # Combine all components for unique flag
    flag_components = f"{vuln_prefix}_{primary_hash}_{random_component}_{user_hash}"
    
    return f"FLAG{{{flag_components}}}"


def generate_session_flag(
    session_id: str, 
    vulnerability_type: str, 
    challenge_name: str = ""
) -> str:
    """
    Generate a flag for the current session with enhanced randomness
    
    Args:
        session_id: Session identifier
        vulnerability_type: Type of vulnerability
        challenge_name: Challenge name for uniqueness
    
    Returns:
        Session-specific flag with randomness
    """
    # Multi-layer hashing for session flag
    base_hash = _multi_hash(f"{session_id}:{vulnerability_type}:{challenge_name}")[:16]
    
    # Add session-specific randomness
    random_part = _generate_random_component(session_id, challenge_name)
    
    return f"FLAG{{{vulnerability_type.upper()}_{base_hash}_{random_part[:8]}}}"


def generate_time_based_flag(
    user_id: str, 
    vulnerability_type: str,
    challenge_name: str = ""
) -> str:
    """
    Generate a time-based flag that changes every hour with randomness
    
    Args:
        user_id: User identifier
        vulnerability_type: Vulnerability type
        challenge_name: Challenge name
    
    Returns:
        Time-based flag with randomness
    """
    current_hour = datetime.utcnow().strftime("%Y%m%d%H")
    
    # Create complex seed
    seed = f"{user_id}:{vulnerability_type}:{current_hour}:{challenge_name}"
    
    # Multi-hash with salt
    flag_hash = _multi_hash(seed, salt=user_id)[:20]
    
    # Add random component
    random_part = _generate_random_component(user_id, challenge_name)[:8]
    
    return f"FLAG{{{flag_hash.upper()}_{random_part.upper()}}}"


def verify_dynamic_flag(
    submitted_flag: str,
    user_id: str,
    challenge_id: str,
    vulnerability_type: str,
    challenge_name: str = "",
    time_window_hours: int = 24
) -> bool:
    """
    Verify a dynamically generated flag within a time window
    
    Args:
        submitted_flag: Flag submitted by user
        user_id: User identifier
        challenge_id: Challenge identifier
        vulnerability_type: Vulnerability type
        challenge_name: Challenge name
        time_window_hours: Hours to check backwards
    
    Returns:
        True if flag is valid within time window
    """
    current_time = datetime.utcnow()
    
    # Check flags for past N hours
    for hours_ago in range(time_window_hours):
        check_time = current_time.replace(minute=0, second=0, microsecond=0)
        check_time = check_time.replace(hour=current_time.hour - hours_ago)
        
        expected_flag = generate_dynamic_flag(
            user_id=user_id,
            challenge_id=challenge_id,
            vulnerability_type=vulnerability_type,
            challenge_name=challenge_name,
            timestamp=check_time
        )
        
        if submitted_flag == expected_flag:
            return True
    
    return False


def generate_challenge_specific_flag(
    user_id: str,
    challenge_name: str,
    difficulty: str = "medium"
) -> str:
    """
    Generate a flag specific to challenge name with maximum randomness
    
    Args:
        user_id: User identifier
        challenge_name: Full challenge name
        difficulty: Challenge difficulty
    
    Returns:
        Highly randomized challenge-specific flag
    """
    # Create complex seed with all parameters
    seed = f"{user_id}:{challenge_name}:{difficulty}:{datetime.utcnow().isoformat()}"
    
    # Apply multiple hashing layers
    hash_layer1 = hashlib.sha512(seed.encode()).hexdigest()
    hash_layer2 = hashlib.blake2b(hash_layer1.encode(), digest_size=32).hexdigest()
    
    # Generate HMAC-based random component
    hmac_key = user_id.encode()
    hmac_val = hmac.new(hmac_key, challenge_name.encode(), hashlib.sha256).hexdigest()[:12]
    
    # Mix with entropy
    entropy = secrets.token_hex(6)
    
    # Final hash combination
    final_hash = _multi_hash(f"{hash_layer2}:{hmac_val}:{entropy}")[:16]
    
    # Format challenge name for flag (sanitized)
    sanitized_name = challenge_name.replace(" ", "_").upper()[:20]
    
    return f"FLAG{{{sanitized_name}_{final_hash}_{hmac_val[:8]}}}"


def generate_easter_egg_flag(hint: str = "you_found_me") -> str:
    """
    Generate a special easter egg flag
    
    Args:
        hint: Hint text for the easter egg
    
    Returns:
        Easter egg flag
    """
    random_suffix = secrets.token_hex(6)
    return f"FLAG{{EASTER_EGG_{hint}_{random_suffix}}}"


def generate_bonus_flag(achievement: str, user_id: str) -> str:
    """
    Generate a bonus achievement flag
    
    Args:
        achievement: Achievement name
        user_id: User identifier
    
    Returns:
        Bonus flag
    """
    achievement_hash = hashlib.md5(f"{achievement}:{user_id}".encode()).hexdigest()[:10]
    return f"FLAG{{BONUS_{achievement.upper()}_{achievement_hash}}}"
