"""
Steganography and Encoding Models
Various encoding, encryption, and steganography challenge models
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal, Dict, Any
from enum import Enum


class EncodingType(str, Enum):
    """Types of encoding schemes"""
    BASE64 = "base64"
    BASE32 = "base32"
    BASE85 = "base85"
    HEX = "hex"
    ROT13 = "rot13"
    BINARY = "binary"
    MORSE_CODE = "morse_code"
    URL_ENCODING = "url_encoding"
    HTML_ENTITIES = "html_entities"
    UNICODE_ESCAPE = "unicode_escape"
    CUSTOM_CIPHER = "custom_cipher"


class SteganographyType(str, Enum):
    """Types of steganography techniques"""
    LSB_IMAGE = "lsb_image"  # Least Significant Bit in images
    DCT_IMAGE = "dct_image"  # Discrete Cosine Transform
    AUDIO_SPECTRAL = "audio_spectral"  # Audio frequency spectrum
    TEXT_WHITESPACE = "text_whitespace"  # Whitespace steganography
    FILE_METADATA = "file_metadata"  # Hidden in file metadata
    PNG_CHUNK = "png_chunk"  # Hidden in PNG chunks
    JPEG_COMMENT = "jpeg_comment"  # JPEG comment field
    QR_CODE = "qr_code"  # Hidden in QR codes
    PALETTE_IMAGE = "palette_image"  # Image palette manipulation


class EncodingChallenge(BaseModel):
    """Model for encoding/decoding challenges"""
    challenge_id: str = Field(..., description="Unique challenge identifier")
    title: str = Field(..., description="Challenge title")
    description: str = Field(..., description="Challenge description")
    encoding_layers: List[EncodingType] = Field(..., description="Encoding layers applied")
    encoded_flag: str = Field(..., description="Encoded flag")
    hints: List[str] = Field(default_factory=list, description="Hints for decoding")
    difficulty: Literal["easy", "medium", "hard", "expert"] = Field(..., description="Challenge difficulty")
    points: int = Field(..., ge=10, le=1000, description="Points awarded")


class Base64Challenge(BaseModel):
    """Specific Base64 encoding challenge"""
    encoded_data: str = Field(..., description="Base64 encoded data")
    encoding_count: int = Field(default=1, ge=1, le=10, description="Number of encoding iterations")
    padding_tricks: bool = Field(default=False, description="Uses padding tricks")
    url_safe: bool = Field(default=False, description="Uses URL-safe Base64")
    custom_alphabet: Optional[str] = Field(None, description="Custom Base64 alphabet")


class ImageSteganographyChallenge(BaseModel):
    """Image steganography challenge model"""
    challenge_id: str = Field(..., description="Challenge identifier")
    title: str = Field(..., description="Challenge title")
    stego_type: SteganographyType = Field(..., description="Steganography technique used")
    image_format: Literal["png", "jpg", "bmp", "gif"] = Field(..., description="Image format")
    image_url: str = Field(..., description="URL to steganographic image")
    image_dimensions: Dict[str, int] = Field(..., description="Image width and height")
    extraction_method: str = Field(..., description="Method to extract hidden data")
    password_protected: bool = Field(default=False, description="Requires password to extract")
    extraction_password: Optional[str] = Field(None, description="Password if protected")
    hints: List[str] = Field(default_factory=list)


class AudioSteganographyChallenge(BaseModel):
    """Audio steganography challenge model"""
    challenge_id: str = Field(..., description="Challenge identifier")
    title: str = Field(..., description="Challenge title")
    audio_format: Literal["wav", "mp3", "ogg", "flac"] = Field(..., description="Audio format")
    audio_url: str = Field(..., description="URL to audio file")
    stego_technique: Literal["lsb", "echo_hiding", "phase_coding", "spectral"] = Field(
        ..., description="Audio steganography technique"
    )
    sample_rate: int = Field(..., description="Audio sample rate")
    duration_seconds: float = Field(..., description="Audio duration")
    extraction_tool: str = Field(..., description="Recommended tool for extraction")


class MultiLayerEncodingChallenge(BaseModel):
    """Multi-layer encoding challenge with multiple transformations"""
    challenge_id: str = Field(..., description="Challenge identifier")
    title: str = Field(..., description="Challenge title")
    encoding_pipeline: List[Dict[str, Any]] = Field(
        ..., 
        description="Ordered list of encoding operations"
    )
    final_encoded_data: str = Field(..., description="Final encoded result")
    complexity_score: int = Field(..., ge=1, le=10, description="Complexity rating")
    time_limit_minutes: Optional[int] = Field(None, description="Time limit for challenge")
    
    @validator('encoding_pipeline')
    def validate_pipeline(cls, v):
        if len(v) < 1:
            raise ValueError("Must have at least one encoding layer")
        if len(v) > 20:
            raise ValueError("Too many encoding layers (max 20)")
        return v


class QRCodeChallenge(BaseModel):
    """QR code based challenge"""
    challenge_id: str = Field(..., description="Challenge identifier")
    qr_image_url: str = Field(..., description="URL to QR code image")
    embedded_data_type: Literal["flag", "url", "encoded_text", "binary"] = Field(
        ..., description="Type of data in QR"
    )
    error_correction_level: Literal["L", "M", "Q", "H"] = Field(
        default="M", description="QR error correction level"
    )
    steganography_applied: bool = Field(default=False, description="Additional stego in QR")
    requires_manipulation: bool = Field(
        default=False, 
        description="Requires image manipulation to read"
    )


class FileFormatChallenge(BaseModel):
    """Challenge based on file format exploitation"""
    challenge_id: str = Field(..., description="Challenge identifier")
    file_type: Literal["zip", "pdf", "docx", "xlsx", "png", "jpg", "elf", "pe"] = Field(
        ..., description="File type"
    )
    file_url: str = Field(..., description="URL to download file")
    hidden_data_location: str = Field(..., description="Where data is hidden")
    extraction_technique: str = Field(..., description="Technique to extract")
    file_size_bytes: int = Field(..., description="File size in bytes")
    requires_tool: Optional[str] = Field(None, description="Required extraction tool")


class CipherChallenge(BaseModel):
    """Classical cipher challenge"""
    challenge_id: str = Field(..., description="Challenge identifier")
    cipher_type: Literal[
        "caesar", "vigenere", "playfair", "rail_fence", 
        "substitution", "transposition", "affine", "atbash"
    ] = Field(..., description="Type of cipher")
    ciphertext: str = Field(..., description="Encrypted text")
    key_hint: Optional[str] = Field(None, description="Hint about the key")
    has_key: bool = Field(..., description="Whether cipher uses a key")
    alphabet: str = Field(default="ABCDEFGHIJKLMNOPQRSTUVWXYZ", description="Cipher alphabet")


class PolyglotFileChallenge(BaseModel):
    """Polyglot file challenge (file valid in multiple formats)"""
    challenge_id: str = Field(..., description="Challenge identifier")
    file_formats: List[str] = Field(..., description="Valid formats for this file")
    file_url: str = Field(..., description="URL to polyglot file")
    primary_format: str = Field(..., description="Primary file format")
    hidden_format: str = Field(..., description="Format containing hidden data")
    extraction_method: str = Field(..., description="How to extract hidden data")


class MetadataChallenge(BaseModel):
    """Challenge based on file metadata"""
    challenge_id: str = Field(..., description="Challenge identifier")
    file_type: str = Field(..., description="Type of file")
    file_url: str = Field(..., description="URL to file")
    metadata_fields: List[str] = Field(..., description="Relevant metadata fields")
    extraction_tool: str = Field(default="exiftool", description="Tool to extract metadata")
    hidden_in_field: str = Field(..., description="Which metadata field has the flag")


class BinaryAnalysisChallenge(BaseModel):
    """Binary file analysis challenge"""
    challenge_id: str = Field(..., description="Challenge identifier")
    binary_type: Literal["elf", "pe", "mach-o", "raw"] = Field(..., description="Binary type")
    architecture: Literal["x86", "x64", "arm", "mips"] = Field(..., description="CPU architecture")
    binary_url: str = Field(..., description="URL to binary file")
    analysis_objective: str = Field(..., description="What to find in binary")
    requires_disassembly: bool = Field(default=True, description="Needs disassembly")
    requires_debugging: bool = Field(default=False, description="Needs debugging")
    recommended_tools: List[str] = Field(
        default_factory=lambda: ["ghidra", "ida", "radare2", "gdb"]
    )


class NetworkPacketChallenge(BaseModel):
    """Network packet analysis challenge"""
    challenge_id: str = Field(..., description="Challenge identifier")
    pcap_url: str = Field(..., description="URL to PCAP file")
    protocol: str = Field(..., description="Network protocol to analyze")
    packet_count: int = Field(..., description="Number of packets")
    file_size_mb: float = Field(..., description="PCAP file size in MB")
    analysis_tool: str = Field(default="wireshark", description="Recommended analysis tool")
    flag_location: str = Field(..., description="Where flag is hidden in packets")


class MemoryForensicsChallenge(BaseModel):
    """Memory dump forensics challenge"""
    challenge_id: str = Field(..., description="Challenge identifier")
    memory_dump_url: str = Field(..., description="URL to memory dump")
    os_type: Literal["windows", "linux", "mac"] = Field(..., description="Operating system")
    dump_size_mb: int = Field(..., description="Memory dump size")
    volatility_profile: str = Field(..., description="Volatility profile to use")
    objective: str = Field(..., description="What to find in memory")
    recommended_plugins: List[str] = Field(default_factory=list, description="Volatility plugins")


class CryptoChallenge(BaseModel):
    """Cryptography challenge"""
    challenge_id: str = Field(..., description="Challenge identifier")
    crypto_type: Literal[
        "rsa", "aes", "des", "md5_collision", "hash_crack",
        "weak_random", "ecb_mode", "padding_oracle", "timing_attack"
    ] = Field(..., description="Type of crypto challenge")
    encrypted_data: str = Field(..., description="Encrypted or hashed data")
    public_key: Optional[str] = Field(None, description="Public key if applicable")
    algorithm_details: Dict[str, Any] = Field(default_factory=dict, description="Algorithm parameters")
    weakness: str = Field(..., description="Cryptographic weakness to exploit")


class StegoImageMetadata(BaseModel):
    """Metadata for steganographic images"""
    original_size: int = Field(..., description="Original image size in bytes")
    stego_size: int = Field(..., description="Steganographic image size")
    capacity_bytes: int = Field(..., description="Hidden data capacity")
    embedding_rate: float = Field(..., ge=0.0, le=1.0, description="Embedding rate (0-1)")
    quality_score: float = Field(..., ge=0.0, le=100.0, description="Image quality after embedding")


class EncodingSubmission(BaseModel):
    """Submission for encoding/steganography challenges"""
    challenge_id: str = Field(..., description="Challenge ID")
    decoded_flag: str = Field(..., description="Decoded flag attempt")
    decoding_method: Optional[str] = Field(None, description="Method used to decode")
    tools_used: List[str] = Field(default_factory=list, description="Tools used")


class SteganographySetup(BaseModel):
    """Configuration for steganography system setup"""
    image_storage_path: str = Field(default="/app/stego_images", description="Path for images")
    audio_storage_path: str = Field(default="/app/stego_audio", description="Path for audio files")
    max_image_size_mb: int = Field(default=10, description="Max image size")
    max_audio_size_mb: int = Field(default=20, description="Max audio size")
    supported_image_formats: List[str] = Field(
        default_factory=lambda: ["png", "jpg", "bmp", "gif"]
    )
    supported_audio_formats: List[str] = Field(
        default_factory=lambda: ["wav", "mp3", "ogg", "flac"]
    )
    enable_image_stego: bool = Field(default=True)
    enable_audio_stego: bool = Field(default=True)
    enable_text_stego: bool = Field(default=True)


class EncodingLayerConfig(BaseModel):
    """Configuration for a single encoding layer"""
    encoding_type: EncodingType = Field(..., description="Type of encoding")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Encoding parameters")
    description: str = Field(..., description="Description of this layer")
    difficulty_contribution: int = Field(default=1, ge=1, le=5, description="Adds to difficulty")
