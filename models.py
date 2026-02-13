"""
Comprehensive Pydantic Models for CTF Lab
This module contains all Pydantic models for the CTF simulation platform
"""

from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


# ===== User Authentication Models =====

class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, description="Full name of the user")
    role: UserRole = Field(default=UserRole.USER, description="User role")


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8, description="User password")
    
    @validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserLogin(BaseModel):
    """User login model"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class User(UserBase):
    """User model with database fields"""
    id: str = Field(..., description="User ID")
    hashed_password: str = Field(..., description="Hashed password")
    is_active: bool = Field(default=True, description="Is user active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    score: int = Field(default=0, description="Total CTF score")
    solved_challenges: List[str] = Field(default_factory=list, description="List of solved challenge IDs")
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT token model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    user_id: Optional[str] = None


# ===== Vulnerability Challenge Models =====

class VulnerabilityType(str, Enum):
    """Types of vulnerabilities"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    CSRF = "csrf"
    IDOR = "idor"
    XXE = "xxe"
    SSRF = "ssrf"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    BROKEN_AUTH = "broken_authentication"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    USING_COMPONENTS_VULNERABILITIES = "using_components_vulnerabilities"


class DifficultyLevel(str, Enum):
    """Challenge difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ChallengeBase(BaseModel):
    """Base challenge model"""
    title: str = Field(..., min_length=3, max_length=200, description="Challenge title")
    description: str = Field(..., description="Challenge description")
    vulnerability_type: VulnerabilityType = Field(..., description="Type of vulnerability")
    difficulty: DifficultyLevel = Field(..., description="Challenge difficulty")
    points: int = Field(..., ge=10, le=1000, description="Points awarded for solving")
    hints: List[str] = Field(default_factory=list, description="List of hints")
    tags: List[str] = Field(default_factory=list, description="Challenge tags")


class ChallengeCreate(ChallengeBase):
    """Challenge creation model"""
    flag: str = Field(..., description="Challenge flag/answer")
    vulnerable_code: Optional[str] = Field(None, description="Vulnerable code snippet")
    solution_explanation: Optional[str] = Field(None, description="Explanation of the solution")


class Challenge(ChallengeBase):
    """Challenge model with database fields"""
    id: str = Field(..., description="Challenge ID")
    flag_hash: str = Field(..., description="Hashed flag")
    vulnerable_endpoint: Optional[str] = Field(None, description="Vulnerable API endpoint")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="Creator user ID")
    solve_count: int = Field(default=0, description="Number of solves")
    
    model_config = ConfigDict(from_attributes=True)


class ChallengeSubmission(BaseModel):
    """Challenge submission model"""
    challenge_id: str = Field(..., description="Challenge ID")
    flag: str = Field(..., description="Submitted flag")


class SubmissionResult(BaseModel):
    """Submission result model"""
    success: bool = Field(..., description="Whether submission was correct")
    message: str = Field(..., description="Result message")
    points_awarded: Optional[int] = Field(None, description="Points awarded if correct")


# ===== SQL Injection Models =====

class SQLInjectionPayload(BaseModel):
    """SQL Injection payload model"""
    query: str = Field(..., description="SQL query with potential injection")
    expected_result: Optional[str] = Field(None, description="Expected result")
    is_vulnerable: bool = Field(..., description="Whether query is vulnerable")


class SQLInjectionChallenge(BaseModel):
    """SQL Injection specific challenge"""
    database_schema: Dict[str, List[str]] = Field(..., description="Database schema for the challenge")
    target_table: str = Field(..., description="Target table name")
    objective: str = Field(..., description="Challenge objective")
    sample_queries: List[str] = Field(default_factory=list, description="Sample safe queries")


# ===== XSS Models =====

class XSSType(str, Enum):
    """Types of XSS attacks"""
    REFLECTED = "reflected"
    STORED = "stored"
    DOM_BASED = "dom_based"


class XSSPayload(BaseModel):
    """XSS payload model"""
    payload: str = Field(..., description="XSS payload")
    xss_type: XSSType = Field(..., description="Type of XSS")
    context: str = Field(..., description="Where payload is injected")


class XSSChallenge(BaseModel):
    """XSS specific challenge"""
    xss_type: XSSType = Field(..., description="Type of XSS vulnerability")
    input_field: str = Field(..., description="Vulnerable input field")
    sanitization_attempt: Optional[str] = Field(None, description="Attempted sanitization method")


# ===== Command Injection Models =====

class CommandInjectionPayload(BaseModel):
    """Command injection payload model"""
    command: str = Field(..., description="Command with potential injection")
    os_type: Literal["linux", "windows", "mac"] = Field(..., description="Target OS type")
    expected_output: Optional[str] = Field(None, description="Expected command output")


class CommandInjectionChallenge(BaseModel):
    """Command injection specific challenge"""
    vulnerable_function: str = Field(..., description="Vulnerable function name")
    command_template: str = Field(..., description="Command template being used")
    allowed_commands: List[str] = Field(default_factory=list, description="Supposedly allowed commands")


# ===== Path Traversal Models =====

class PathTraversalPayload(BaseModel):
    """Path traversal payload model"""
    path: str = Field(..., description="Path with potential traversal")
    target_file: str = Field(..., description="Target file to access")
    expected_content: Optional[str] = Field(None, description="Expected file content")


class PathTraversalChallenge(BaseModel):
    """Path traversal specific challenge"""
    base_directory: str = Field(..., description="Base directory for file access")
    restricted_files: List[str] = Field(default_factory=list, description="Files that should be restricted")
    file_extension_filter: Optional[str] = Field(None, description="File extension filter")


# ===== Eisenhower Decision Matrix Models =====

class TaskPriority(str, Enum):
    """Task priority based on Eisenhower Matrix"""
    DO_FIRST = "do_first"  # Urgent and Important
    SCHEDULE = "schedule"  # Important but Not Urgent
    DELEGATE = "delegate"  # Urgent but Not Important
    ELIMINATE = "eliminate"  # Neither Urgent nor Important


class EisenhowerTask(BaseModel):
    """Task model using Eisenhower Decision Matrix"""
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    is_urgent: bool = Field(..., description="Is task urgent")
    is_important: bool = Field(..., description="Is task important")
    priority: TaskPriority = Field(..., description="Task priority")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    assigned_to: Optional[str] = Field(None, description="User assigned to task")
    related_challenge: Optional[str] = Field(None, description="Related challenge ID")
    
    @validator('priority', always=True)
    def calculate_priority(cls, v, values):
        """Auto-calculate priority based on urgency and importance"""
        is_urgent = values.get('is_urgent', False)
        is_important = values.get('is_important', False)
        
        if is_urgent and is_important:
            return TaskPriority.DO_FIRST
        elif is_important and not is_urgent:
            return TaskPriority.SCHEDULE
        elif is_urgent and not is_important:
            return TaskPriority.DELEGATE
        else:
            return TaskPriority.ELIMINATE


class TaskUpdate(BaseModel):
    """Task update model"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_urgent: Optional[bool] = None
    is_important: Optional[bool] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None


