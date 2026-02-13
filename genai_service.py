"""
Google GenAI Context-Aware Service
Optional AI assistance using Google's Gemini - FALLBACK ONLY
Core platform functionality does NOT depend on this service
Integrated with Google Search for real-time information when needed
"""

from typing import List, Dict, Optional, Any
from google import genai
from google.genai import types
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class ContextAwareGenAI:
    """
    Context-aware AI assistant powered by Google Gemini
    OPTIONAL service - platform works fine without it
    Used only as fallback for enhanced user assistance
    """
    
    def __init__(self):
        """Initialize Google GenAI service - optional, may fail gracefully"""
        self.available = False
        self.client = None
        self.model_name = 'gemini-2.0-flash-exp'
        
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
                self.available = True
        except Exception as e:
            print(f"GenAI not available: {e}. Platform will work without AI assistance.")
        
        # Conversation history per user
        self.conversations: Dict[str, List[Dict]] = {}
        
        # Context tracking
        self.user_contexts: Dict[str, Dict[str, Any]] = {}
    
    def is_available(self) -> bool:
        """Check if GenAI service is available"""
        return self.available and self.client is not None
    
    def update_user_context(
        self,
        user_id: str,
        challenge_id: Optional[str] = None,
        vulnerability_type: Optional[str] = None,
        attempt_count: int = 0,
        last_error: Optional[str] = None,
        solved_challenges: Optional[List[str]] = None
    ):
        """
        Update user's current context
        
        Args:
            user_id: User identifier
            challenge_id: Current challenge
            vulnerability_type: Type of vulnerability
            attempt_count: Number of attempts
            last_error: Last error message
            solved_challenges: List of solved challenges
        """
        self.user_contexts[user_id] = {
            "challenge_id": challenge_id,
            "vulnerability_type": vulnerability_type,
            "attempt_count": attempt_count,
            "last_error": last_error,
            "solved_challenges": solved_challenges or [],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_context_aware_hint(
        self,
        user_id: str,
        user_question: str,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """
        Generate context-aware hint using user's current situation
        FALLBACK ONLY - returns static hints if GenAI unavailable
        
        Args:
            user_id: User identifier
            user_question: User's question
            include_history: Include conversation history
        
        Returns:
            AI-generated contextual response or static fallback
        """
        # Check if GenAI is available
        if not self.is_available():
            return self._get_static_hint(user_id, user_question)
        
        # Get user context
        context = self.user_contexts.get(user_id, {})
        
        # Build context-aware prompt
        prompt = self._build_contextual_prompt(user_id, user_question, context)
        
        try:
            # Determine if we should use Google Search for this query
            use_search_for_query = self._should_use_search(user_question, context)
            
            # Generate response using new API with optional search
            config = {}
            if use_search_for_query:
                config = {
                    'tools': [{'google_search': {}}],
                }
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config if use_search_for_query else None
            )
            
            # Store in conversation history
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            
            self.conversations[user_id].append({
                "role": "user",
                "content": user_question,
                "timestamp": datetime.utcnow().isoformat(),
                "used_search": use_search_for_query
            })
            
            self.conversations[user_id].append({
                "role": "assistant",
                "content": response.text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep only last 20 messages
            if len(self.conversations[user_id]) > 20:
                self.conversations[user_id] = self.conversations[user_id][-20:]
            
            return {
                "success": True,
                "response": response.text,
                "context_aware": True,
                "current_challenge": context.get("challenge_id"),
                "conversation_length": len(self.conversations.get(user_id, [])),
                "used_google_search": use_search_for_query
            }
            
        except Exception as e:
            # Fallback to static hint on error
            return self._get_static_hint(user_id, user_question)
    
    def _get_static_hint(self, user_id: str, question: str) -> Dict[str, Any]:
        """
        Generate static hints without AI - platform always works
        
        Args:
            user_id: User identifier
            question: User's question
        
        Returns:
            Static contextual hint
        """
        context = self.user_contexts.get(user_id, {})
        vuln_type = context.get("vulnerability_type", "unknown")
        
        # Static hints based on vulnerability type
        static_hints = {
            "sqli": "💡 Try using SQL injection techniques. Look for input fields that interact with databases. Common payloads: ' OR '1'='1' --, UNION SELECT, etc.",
            "xss": "💡 Look for places where user input is reflected in the page. Try injecting <script>alert(1)</script> or other XSS payloads.",
            "command_injection": "💡 Check if user input is passed to system commands. Try command chaining with ; | & or other shell operators.",
            "path_traversal": "💡 Try navigating directories using ../ sequences. Look for file path parameters.",
            "lfi": "💡 Local File Inclusion - try reading sensitive files using paths like /etc/passwd or ../../../../etc/passwd",
            "rfi": "💡 Remote File Inclusion - try including external files. Test with URLs.",
            "csrf": "💡 CSRF attacks require forging requests. Check for missing CSRF tokens or improper validation.",
            "idor": "💡 Insecure Direct Object Reference - try changing IDs in URLs or parameters to access other users' data.",
            "xxe": "💡 XML External Entity - inject external entity references in XML input.",
            "deserialization": "💡 Look for serialized objects. Try modifying serialized data to inject malicious code."
        }
        
        hint = static_hints.get(vuln_type, "💡 Analyze the challenge carefully. Look for user input points and how data flows through the application.")
        
        return {
            "success": True,
            "response": f"{hint}\n\n🎯 Challenge: {context.get('challenge_id', 'Unknown')}\n⚡ Attempts: {context.get('attempt_count', 0)}",
            "context_aware": True,
            "current_challenge": context.get("challenge_id"),
            "static_hint": True,
            "genai_unavailable": not self.is_available()
        }
    
    def _build_contextual_prompt(
        self,
        user_id: str,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Build a context-aware prompt
        
        Args:
            user_id: User identifier
            question: User's question
            context: User context
        
        Returns:
            Complete prompt with context
        """
        # Base system prompt
        system_prompt = """You are an expert CTF (Capture The Flag) mentor and cybersecurity instructor. 
You help users learn about security vulnerabilities through hands-on challenges.

Your teaching style:
- Be encouraging and supportive 😊
- Provide hints, not complete solutions
- Explain concepts clearly with examples
- Use emojis to make learning fun 🎯
- Relate vulnerabilities to real-world scenarios
- Suggest tools and techniques
- Build on what the user already knows

Remember: The goal is to help them LEARN, not just get the flag!
"""
        
        # Add context information
        context_info = "\n\n📊 CURRENT USER CONTEXT:\n"
        
        if context.get("challenge_id"):
            context_info += f"- Current Challenge: {context['challenge_id']}\n"
        
        if context.get("vulnerability_type"):
            context_info += f"- Vulnerability Type: {context['vulnerability_type']}\n"
        
        if context.get("attempt_count", 0) > 0:
            context_info += f"- Attempts so far: {context['attempt_count']}\n"
        
        if context.get("last_error"):
            context_info += f"- Last error: {context['last_error']}\n"
        
        if context.get("solved_challenges"):
            solved_count = len(context['solved_challenges'])
            context_info += f"- Previously solved: {solved_count} challenges\n"
        
        # Add conversation history
        history_prompt = ""
        if user_id in self.conversations and self.conversations[user_id]:
            history_prompt = "\n\n💬 RECENT CONVERSATION:\n"
            recent = self.conversations[user_id][-6:]  # Last 3 exchanges
            for msg in recent:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_prompt += f"{role}: {msg['content'][:200]}...\n"
        
        # Combine all parts
        full_prompt = f"""{system_prompt}
{context_info}
{history_prompt}

👤 USER QUESTION:
{question}

💡 YOUR HELPFUL RESPONSE (with emojis and encouragement):
"""
        
        return full_prompt
    
    def analyze_code_vulnerability(
        self,
        code_snippet: str,
        vulnerability_type: Optional[str] = None,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Analyze code for vulnerabilities - OPTIONAL GenAI feature
        Returns basic analysis if GenAI unavailable
        
        Args:
            code_snippet: Code to analyze
            vulnerability_type: Expected vulnerability type
            language: Programming language
        
        Returns:
            Detailed vulnerability analysis or basic check
        """
        # If GenAI not available, return basic static analysis
        if not self.is_available():
            return {
                "success": True,
                "analysis": f"📝 Code analysis requested for {language} code.\n\n"
                           f"{'Focus area: ' + vulnerability_type if vulnerability_type else 'General security review'}\n\n"
                           f"⚠️ AI analysis unavailable. Please manually review:\n"
                           f"- Input validation\n- Output encoding\n- Authentication/authorization\n- Error handling\n- Secure defaults",
                "code_language": language,
                "vulnerability_focus": vulnerability_type,
                "static_analysis": True
            }
        
        prompt = f"""You are a security code reviewer. Analyze this {language} code for vulnerabilities.

CODE TO ANALYZE:
```{language}
{code_snippet}
```

"""
        if vulnerability_type:
            prompt += f"\nFocus on: {vulnerability_type} vulnerabilities\n"
        
        prompt += """
Provide a detailed analysis including:
1. 🔍 Identified vulnerabilities
2. ⚠️ Severity level (Critical/High/Medium/Low)
3. 💥 How it can be exploited (example attack)
4. ✅ How to fix it (secure code example)
5. 🛡️ Best practices to prevent this
6. 🔗 Latest security advisories and patches (use Google Search)

Format your response with clear sections and emojis!
"""
        
        try:
            # Use Google Search for latest vulnerability info
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={'tools': [{'google_search': {}}]}
            )
            
            return {
                "success": True,
                "analysis": response.text,
                "code_language": language,
                "vulnerability_focus": vulnerability_type
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_challenge_explanation(
        self,
        challenge_id: str,
        vulnerability_type: str,
        user_skill_level: str = "beginner"
    ) -> Dict[str, Any]:
        """
        Generate detailed challenge explanation
        
        Args:
            challenge_id: Challenge identifier
            vulnerability_type: Vulnerability type
            user_skill_level: User's skill level
        
        Returns:
            Detailed explanation
        """
        prompt = f"""Create a detailed, educational explanation for a CTF challenge.

Challenge Type: {vulnerability_type}
User Level: {user_skill_level}

Provide:
1. 🎯 What is {vulnerability_type}?
2. 🌍 Real-world examples where this vulnerability caused problems (use Google Search for recent cases)
3. 🔨 Tools commonly used to exploit/test this (search for latest versions and tools)
4. 📚 Learning resources (articles, videos, practice sites - find current ones)
5. 💡 Tips for this specific challenge
6. 🎓 Key concepts to understand
7. 🔗 Latest CVEs and security advisories related to this vulnerability

Make it engaging and educational! Use emojis and be encouraging!
Use Google Search to provide up-to-date information!
"""
        
        try:
            # Use Google Search for latest vulnerability info and resources
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={'tools': [{'google_search': {}}]}
            )
            
            return {
                "success": True,
                "explanation": response.text,
                "challenge_id": challenge_id,
                "skill_level": user_skill_level
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_personalized_learning_path(
        self,
        user_id: str,
        solved_challenges: List[str],
        current_skill_level: str
    ) -> Dict[str, Any]:
        """
        Generate personalized learning path based on user progress
        
        Args:
            user_id: User identifier
            solved_challenges: List of completed challenges
            current_skill_level: Current skill assessment
        
        Returns:
            Personalized learning recommendations
        """
        prompt = f"""You are a personalized CTF learning advisor.

User Progress:
- Skill Level: {current_skill_level}
- Completed Challenges: {len(solved_challenges)}
- Challenge Types Solved: {', '.join(set(solved_challenges)) if solved_challenges else 'None yet'}

Create a personalized learning path with:
1. 🎯 Next 3 recommended challenges (in order of difficulty)
2. 📚 Skills to focus on developing
3. 🛠️ Tools to learn
4. 📖 Resources (courses, articles, practice platforms)
5. 🎓 Career path advice for cybersecurity
6. 💪 Motivational message

Make it specific, actionable, and encouraging!
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            return {
                "success": True,
                "learning_path": response.text,
                "skill_level": current_skill_level,
                "challenges_completed": len(solved_challenges)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def explain_error_message(
        self,
        error_message: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Explain what an error message means in simple terms
        
        Args:
            error_message: The error message
            context: Challenge context
        
        Returns:
            Simple explanation
        """
        prompt = f"""Explain this error message in simple, beginner-friendly terms:

ERROR: {error_message}

Context: Working on a {context.get('vulnerability_type', 'security')} challenge

Provide:
1. What the error means
2. Why it happened
3. How to fix it
4. What to try next

Keep it simple and encouraging! Use emojis! 😊
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return "🤔 That's a tricky error! Try checking your syntax and approach."
    
    def _should_use_search(self, question: str, context: Dict[str, Any]) -> bool:
        """
        Determine if Google Search should be used for this query
        
        Args:
            question: User's question
            context: User context
        
        Returns:
            True if search should be used
        """
        # Keywords that indicate need for real-time search
        search_keywords = [
            'latest', 'recent', 'current', 'new', 'updated', 'tool', 'exploit',
            'cve', 'vulnerability', 'patch', 'version', '2024', '2025', '2026',
            'real-world', 'example', 'case study', 'news', 'advisory',
            'best practice', 'recommended', 'popular', 'trending'
        ]
        
        question_lower = question.lower()
        
        # Check if question contains search keywords
        for keyword in search_keywords:
            if keyword in question_lower:
                return True
        
        # Check if asking about specific tools or CVEs
        if 'tool' in question_lower or 'cve-' in question_lower:
            return True
        
        # Check if asking for current information about vulnerabilities
        vuln_type = context.get('vulnerability_type', '')
        if vuln_type and any(word in question_lower for word in ['how', 'what', 'which', 'when']):
            return True
        
        return False
    
    def _generate_fallback_hint(self, context: Dict[str, Any]) -> str:
        """Generate fallback hint when API fails"""
        vuln_type = context.get("vulnerability_type", "general")
        
        fallback_hints = {
            "sql_injection": "💡 Try using special characters like quotes (') and comments (--) in your input!",
            "xss": "💡 Think about how you can inject JavaScript into the page. Try <script> tags!",
            "command_injection": "💡 Look for ways to chain commands using ; | & or backticks!",
            "path_traversal": "💡 Can you navigate up directories using ../ to access restricted files?",
            "general": "💡 Think about what the application expects vs. what you can provide. Look for input validation weaknesses!"
        }
        
        return fallback_hints.get(vuln_type, fallback_hints["general"])
    
    def clear_conversation(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversations:
            del self.conversations[user_id]
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]


# Global instance
genai_service = ContextAwareGenAI()


def get_genai_service() -> ContextAwareGenAI:
    """Dependency to get GenAI service"""
    return genai_service
