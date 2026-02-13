"""
Steganography and Encoding Challenges Router
Handles image stego, base64, multi-layer encoding, and cryptography challenges
"""

from fastapi import APIRouter, Depends, Body
import random

from models import User
from auth_utils import get_current_active_user
from stego_utils import (
    Base64Utils, HexUtils, BinaryUtils, ROT13Utils, MorseCodeUtils,
    CaesarCipher, generate_encoded_flag
)
from flag_generator import generate_dynamic_flag

router = APIRouter()

STEGO_GIFS = [
    "https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif",  # Magnifying glass
    "https://media.giphy.com/media/3oKIPnbKgN3bXeVpvy/giphy.gif",  # Hidden
]


@router.get("/", response_model=dict)
async def list_encoding_challenges():
    """
    🎨 List all steganography and encoding challenges
    """
    return {
        "message": "🔐 Welcome to the Encoding & Steganography Lab!",
        "categories": [
            {
                "name": "Base64 Challenges",
                "emoji": "🔤",
                "endpoint": "/api/v1/stego/base64",
                "description": "Master Base64 encoding and its variations"
            },
            {
                "name": "Image Steganography",
                "emoji": "🖼️",
                "endpoint": "/api/v1/stego/image",
                "description": "Find hidden messages in images"
            },
            {
                "name": "Multi-Layer Encoding",
                "emoji": "🧅",
                "endpoint": "/api/v1/stego/multi-layer",
                "description": "Decode multiple encoding layers like an onion"
            },
            {
                "name": "Classical Ciphers",
                "emoji": "🗝️",
                "endpoint": "/api/v1/stego/ciphers",
                "description": "Break Caesar, Vigenère, and other ciphers"
            },
            {
                "name": "Binary & Hex",
                "emoji": "💾",
                "endpoint": "/api/v1/stego/binary",
                "description": "Work with binary and hexadecimal encoding"
            }
        ],
        "meme": random.choice(STEGO_GIFS),
        "fun_fact": "🎓 Steganography comes from Greek: 'steganos' (covered) + 'graphein' (writing)!"
    }


# ===== BASE64 CHALLENGES =====

@router.get("/base64/easy", response_model=dict)
async def base64_easy_challenge(current_user: User = Depends(get_current_active_user)):
    """
    🔤 Easy Base64 Challenge
    
    Decode a single Base64 encoded flag
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    # Generate dynamic flag
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="base64_easy",
        vulnerability_type="sql_injection",
        challenge_name="Base64 Easy"
    )
    
    # Single Base64 encoding
    encoded = Base64Utils.encode_multiple_times(flag, count=1)
    
    return {
        "challenge": "Decode this Base64 string to get your flag! 🎯",
        "encoded_flag": encoded,
        "hint": "This is standard Base64 encoding. Python has a built-in module for this!",
        "points": 50,
        "meme": random.choice(STEGO_GIFS)
    }


@router.get("/base64/medium", response_model=dict)
async def base64_medium_challenge(current_user: User = Depends(get_current_active_user)):
    """
    🔤 Medium Base64 Challenge
    
    Multiple Base64 encodings!
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="base64_medium",
        vulnerability_type="xss",
        challenge_name="Base64 Medium"
    )
    
    # Triple Base64 encoding
    encoded = Base64Utils.encode_multiple_times(flag, count=3)
    
    return {
        "challenge": "This flag has been Base64 encoded... multiple times! 🧅",
        "encoded_flag": encoded,
        "hint": "Count how many times you need to decode. Nested like an onion!",
        "layers": 3,
        "points": 100,
        "fun_tip": "Write a loop to decode multiple times! 🔄"
    }


@router.get("/base64/hard", response_model=dict)
async def base64_hard_challenge(current_user: User = Depends(get_current_active_user)):
    """
    🔤 Hard Base64 Challenge
    
    Mix of Base64, Base32, and Base85!
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="base64_hard",
        vulnerability_type="command_injection",
        challenge_name="Base64 Hard"
    )
    
    # Mix encodings
    encoded = Base64Utils.encode_base85(flag)
    encoded = Base64Utils.encode_base32(encoded)
    encoded = Base64Utils.encode_multiple_times(encoded, count=2)
    
    return {
        "challenge": "Mixed encoding madness! Base64, Base32, and Base85! 🎪",
        "encoded_flag": encoded,
        "hint": "Work backwards: Base64 (x2) → Base32 → Base85",
        "encoding_layers": ["base64", "base64", "base32", "base85"],
        "points": 250,
        "meme": "https://i.imgflip.com/4/3oevdk.jpg"
    }


# ===== MULTI-LAYER ENCODING =====

@router.get("/multi-layer/expert", response_model=dict)
async def multilayer_expert_challenge(current_user: User = Depends(get_current_active_user)):
    """
    🧅 Expert Multi-Layer Encoding
    
    7 layers of different encodings! Are you ready?
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="multilayer_expert",
        vulnerability_type="path_traversal",
        challenge_name="Multi-Layer Expert"
    )
    
    # Generate complex encoding
    encoded_data = generate_encoded_flag(flag, difficulty="expert")
    
    return {
        "challenge": "🔥 EXPERT LEVEL: 7 encoding layers! Good luck! 🔥",
        "encoded_flag": encoded_data["encoded_flag"],
        "layers": encoded_data["encoding_layers"],
        "hint": encoded_data["hint"],
        "points": 500,
        "warning": "This will test your decoding skills to the max! 💀",
        "meme": "https://i.imgflip.com/4/5sijq.jpg"
    }