# ===== MCP Agent Models (Llama.cpp) =====

class MCPAgentRole(str, Enum):
    """MCP Agent roles"""
    HINT_PROVIDER = "hint_provider"
    VULNERABILITY_ANALYZER = "vulnerability_analyzer"
    CODE_REVIEWER = "code_reviewer"
    CHALLENGE_CREATOR = "challenge_creator"


class MCPAgentRequest(BaseModel):
    """MCP Agent request model"""
    agent_role: MCPAgentRole = Field(..., description="Role of the MCP agent")
    prompt: str = Field(..., min_length=1, description="Prompt for the agent")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    max_tokens: int = Field(default=500, ge=1, le=2000, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")


class MCPAgentResponse(BaseModel):
    """MCP Agent response model"""
    role: MCPAgentRole = Field(..., description="Agent role")
    response: str = Field(..., description="Agent response")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class HintRequest(BaseModel):
    """Hint request model"""
    challenge_id: str = Field(..., description="Challenge ID")
    user_id: str = Field(..., description="User ID requesting hint")
    difficulty_preference: Optional[str] = Field(None, description="Preferred hint difficulty")


class HintResponse(BaseModel):
    """Hint response model"""
    hint: str = Field(..., description="Generated hint")
    cost: int = Field(..., description="Points cost for the hint")
    hint_level: int = Field(..., description="Hint difficulty level")


# ===== Google GenAI Integration Models =====

class GenAIAnalysisRequest(BaseModel):
    """Google GenAI analysis request"""
    vulnerability_type: VulnerabilityType = Field(..., description="Type of vulnerability to analyze")
    code_snippet: str = Field(..., description="Code snippet to analyze")
    context: Optional[str] = Field(None, description="Additional context")


class GenAIAnalysisResponse(BaseModel):
    """Google GenAI analysis response"""
    is_vulnerable: bool = Field(..., description="Whether code is vulnerable")
    vulnerability_details: List[str] = Field(default_factory=list, description="Vulnerability details")
    severity: str = Field(..., description="Vulnerability severity")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")
    patched_code: Optional[str] = Field(None, description="Suggested patched code")


class CodeGenerationRequest(BaseModel):
    """Code generation request"""
    vulnerability_type: VulnerabilityType = Field(..., description="Type of vulnerable code to generate")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    programming_language: str = Field(default="python", description="Programming language")
    include_fix: bool = Field(default=False, description="Include fixed version")


class CodeGenerationResponse(BaseModel):
    """Code generation response"""
    vulnerable_code: str = Field(..., description="Generated vulnerable code")
    fixed_code: Optional[str] = Field(None, description="Fixed version of code")
    explanation: str = Field(..., description="Explanation of the vulnerability")
    exploitation_steps: List[str] = Field(default_factory=list, description="Steps to exploit")


# ===== Leaderboard Models =====

class UserScore(BaseModel):
    """User score model for leaderboard"""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    total_score: int = Field(..., description="Total score")
    solved_challenges: int = Field(..., description="Number of solved challenges")
    rank: int = Field(..., description="User rank")
    last_solve: Optional[datetime] = Field(None, description="Last solve timestamp")


class Leaderboard(BaseModel):
    """Leaderboard model"""
    top_users: List[UserScore] = Field(..., description="Top users")
    total_users: int = Field(..., description="Total number of users")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")


# ===== CTF Lab Statistics Models =====

class VulnerabilityStats(BaseModel):
    """Statistics for a specific vulnerability type"""
    vulnerability_type: VulnerabilityType = Field(..., description="Vulnerability type")
    total_challenges: int = Field(..., description="Total challenges of this type")
    total_attempts: int = Field(..., description="Total submission attempts")
    successful_solves: int = Field(..., description="Successful solves")
    average_solve_time: Optional[float] = Field(None, description="Average solve time in minutes")


class LabStats(BaseModel):
    """Overall lab statistics"""
    total_users: int = Field(..., description="Total registered users")
    total_challenges: int = Field(..., description="Total challenges")
    total_submissions: int = Field(..., description="Total submissions")
    vulnerability_breakdown: List[VulnerabilityStats] = Field(default_factory=list)
    most_solved_challenge: Optional[str] = Field(None, description="Most solved challenge ID")
    hardest_challenge: Optional[str] = Field(None, description="Challenge with lowest solve rate")


# ===== Configuration Models =====

class DatabaseConfig(BaseModel):
    """Database configuration"""
    mongodb_uri: str = Field(..., description="MongoDB Atlas URI")
    database_name: str = Field(default="ctf_lab", description="Database name")
    max_pool_size: int = Field(default=10, description="Maximum connection pool size")


class SecurityConfig(BaseModel):
    """Security configuration"""
    secret_key: str = Field(..., min_length=32, description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")
    password_hash_scheme: str = Field(default="bcrypt", description="Password hashing scheme")


class LlamaCppConfig(BaseModel):
    """Llama.cpp configuration"""
    model_path: str = Field(..., description="Path to llama model file")
    n_ctx: int = Field(default=2048, description="Context size")
    n_threads: int = Field(default=4, description="Number of threads")
    n_gpu_layers: int = Field(default=0, description="Number of GPU layers")


class GoogleGenAIConfig(BaseModel):
    """Google GenAI configuration"""
    api_key: str = Field(..., description="Google API key")
    model_name: str = Field(default="gemini-2.5-flash", description="Model name")
    temperature: float = Field(default=0.7, description="Generation temperature")


class AppConfig(BaseModel):
    """Application configuration"""
    app_name: str = Field(default="CTF Security Lab", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    api_version: str = Field(default="v1", description="API version")
    cors_origins: List[str] = Field(default_factory=list, description="CORS origins")
    database: DatabaseConfig
    security: SecurityConfig
    llama_cpp: Optional[LlamaCppConfig] = None
    google_genai: GoogleGenAIConfig
