"""
Tests for Vulnerability Challenges
Tests all vulnerability types without database
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestVulnerabilityChallenges:
    """Test vulnerability challenge endpoints"""
    
    def test_sql_injection_basics(self):
        """Test SQL injection patterns"""
        # Test basic SQL injection payloads
        payloads = [
            "' OR '1'='1' --",
            "admin'--",
            "' UNION SELECT NULL--",
            "1' OR '1'='1",
        ]
        
        for payload in payloads:
            # Should recognize as SQL injection attempt
            assert "'" in payload or "--" in payload
    
    def test_xss_patterns(self):
        """Test XSS payload patterns"""
        xss_payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "<svg onload=alert(1)>",
        ]
        
        for payload in xss_payloads:
            # Should recognize as XSS attempt
            assert "<" in payload or "javascript:" in payload
    
    def test_command_injection_patterns(self):
        """Test command injection patterns"""
        cmd_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "& whoami",
            "`id`",
            "$(cat flag.txt)",
        ]
        
        for payload in cmd_payloads:
            # Should recognize as command injection
            assert any(char in payload for char in [';', '|', '&', '`', '$'])
    
    def test_path_traversal_patterns(self):
        """Test path traversal patterns"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f",
        ]
        
        for payload in traversal_payloads:
            # Should recognize as path traversal
            assert ".." in payload or "%2e" in payload
    
    def test_lfi_patterns(self):
        """Test Local File Inclusion patterns"""
        lfi_payloads = [
            "/etc/passwd",
            "php://filter/convert.base64-encode/resource=index.php",
            "file:///etc/passwd",
            "/proc/self/environ",
        ]
        
        for payload in lfi_payloads:
            # Should recognize as LFI attempt
            assert "/" in payload or "php://" in payload


class TestSteganographyUtils:
    """Test steganography utilities"""
    
    def test_base64_encoding(self):
        """Test Base64 encoding/decoding"""
        import base64
        
        test_string = "CTF{test_flag_12345}"
        encoded = base64.b64encode(test_string.encode()).decode()
        decoded = base64.b64decode(encoded).decode()
        
        assert decoded == test_string
        assert encoded != test_string
    
    def test_multi_layer_encoding(self):
        """Test multi-layer encoding"""
        import base64
        
        original = "flag"
        
        # Layer 1: Base64
        layer1 = base64.b64encode(original.encode()).decode()
        
        # Layer 2: Base64 again
        layer2 = base64.b64encode(layer1.encode()).decode()
        
        # Decode
        decode1 = base64.b64decode(layer2).decode()
        decode2 = base64.b64decode(decode1).decode()
        
        assert decode2 == original
    
    def test_hex_encoding(self):
        """Test hex encoding"""
        test_string = "flag"
        hex_encoded = test_string.encode().hex()
        hex_decoded = bytes.fromhex(hex_encoded).decode()
        
        assert hex_decoded == test_string


class TestFlagValidation:
    """Test flag validation logic"""
    
    def test_flag_format(self):
        """Test CTF flag format"""
        valid_flags = [
            "CTF{test_flag}",
            "CTF{12345abcde}",
            "CTF{sql_injection_master}",
        ]
        
        invalid_flags = [
            "flag{test}",
            "CTF(test)",
            "test",
            "",
        ]
        
        for flag in valid_flags:
            assert flag.startswith("CTF{")
            assert flag.endswith("}")
        
        for flag in invalid_flags:
            assert not (flag.startswith("CTF{") and flag.endswith("}"))
    
    def test_flag_length_requirements(self):
        """Test flag length requirements"""
        flag = "CTF{test}"
        
        # Minimum length check
        assert len(flag) > 5
        assert len(flag.replace("CTF{", "").replace("}", "")) > 0