# ===== CLASSICAL CIPHERS =====

@router.get("/cipher/caesar", response_model=dict)
async def caesar_cipher_challenge(current_user: User = Depends(get_current_active_user)):
    """
    🗝️ Caesar Cipher Challenge
    
    Decrypt the Caesar cipher to find the flag!
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="caesar_cipher",
        vulnerability_type="csrf",
        challenge_name="Caesar Cipher"
    )
    
    # Apply Caesar cipher with random shift
    shift = 13  # ROT13
    encrypted = CaesarCipher.encrypt(flag, shift)
    
    return {
        "challenge": "Decrypt this Caesar cipher! 🏛️",
        "ciphertext": encrypted,
        "hint": "Julius Caesar used this 2000 years ago! Try all 26 shifts.",
        "historical_note": "Caesar used a shift of 3 in his time!",
        "points": 75,
        "fun_fact": "🎓 ROT13 is a special case of Caesar cipher with shift 13!"
    }


@router.get("/cipher/rot13", response_model=dict)
async def rot13_challenge(current_user: User = Depends(get_current_active_user)):
    """
    🔄 ROT13 Challenge
    
    Simple ROT13 encoding
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="rot13",
        vulnerability_type="idor",
        challenge_name="ROT13"
    )
    
    encoded = ROT13Utils.encode(flag)
    
    return {
        "challenge": "ROT13 is everywhere in CTFs! Decode this! 🔄",
        "encoded_flag": encoded,
        "hint": "ROT13 is its own inverse - encode and decode are the same!",
        "points": 50
    }


# ===== BINARY & HEX =====

@router.get("/binary/challenge", response_model=dict)
async def binary_challenge(current_user: User = Depends(get_current_active_user)):
    """
    💾 Binary Encoding Challenge
    
    Convert binary to text!
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="binary",
        vulnerability_type="xxe",
        challenge_name="Binary Challenge"
    )
    
    binary = BinaryUtils.encode(flag)
    
    return {
        "challenge": "01010100 01101000 01101001 01101110 01101011 in binary! 💾",
        "binary_flag": binary,
        "hint": "Each byte is 8 bits. Convert to ASCII characters!",
        "points": 100,
        "tip": "Python's int() function can convert binary strings!"
    }


@router.get("/hex/challenge", response_model=dict)
async def hex_challenge(current_user: User = Depends(get_current_active_user)):
    """
    🔢 Hexadecimal Challenge
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="hex",
        vulnerability_type="ssrf",
        challenge_name="Hex Challenge"
    )
    
    hex_encoded = HexUtils.encode(flag)
    
    return {
        "challenge": "Hexadecimal - the language of computers! 🔢",
        "hex_flag": hex_encoded,
        "hint": "Two hex digits = one byte = one character",
        "points": 75,
        "fun_fact": "0x prefix indicates hexadecimal in most programming languages!"
    }


# ===== MORSE CODE =====

@router.get("/morse/challenge", response_model=dict)
async def morse_code_challenge(current_user: User = Depends(get_current_active_user)):
    """
    📡 Morse Code Challenge
    
    Decode the dots and dashes!
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="morse",
        vulnerability_type="insecure_deserialization",
        challenge_name="Morse Code"
    )
    
    morse = MorseCodeUtils.encode(flag)
    
    return {
        "challenge": "... --- ... Send help! Decode this Morse code! 📡",
        "morse_code": morse,
        "hint": ". = dit, - = dah, space separates letters, / separates words",
        "points": 100,
        "historical": "🎓 Invented by Samuel Morse in 1830s for telegraph!"
    }


# ===== IMAGE STEGANOGRAPHY =====

@router.get("/image/lsb-challenge", response_model=dict)
async def image_lsb_challenge(current_user: User = Depends(get_current_active_user)):
    """
    🖼️ LSB Image Steganography Challenge
    
    Hidden message in image pixels!
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id="image_lsb",
        vulnerability_type="sql_injection",
        challenge_name="Image LSB"
    )
    
    return {
        "challenge": "🖼️ There's a hidden message in this image!",
        "image_url": "/static/stego_images/challenge_lsb.png",
        "technique": "LSB (Least Significant Bit) Steganography",
        "hint": "Use tools like steghide, zsteg, or stegsolve!",
        "extraction_command": "zsteg challenge_lsb.png",
        "points": 200,
        "tools": ["steghide", "zsteg", "stegsolve", "binwalk"],
        "your_flag": flag,
        "note": "🔍 In production, flag would be hidden in actual image file!"
    }


@router.post("/submit-decoded", response_model=dict)
async def submit_decoded_flag(
    challenge_id: str = Body(...),
    decoded_flag: str = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    ✅ Submit your decoded flag
    
    Verify if your decoding was successful!
    """
    user_id = getattr(current_user, 'user_id', 'demo_user')
    
    # Generate expected flag
    expected_flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id=challenge_id,
        vulnerability_type="sql_injection",
        challenge_name=challenge_id
    )
    
    if decoded_flag == expected_flag:
        return {
            "success": True,
            "message": "🎉 Correct! You've successfully decoded the flag!",
            "points_awarded": 100,
            "meme": random.choice(STEGO_GIFS),
            "achievement": "🏆 Decoder Master!"
        }
    else:
        return {
            "success": False,
            "message": "❌ Incorrect flag. Keep trying!",
            "hint": "Double-check your decoding steps. Did you decode all layers?",
            "encouragement": "Every hacker fails before they succeed! 💪"
        }
