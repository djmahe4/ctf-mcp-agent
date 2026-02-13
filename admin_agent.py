"""
Multi-Modal Admin AI Agent - OPTIONAL FEATURE
Enhanced admin orchestration agent with image analysis and creative operations
Supports steganography analysis, custom operations, and flexible prompts
Integrated with Google Search for real-time vulnerability research
FALLBACK: Core admin functions work without AI
"""

from typing import List, Dict, Optional, Any
from google import genai
from google.genai import types
import os
import subprocess
import shutil
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


class ToolExecutionLayer:
    """
    Secure layer for executing external security tools
    Only allows specific tools and validates paths
    """
    
    ALLOWED_TOOLS = {
        "exiftool": ["exiftool", "-ver"],
        "strings": ["strings", "--version"],
        "binwalk": ["binwalk", "--version"],
        "zsteg": ["zsteg", "--version"]
    }
    
    def __init__(self, sandbox_dir: str = "sandbox/forensics"):
        self.sandbox_dir = os.path.abspath(sandbox_dir)
        os.makedirs(self.sandbox_dir, exist_ok=True)
        self.available_tools = {}
        self._check_tool_availability()
    
    def _check_tool_availability(self):
        """Check which tools are actually installed on the system"""
        for tool_name, check_cmd in self.ALLOWED_TOOLS.items():
            tool_path = shutil.which(tool_name)
            if tool_path:
                try:
                    # Run the version check command
                    result = subprocess.run(
                        check_cmd, 
                        capture_output=True, 
                        text=True, 
                        timeout=2
                    )
                    if result.returncode == 0:
                        self.available_tools[tool_name] = tool_path
                except Exception:
                    pass
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.available_tools.keys())
    
    def execute_tool(
        self, 
        tool_name: str, 
        args: List[str], 
        file_path: str
    ) -> Dict[str, Any]:
        """
        Execute an allowed tool against a file safely
        
        Args:
            tool_name: Name of the tool (exiftool, strings, etc.)
            args: List of arguments for the tool
            file_path: Path to the file to analyze
            
        Returns:
            Execution results
        """
        if tool_name not in self.available_tools:
            return {
                "success": False, 
                "error": f"Tool '{tool_name}' is not available on this system."
            }
        
        # Security: Validate file path is within allowed areas or exists
        abs_file_path = os.path.abspath(file_path)
        if not os.path.exists(abs_file_path):
            return {"success": False, "error": f"File not found: {file_path}"}
            
        # Security: Filter/validate arguments (very basic for this demo)
        forbidden_chars = [';', '&', '|', '>', '<', '`', '$']
        for arg in args:
            if any(char in arg for char in forbidden_chars):
                return {"success": False, "error": "Invalid characters in arguments."}
        
        try:
            full_cmd = [self.available_tools[tool_name]] + args + [abs_file_path]
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(full_cmd)
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Tool execution timed out."}
        except Exception as e:
            return {"success": False, "error": str(e)}