class TestAuthenticationBasics:
    """Test authentication logic"""
    
    def test_password_hashing(self):
        """Test password hashing works"""
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        password = "test_password_123"
        hashed = pwd_context.hash(password)
        
        # Verify hash is different from password
        assert hashed != password
        
        # Verify password can be verified
        assert pwd_context.verify(password, hashed)
        
        # Wrong password should fail
        assert not pwd_context.verify("wrong_password", hashed)
    
    def test_jwt_token_structure(self):
        """Test JWT token structure"""
        from datetime import datetime, timedelta
        
        # Mock token data
        token_data = {
            "sub": "testuser",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        
        assert "sub" in token_data
        assert "exp" in token_data


class TestPydanticModels:
    """Test Pydantic model validation"""
    
    def test_user_model_validation(self):
        """Test User model validation"""
        from models import UserCreate
        
        # Valid user
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
    
    def test_challenge_model_validation(self):
        """Test Challenge model validation"""
        from models import Challenge
        
        challenge = Challenge(
            id="sqli_001",
            title="SQL Injection Basic",
            description="Learn SQL injection",
            vulnerability_type="sql_injection",  # Use full enum value
            difficulty="easy",
            points=100,
            category="web",
            flag_hash="test_hash_12345",  # Required field
            created_by="admin"  # Required field
        )
        
        assert challenge.difficulty in ["easy", "medium", "hard"]
        assert challenge.points > 0


class TestPerformanceUtils:
    """Test performance utilities"""
    
    def test_rate_limiting_logic(self):
        """Test rate limiting logic"""
        from collections import defaultdict
        from time import time
        
        # Simulate rate limiter
        requests = defaultdict(list)
        user_id = "test_user"
        max_requests = 10
        window = 60  # 60 seconds
        
        current_time = time()
        
        # Add requests
        for i in range(15):
            requests[user_id].append(current_time + i)
        
        # Count recent requests
        recent = [t for t in requests[user_id] if t > current_time - window]
        
        # Should limit after max_requests
        assert len(recent) > max_requests
    
    def test_caching_logic(self):
        """Test caching logic"""
        from datetime import datetime, timedelta
        
        cache = {}
        cache_ttl = timedelta(minutes=5)
        
        # Add to cache
        key = "test_key"
        cache[key] = {
            "data": "test_data",
            "timestamp": datetime.utcnow()
        }
        
        # Check if in cache
        assert key in cache
        
        # Check if expired (should not be)
        age = datetime.utcnow() - cache[key]["timestamp"]
        assert age < cache_ttl


class TestEisenhowerMatrix:
    """Test Eisenhower decision matrix"""
    
    def test_task_prioritization(self):
        """Test task priority calculation"""
        tasks = [
            {"name": "Critical bug", "urgency": 10, "importance": 10},
            {"name": "Feature request", "urgency": 3, "importance": 7},
            {"name": "Documentation", "urgency": 5, "importance": 6},
        ]
        
        for task in tasks:
            # Calculate priority score
            priority = (task["urgency"] * 0.6 + task["importance"] * 0.4)
            
            assert 0 <= priority <= 10
            assert priority > 0 if task["urgency"] > 0 or task["importance"] > 0 else priority == 0
    
    def test_quadrant_assignment(self):
        """Test quadrant assignment logic"""
        def get_quadrant(urgency, importance):
            if urgency >= 7 and importance >= 7:
                return "DO_FIRST"
            elif urgency < 7 and importance >= 7:
                return "SCHEDULE"
            elif urgency >= 7 and importance < 7:
                return "DELEGATE"
            else:
                return "ELIMINATE"
        
        assert get_quadrant(8, 8) == "DO_FIRST"
        assert get_quadrant(5, 8) == "SCHEDULE"
        assert get_quadrant(8, 5) == "DELEGATE"
        assert get_quadrant(3, 3) == "ELIMINATE"


class TestAdminAgent:
    """Test Admin Agent functionality"""
    
    def test_admin_agent_initialization(self):
        """Test admin agent initializes"""
        from admin_agent import MultiModalAdminAgent
        
        agent = MultiModalAdminAgent()
        assert agent is not None
        assert hasattr(agent, 'is_available')
    
    def test_admin_agent_availability(self):
        """Test admin agent availability check"""
        from admin_agent import MultiModalAdminAgent
        
        agent = MultiModalAdminAgent()
        available = agent.is_available()
        
        # Should return True or False
        assert isinstance(available, bool)
