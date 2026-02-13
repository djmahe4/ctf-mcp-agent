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
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


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
                print("✅ Admin AI Agent available for enhanced operations")
        except Exception as e:
            print(f"ℹ️ Admin AI Agent unavailable: {e}. Core admin functions still work.")
        
        # Enable Google Search by default for admin when available
        self.use_search = True
    
    def is_available(self) -> bool:
        """Check if admin AI agent is available"""
        return self.available and self.client is not None
    
    def analyze_steganography_image(
        self,
        image_path: str,
        analysis_type: str = "comprehensive"
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
            
            # Create multi-modal request
            response = self.client.models.generate_content(
                model=self.vision_model_name,
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type=f"image/{img_format.lower()}"),
                    prompt
                ]
            )
            
            return {
                "success": True,
                "analysis": response.text,
                "image_path": image_path,
                "image_format": img_format,
                "image_size": img_size,
                "analysis_type": analysis_type
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


# Global instance
admin_agent = MultiModalAdminAgent()


def get_admin_agent() -> MultiModalAdminAgent:
    """Dependency to get admin agent"""
    return admin_agent