class MultiModalAdminAgent:
    """
    Multi-modal AI agent for admin operations - OPTIONAL
    Supports text, images, Google Search, and custom creative operations
    Admin functions work without this - it's an enhancement only
    """
    
    def __init__(self):
        """Initialize multi-modal admin agent - may fail gracefully"""
        self.available = False
        self.client = None
        self.model_name = 'gemini-2.0-flash-exp'
        self.vision_model_name = 'gemini-2.0-flash-exp'
        
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
                self.available = True
                print("SUCCESS: Admin AI Agent available for enhanced operations")
        except Exception as e:
            print(f"[INFO] Admin AI Agent unavailable: {e}. Core admin functions still work.")
        
        # Enable Google Search by default for admin when available
        self.use_search = True
        
        # Initialize tool execution layer
        self.tool_layer = ToolExecutionLayer()
    
    def is_available(self) -> bool:
        """Check if admin AI agent is available"""
        return self.available and self.client is not None
    
    def analyze_steganography_image(
        self,
        image_path: str,
        analysis_type: str = "comprehensive",
        use_real_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze an image for steganography - AI optional
        Returns basic analysis without AI
        
        Args:
            image_path: Path to the image file
            analysis_type: Type of analysis (comprehensive, lsb, metadata, visual)
        
        Returns:
            Analysis results with AI insights or basic metadata
        """
        try:
            # Load and prepare image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Get image info
            img = Image.open(image_path)
            img_format = img.format
            img_size = img.size
            img_mode = img.mode
            
            # Basic analysis always available
            basic_analysis = f"""📷 Image Analysis for {image_path}

Format: {img_format}
Size: {img_size}
Mode: {img_mode}
File size: {len(image_data)} bytes

🔍 Recommended Manual Analysis:
1. Check EXIF data: `exiftool {image_path}`
2. LSB analysis: `zsteg {image_path}` or `stegsolve`
3. Strings: `strings {image_path}`
4. Binwalk: `binwalk -e {image_path}`
5. Steghide: `steghide extract -sf {image_path}`
"""

            # If AI unavailable, return basic analysis
            if not self.is_available():
                return {
                    "success": True,
                    "analysis": basic_analysis,
                    "image_path": image_path,
                    "image_format": img_format,
                    "image_size": img_size,
                    "analysis_type": analysis_type,
                    "ai_enhanced": False
                }
            
            # Enhanced AI analysis
            prompt = f"""You are an expert in steganography and image forensics. 
            
Analyze this image for potential hidden data. Image details:
- Format: {img_format}
- Size: {img_size}
- Mode: {img_mode}
- Analysis Type: {analysis_type}

Provide a detailed analysis including:
1. 🔍 Visual anomalies or patterns that might indicate hidden data
2. 📊 Statistical analysis suggestions (LSB, histogram irregularities)
3. 🛠️ Recommended tools and techniques for extraction
4. 💡 Creative approaches to reveal hidden content
5. 🎯 Likelihood assessment of containing hidden data (1-10)
6. 📝 Specific extraction commands or methods to try

Be creative and think outside the box! Consider:
- LSB steganography in RGB channels
- Metadata and EXIF data
- File format peculiarities
- Palette-based hiding
- Visual watermarks
- Frequency domain hiding

Format your response with clear sections and actionable insights!
"""
            
            # Optional: Run real forensics tools as "Subagent Tasks"
            real_tool_results = {}
            if use_real_tools:
                available = self.tool_layer.get_available_tools()
                if "exiftool" in available:
                    real_tool_results["exiftool"] = self.tool_layer.execute_tool(
                        "exiftool", ["-all"], image_path
                    )
                if "strings" in available:
                    real_tool_results["strings"] = self.tool_layer.execute_tool(
                        "strings", ["-n", "10"], image_path
                    )
            
            # Create multi-modal request with real-world tool output as context
            tool_context = ""
            if real_tool_results:
                tool_context = "\n🔍 REAL-WORLD TOOL DATA (Subagent Results):\n"
                for tool, res in real_tool_results.items():
                    if res["success"]:
                        tool_context += f"\n--- {tool} output (truncated) ---\n"
                        tool_context += res["stdout"][:1000] + "\n"
            
            response = self.client.models.generate_content(
                model=self.vision_model_name,
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type=f"image/{img_format.lower()}"),
                    prompt + tool_context
                ]
            )
            
            return {
                "success": True,
                "analysis": response.text,
                "image_path": image_path,
                "image_format": img_format,
                "image_size": img_size,
                "analysis_type": analysis_type,
                "real_tool_outputs": real_tool_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }
    
    def create_challenge_from_image(
        self,
        image_path: str,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate a CTF challenge based on an image
        
        Args:
            image_path: Path to image
            difficulty: Challenge difficulty
        
        Returns:
            Complete challenge specification
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            img = Image.open(image_path)
            
            prompt = f"""You are a creative CTF challenge designer.

Create a unique {difficulty} difficulty challenge based on this image.

Be creative! Consider:
- Image steganography (LSB, metadata, visual encoding)
- QR codes or barcodes hidden in the image
- Cryptographic puzzles visible in the image
- Visual ciphers or patterns
- File format exploits
- Multi-layer encoding

Generate a complete challenge with:
1. 🎯 Challenge Title (creative and engaging!)
2. 📝 Challenge Description (tell a story!)
3. 🔐 Hidden Flag Location (where/how flag is hidden)
4. 💡 3 Progressive Hints (from vague to specific)
5. 🛠️ Required Tools and Skills
6. 🎓 Educational Value (what will they learn?)
7. ⚡ Difficulty Rating (1-10)
8. 🎨 Creative Twist (what makes this unique?)

Make it interesting and educational!
"""
            
            response = self.client.models.generate_content(
                model=self.vision_model_name,
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type=f"image/{img.format.lower()}"),
                    prompt
                ]
            )
            
            return {
                "success": True,
                "challenge": response.text,
                "image_path": image_path,
                "difficulty": difficulty
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def custom_creative_operation(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a custom creative operation based on admin prompt
        
        This is the flexible, creative function that allows admins to:
        - Analyze any combination of images
        - Generate custom challenge types
        - Perform creative security analysis
        - Design unique CTF scenarios
        
        Args:
            prompt: Custom prompt from admin
            images: Optional list of image paths
            context: Additional context data
        
        Returns:
            AI-generated response
        """
        try:
            contents = []
            
            # Add images if provided
            if images:
                for img_path in images:
                    with open(img_path, 'rb') as f:
                        image_data = f.read()
                    img = Image.open(img_path)
                    contents.append(
                        types.Part.from_bytes(
                            data=image_data, 
                            mime_type=f"image/{img.format.lower()}"
                        )
                    )
            
            # Build comprehensive prompt
            full_prompt = "You are a creative CTF platform administrator and security expert.\n\n"
            
            if context:
                full_prompt += "CONTEXT:\n"
                for key, value in context.items():
                    full_prompt += f"- {key}: {value}\n"
                full_prompt += "\n"
            
            full_prompt += f"ADMIN REQUEST:\n{prompt}\n\n"
            full_prompt += """
Provide a creative, detailed, and actionable response.
Use emojis, be specific, and think outside the box!
If analyzing security, provide exploitation steps.
If creating challenges, make them unique and educational.
Use Google Search to find latest vulnerabilities, tools, and techniques!
"""
            
            contents.append(full_prompt)
            
            # Use Google Search for admin operations
            response = self.client.models.generate_content(
                model=self.vision_model_name,
                contents=contents,
                config={'tools': [{'google_search': {}}]} if self.use_search else None
            )
            
            return {
                "success": True,
                "response": response.text,
                "images_analyzed": len(images) if images else 0,
                "context_provided": bool(context)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_analyze_images(
        self,
        image_paths: List[str],
        analysis_prompt: str
    ) -> Dict[str, Any]:
        """
        Batch analyze multiple images with a custom prompt
        
        Args:
            image_paths: List of image paths
            analysis_prompt: What to analyze/look for
        
        Returns:
            Batch analysis results
        """
        results = []
        
        for img_path in image_paths:
            result = self.custom_creative_operation(
                prompt=f"{analysis_prompt}\n\nAnalyze this image:",
                images=[img_path],
                context={"image_path": img_path}
            )
            results.append(result)
        
        return {
            "success": True,
            "total_images": len(image_paths),
            "results": results
        }
    
    def generate_creative_challenge_series(
        self,
        theme: str,
        count: int = 5,
        difficulty_progression: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a series of related creative challenges
        
        Args:
            theme: Challenge theme (e.g., "movie hackers", "cyberpunk", "medieval")
            count: Number of challenges
            difficulty_progression: Whether to increase difficulty
        
        Returns:
            Series of challenges
        """
        prompt = f"""Create a series of {count} interconnected CTF challenges with the theme: "{theme}"

Requirements:
- Each challenge should be unique and creative
- Include various vulnerability types (research latest trends with Google Search)
- Tell a cohesive story across challenges
- {'Progress from easy to hard' if difficulty_progression else 'Maintain consistent difficulty'}
- Include fun elements and easter eggs
- Make them educational and engaging
- Incorporate recent real-world vulnerabilities and techniques

For each challenge provide:
1. 🎯 Title
2. 📖 Story/Description
3. 🔐 Vulnerability Type (with latest CVEs if relevant)
4. 💎 Hidden Flag Format
5. 💡 Hint System
6. 🎨 Creative Twist
7. 🔗 Connection to Other Challenges
8. 🔍 Real-world relevance (use Google Search)

Be creative and make it memorable! Use Google Search for current vulnerability trends!
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={'tools': [{'google_search': {}}]}
            )
            
            return {
                "success": True,
                "theme": theme,
                "challenge_count": count,
                "series": response.text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def design_unique_vulnerability(
        self,
        base_vuln_type: str,
        innovation_level: str = "high"
    ) -> Dict[str, Any]:
        """
        Design a unique twist on a classic vulnerability
        
        Args:
            base_vuln_type: Base vulnerability (sqli, xss, etc.)
            innovation_level: How creative to be (low, medium, high, extreme)
        
        Returns:
            Unique vulnerability design
        """
        innovation_prompts = {
            "low": "Add a small twist to make it interesting",
            "medium": "Combine it with another concept creatively",
            "high": "Make it completely unique with multiple layers",
            "extreme": "Create something never seen before in CTFs!"
        }
        
        prompt = f"""Design a unique {base_vuln_type} challenge.

Innovation Level: {innovation_level}
Goal: {innovation_prompts.get(innovation_level, innovation_prompts['high'])}

Create:
1. 🎯 Unique Challenge Concept
2. 🔧 Technical Implementation Details
3. 💡 What Makes It Special
4. 🎓 Learning Objectives
5. 🛠️ Setup Instructions for Admins
6. 📊 Expected Solve Rate
7. 🎨 Creative Elements
8. ⚠️ Security Considerations

Think creatively! Combine concepts, add storytelling, use unexpected techniques!
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            return {
                "success": True,
                "base_type": base_vuln_type,
                "innovation_level": innovation_level,
                "design": response.text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


    async def brainstorm_challenge(
        self,
        vulnerability_type: str = "sql_injection",
        difficulty: str = "medium",
        theme: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Brainstorm a complete new challenge using GenAI
        """
        if not self.is_available():
            return {"success": False, "error": "AI Agent unavailable"}
            
        vulnerability_categories = {
            "sql_injection": "Web Security",
            "xss": "Web Security",
            "command_injection": "System Exploitation",
            "path_traversal": "Forensics",
            "steganography": "Steganography",
            "crypto": "Cryptography"
        }
        category = vulnerability_categories.get(vulnerability_type, "General")

        prompt = f"""You are a master CTF challenge designer.
        Brainstorm a unique {difficulty} challenge that internally targets {vulnerability_type}.
        Broad Category: {category}
        {'Theme: ' + theme if theme else ''}
        
        CRITICAL INSTRUCTIONS:
        1. Keep the technical vulnerability name (e.g. '{vulnerability_type}') HIDDEN from the title and description.
        2. Create an IMMERSIVE STORY-DRIVEN description. For example, instead of 'SQL Injection', talk about a corrupt corporate database or a hacker's encrypted diary.
        3. The title must be creative and thematic (e.g. 'The Vault of Secrets', 'Ghost in the Machine').
        4. Provide a relatable real-world scenario.
        
        Provide the result in valid JSON format with:
        - title: Creative story-driven title
        - description: Immersive, relatable story-driven description (at least 2 paragraphs)
        - category: {category}
        - vulnerability_type: {vulnerability_type}
        - difficulty: {difficulty}
        - points: Recommended points (100-500)
        - hints: List of 3 progressive hints (start vague, end technical)
        - flag: A unique flag string starting with FLAG{{
        - fake_flags: List of 2-3 realistic-looking distractor flags (honeytokens)
        - recommended_meme: Theme-relevant meme/gif description or search query
        - vulnerable_endpoint: The relevant endpoint from the lab
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            
            import json
            challenge_data = json.loads(response.text)
            
            # Add unique ID
            challenge_data["id"] = f"dyn_{vulnerability_type}_{str(int(datetime.utcnow().timestamp()))}"
            
            return {
                "success": True,
                "challenge": challenge_data
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def deploy_dynamic_challenge(
        self,
        challenge_data: Dict[str, Any],
        db = None
    ) -> Dict[str, Any]:
        """
        Deploy a brainstormed challenge to the database
        """
        if not db:
            from main import database as db
            
        if not db:
            return {"success": False, "error": "Database not available"}
            
        try:
            await db.challenges.insert_one(challenge_data)
            return {
                "success": True,
                "message": f"🚀 Challenge '{challenge_data['title']}' deployed successfully!",
                "challenge_id": challenge_data["id"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
admin_agent = MultiModalAdminAgent()


def get_admin_agent() -> MultiModalAdminAgent:
    """Dependency to get admin agent"""
    return admin_agent
