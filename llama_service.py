"""
Llama.cpp Integration Service
Handles LLM model loading and inference for MCP agent
"""

from typing import Optional, Dict, Any, List
import os
from dataclasses import dataclass


@dataclass
class LlamaConfig:
    """Configuration for Llama.cpp model"""
    model_path: str
    n_ctx: int = 2048
    n_threads: int = 4
    n_gpu_layers: int = 0
    temperature: float = 0.7
    max_tokens: int = 500


class LlamaCppService:
    """
    Service for interacting with Llama.cpp models
    Provides MCP agent capabilities powered by local LLM
    """
    
    def __init__(self, config: Optional[LlamaConfig] = None):
        """
        Initialize Llama.cpp service
        
        Args:
            config: Model configuration
        """
        self.config = config or LlamaConfig(
            model_path=os.getenv("LLAMA_MODEL_PATH", "models/llama-2-7b-chat.gguf"),
            n_ctx=int(os.getenv("LLAMA_CTX_SIZE", "2048")),
            n_threads=int(os.getenv("LLAMA_THREADS", "4")),
            n_gpu_layers=int(os.getenv("LLAMA_GPU_LAYERS", "0"))
        )
        self.llm = None
        self.is_initialized = False
    
    def initialize(self):
        """
        Initialize the Llama.cpp model
        
        Note: Requires llama-cpp-python to be installed
        """
        try:
            from llama_cpp import Llama
            
            self.llm = Llama(
                model_path=self.config.model_path,
                n_ctx=self.config.n_ctx,
                n_threads=self.config.n_threads,
                n_gpu_layers=self.config.n_gpu_layers,
            )
            self.is_initialized = True
            print(f"✅ Llama.cpp model loaded from {self.config.model_path}")
            
        except ImportError:
            print("⚠️ llama-cpp-python not installed. Using mock responses.")
            self.is_initialized = False
        except Exception as e:
            print(f"⚠️ Failed to load Llama model: {e}")
            self.is_initialized = False
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        Generate a response using the LLM
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop: Stop sequences
        
        Returns:
            Generated text response
        """
        if not self.is_initialized or self.llm is None:
            return self._generate_mock_response(prompt)
        
        try:
            response = self.llm(
                prompt,
                max_tokens=max_tokens or self.config.max_tokens,
                temperature=temperature or self.config.temperature,
                stop=stop or ["</s>", "Human:", "User:"],
                echo=False
            )
            
            return response['choices'][0]['text'].strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._generate_mock_response(prompt)
    
    def generate_ctf_hint(
        self,
        challenge_type: str,
        challenge_description: str,
        user_attempts: Optional[List[str]] = None
    ) -> str:
        """
        Generate a CTF challenge hint using LLM
        
        Args:
            challenge_type: Type of vulnerability
            challenge_description: Challenge description
            user_attempts: Previous user attempts
        
        Returns:
            AI-generated hint
        """
        prompt = self._build_hint_prompt(challenge_type, challenge_description, user_attempts)
        return self.generate_response(prompt, max_tokens=200)
    
    def analyze_vulnerability(
        self,
        code_snippet: str,
        vulnerability_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze code for vulnerabilities using LLM
        
        Args:
            code_snippet: Code to analyze
            vulnerability_type: Expected vulnerability type
        
        Returns:
            Analysis results
        """
        prompt = self._build_analysis_prompt(code_snippet, vulnerability_type)
        analysis = self.generate_response(prompt, max_tokens=300)
        
        return {
            "analysis": analysis,
            "vulnerable": "vulnerable" in analysis.lower(),
            "recommendations": self._extract_recommendations(analysis)
        }
    
    def chat_with_agent(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        agent_role: str = "helper"
    ) -> str:
        """
        Chat with the MCP agent
        
        Args:
            message: User message
            conversation_history: Previous conversation
            agent_role: Role of the agent
        
        Returns:
            Agent response
        """
        prompt = self._build_chat_prompt(message, conversation_history, agent_role)
        return self.generate_response(prompt, max_tokens=400)
    
    def _build_hint_prompt(
        self,
        challenge_type: str,
        challenge_description: str,
        user_attempts: Optional[List[str]]
    ) -> str:
        """Build prompt for hint generation"""
        prompt = f"""You are a helpful CTF assistant. A user is stuck on a {challenge_type} challenge.

Challenge Description: {challenge_description}

"""
        if user_attempts:
            prompt += f"User has tried: {', '.join(user_attempts)}\n\n"
        
        prompt += """Provide a helpful hint without giving away the complete solution. Be encouraging and guide them in the right direction.

Hint:"""
        return prompt
    
    def _build_analysis_prompt(self, code: str, vuln_type: Optional[str]) -> str:
        """Build prompt for vulnerability analysis"""
        prompt = f"""You are a security expert analyzing code for vulnerabilities.

Code to analyze:
```
{code}
```

"""
        if vuln_type:
            prompt += f"Focus on {vuln_type} vulnerabilities.\n\n"
        
        prompt += """Analyze this code and explain:
1. What vulnerabilities exist
2. How they can be exploited
3. How to fix them

Analysis:"""
        return prompt
    
    def _build_chat_prompt(
        self,
        message: str,
        history: List[Dict[str, str]],
        role: str
    ) -> str:
        """Build prompt for chat interaction"""
        system_prompts = {
            "helper": "You are a helpful and encouraging CTF assistant. You provide hints and guidance without giving away complete solutions. Use emojis to make responses fun!",
            "analyzer": "You are a security vulnerability analyzer. You help identify and explain security issues in code.",
            "reviewer": "You are a code reviewer focusing on security best practices.",
            "mentor": "You are a cybersecurity mentor helping users learn about vulnerabilities and exploitation techniques."
        }
        
        prompt = f"{system_prompts.get(role, system_prompts['helper'])}\n\n"
        
        # Add conversation history
        for entry in history[-5:]:  # Last 5 messages
            prompt += f"{entry['role']}: {entry['content']}\n"
        
        prompt += f"User: {message}\nAssistant:"
        
        return prompt
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract security recommendations from analysis"""
        recommendations = []
        
        keywords = [
            "use parameterized queries",
            "sanitize input",
            "validate",
            "escape",
            "encode output",
            "use prepared statements",
            "whitelist"
        ]
        
        for keyword in keywords:
            if keyword in analysis.lower():
                recommendations.append(keyword.title())
        
        return recommendations or ["Review security best practices"]
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate mock response when LLM is not available"""
        import random
        
        responses = [
            "🤖 That's an interesting question! Try examining the input validation more carefully.",
            "💡 Here's a hint: Think about how special characters are handled in the code.",
            "🔍 Have you considered SQL injection? The query looks vulnerable.",
            "🎯 You're on the right track! Look at the authentication mechanism.",
            "🛡️ Security tip: Always sanitize user input before using it in queries!",
            "🧠 Think about what happens when you inject unexpected characters...",
            "⚡ Pro tip: Use a proxy like Burp Suite to inspect the traffic!",
            "🔐 Consider how the application handles sessions and cookies.",
        ]
        
        return random.choice(responses)


# Global service instance
llama_service = LlamaCppService()


def get_llama_service() -> LlamaCppService:
    """Dependency to get Llama service"""
    return llama_service


def initialize_llama_on_startup():
    """Initialize Llama model on server startup"""
    global llama_service
    llama_service.initialize()
