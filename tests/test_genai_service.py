"""
Tests for GenAI Service
Tests both with and without AI available
"""
from genai_service import ContextAwareGenAI


class TestGenAIService:
    """Test GenAI service functionality"""
    
    def test_genai_initialization(self):
        """Test GenAI service initializes correctly"""
        service = ContextAwareGenAI()
        # Should work whether AI is available or not
        assert service is not None
        assert isinstance(service.conversations, dict)
        assert isinstance(service.user_contexts, dict)
    
    def test_genai_availability_check(self):
        """Test availability check works"""
        service = ContextAwareGenAI()
        # Should return True or False based on API key
        available = service.is_available()
        assert isinstance(available, bool)
    
    def test_update_user_context(self, mock_user, mock_challenge):
        """Test updating user context"""
        service = ContextAwareGenAI()
        user_id = mock_user["user_id"]
        
        service.update_user_context(
            user_id=user_id,
            challenge_id=mock_challenge["challenge_id"],
            vulnerability_type=mock_challenge["vulnerability_type"],
            attempt_count=3,
            last_error="Invalid SQL syntax",
            solved_challenges=["xss_001", "sqli_002"]
        )
        
        assert user_id in service.user_contexts
        context = service.user_contexts[user_id]
        assert context["challenge_id"] == mock_challenge["challenge_id"]
        assert context["vulnerability_type"] == "sqli"
        assert context["attempt_count"] == 3
        assert len(context["solved_challenges"]) == 2
    
    def test_static_hint_without_ai(self, mock_user):
        """Test that static hints work without AI"""
        service = ContextAwareGenAI()
        user_id = mock_user["user_id"]
        
        # Update context
        service.update_user_context(
            user_id=user_id,
            challenge_id="sqli_test",
            vulnerability_type="sqli",
            attempt_count=2
        )
        
        # Get static hint (bypasses AI)
        result = service._get_static_hint(user_id, "How do I exploit this?")
        
        assert result["success"] is True
        assert "response" in result
        assert "sqli" in result["response"].lower() or "SQL" in result["response"]
        assert result["static_hint"] is True
    
    def test_context_aware_hint(self, mock_user):
        """Test context-aware hint (works with or without AI)"""
        service = ContextAwareGenAI()
        user_id = mock_user["user_id"]
        
        service.update_user_context(
            user_id=user_id,
            challenge_id="xss_test",
            vulnerability_type="xss",
            attempt_count=1
        )
        
        result = service.get_context_aware_hint(
            user_id=user_id,
            user_question="What payload should I try?"
        )
        
        assert result["success"] is True
        assert "response" in result
        assert result["context_aware"] is True
    
    def test_code_vulnerability_analysis_fallback(self):
        """Test code analysis works without AI"""
        service = ContextAwareGenAI()
        
        code = """
        username = input("Username: ")
        query = f"SELECT * FROM users WHERE username = '{username}'"
        """
        
        result = service.analyze_code_vulnerability(
            code_snippet=code,
            vulnerability_type="sqli",
            language="python"
        )
        
        assert result["success"] is True
        assert "analysis" in result
        assert result["code_language"] == "python"
    
    def test_should_use_search_detection(self):
        """Test Google Search trigger detection"""
        service = ContextAwareGenAI()
        
        # Should trigger search
        assert service._should_use_search("What are the latest XSS techniques?", {})
        assert service._should_use_search("Which tools are recommended for SQLi?", {})
        assert service._should_use_search("CVE-2024-1234 details", {})
        assert service._should_use_search("Best practices for 2026", {})
        
        # Should NOT trigger search
        assert not service._should_use_search("How do I use this?", {})
        assert not service._should_use_search("Give me a hint", {})
    
    def test_multiple_vulnerability_types_static_hints(self):
        """Test static hints for different vulnerability types"""
        service = ContextAwareGenAI()
        
        vuln_types = ["sqli", "xss", "command_injection", "lfi", "csrf", "idor"]
        
        for vuln_type in vuln_types:
            service.update_user_context(
                user_id="test_user",
                vulnerability_type=vuln_type
            )
            
            result = service._get_static_hint("test_user", "Give me a hint")
            assert result["success"] is True
            assert len(result["response"]) > 0


class TestGenAIWithoutAPIKey:
    """Test that service works without API key"""
    
    def test_service_works_without_api_key(self, monkeypatch):
        """Test graceful degradation without API key"""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        
        service = ContextAwareGenAI()
        assert service is not None
        assert service.is_available() is False
    
    def test_all_methods_work_without_api(self, mock_user, monkeypatch):
        """Test all methods return valid responses without API"""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        
        service = ContextAwareGenAI()
        user_id = mock_user["user_id"]
        
        service.update_user_context(
            user_id=user_id,
            vulnerability_type="sqli"
        )
        
        # Test hint generation
        result = service.get_context_aware_hint(user_id, "Help me")
        assert result["success"] is True
        
        # Test code analysis
        result = service.analyze_code_vulnerability("SELECT * FROM users")
        assert result["success"] is True
