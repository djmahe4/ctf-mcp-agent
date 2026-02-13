"""
Google GenAI Context-Aware Service
Provides intelligent, context-aware assistance using Google's Gemini
"""

from typing import List, Dict, Optional, Any
import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class ContextAwareGenAI:
    """
    Context-aware AI assistant powered by Google Gemini
    Provides intelligent help based on user's current challenge context
    """
    
    def __init__(self):
        """Initialize Google GenAI service"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Conversation history per user
        self.conversations: Dict[str, List[Dict]] = {}
        
        # Context tracking
        self.user_contexts: Dict[str, Dict[str, Any]] = {}
    
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
        
        Args:
            user_id: User identifier
            user_question: User's question
            include_history: Include conversation history
        
        Returns:
            AI-generated contextual response
        """
        # Get user context
        context = self.user_contexts.get(user_id, {})
        
        # Build context-aware prompt
        prompt = self._build_contextual_prompt(user_id, user_question, context)
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Store in conversation history
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            
            self.conversations[user_id].append({
                "role": "user",
                "content": user_question,
                "timestamp": datetime.utcnow().isoformat()
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
                "conversation_length": len(self.conversations.get(user_id, []))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_response": self._generate_fallback_hint(context)
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
        Analyze code for vulnerabilities using GenAI
        
        Args:
            code_snippet: Code to analyze
            vulnerability_type: Expected vulnerability type
            language: Programming language
        
        Returns:
            Detailed vulnerability analysis
        """
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

Format your response with clear sections and emojis!
"""
        
        try:
            response = self.model.generate_content(prompt)
            
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
2. 🌍 Real-world examples where this vulnerability caused problems
3. 🔨 Tools commonly used to exploit/test this
4. 📚 Learning resources (articles, videos, practice sites)
5. 💡 Tips for this specific challenge
6. 🎓 Key concepts to understand

Make it engaging and educational! Use emojis and be encouraging!
"""
        
        try:
            response = self.model.generate_content(prompt)
            
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
            response = self.model.generate_content(prompt)
            
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
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "🤔 That's a tricky error! Try checking your syntax and approach."
    
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
