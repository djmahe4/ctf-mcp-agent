"""
Steganography and Encoding Utilities
Implements various encoding and steganography techniques for CTF challenges
"""

import base64
import binascii
from typing import Tuple, List
from PIL import Image
import numpy as np


class Base64Utils:
    """Base64 encoding/decoding utilities with variations"""
    
    @staticmethod
    def encode_multiple_times(data: str, count: int = 1) -> str:
        """
        Encode data multiple times with Base64
        
        Args:
            data: Data to encode
            count: Number of times to encode
        
        Returns:
            Multi-encoded string
        """
        encoded = data.encode()
        for _ in range(count):
            encoded = base64.b64encode(encoded)
        return encoded.decode()
    
    @staticmethod
    def decode_multiple_times(data: str, count: int = 1) -> str:
        """
        Decode Base64 encoded data multiple times
        
        Args:
            data: Encoded data
            count: Number of times to decode
        
        Returns:
            Decoded string
        """
        decoded = data.encode()
        for _ in range(count):
            decoded = base64.b64decode(decoded)
        return decoded.decode()
    
    @staticmethod
    def encode_urlsafe(data: str) -> str:
        """URL-safe Base64 encoding"""
        return base64.urlsafe_b64encode(data.encode()).decode()
    
    @staticmethod
    def decode_urlsafe(data: str) -> str:
        """URL-safe Base64 decoding"""
        return base64.urlsafe_b64decode(data.encode()).decode()
    
    @staticmethod
    def encode_base32(data: str) -> str:
        """Base32 encoding"""
        return base64.b32encode(data.encode()).decode()
    
    @staticmethod
    def decode_base32(data: str) -> str:
        """Base32 decoding"""
        return base64.b32decode(data.encode()).decode()
    
    @staticmethod
    def encode_base85(data: str) -> str:
        """Base85 (ASCII85) encoding"""
        return base64.b85encode(data.encode()).decode()
    
    @staticmethod
    def decode_base85(data: str) -> str:
        """Base85 (ASCII85) decoding"""
        return base64.b85decode(data.encode()).decode()


class HexUtils:
    """Hexadecimal encoding utilities"""
    
    @staticmethod
    def encode(data: str) -> str:
        """Encode string to hex"""
        return binascii.hexlify(data.encode()).decode()
    
    @staticmethod
    def decode(hex_data: str) -> str:
        """Decode hex to string"""
        return binascii.unhexlify(hex_data.encode()).decode()
    
    @staticmethod
    def encode_with_spacing(data: str, separator: str = " ") -> str:
        """Encode to hex with custom separator"""
        hex_str = HexUtils.encode(data)
        return separator.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)])


class BinaryUtils:
    """Binary encoding utilities"""
    
    @staticmethod
    def encode(data: str) -> str:
        """Encode string to binary"""
        return ' '.join(format(ord(char), '08b') for char in data)
    
    @staticmethod
    def decode(binary_data: str) -> str:
        """Decode binary to string"""
        binary_values = binary_data.split()
        return ''.join(chr(int(bv, 2)) for bv in binary_values)


class ROT13Utils:
    """ROT13 cipher utilities"""
    
    @staticmethod
    def encode(data: str) -> str:
        """Apply ROT13 transformation"""
        import codecs
        return codecs.encode(data, 'rot_13')
    
    @staticmethod
    def decode(data: str) -> str:
        """Decode ROT13 (same as encode)"""
        return ROT13Utils.encode(data)


class MorseCodeUtils:
    """Morse code utilities"""
    
    MORSE_CODE_DICT = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.', ' ': '/'
    }
    
    REVERSE_MORSE = {v: k for k, v in MORSE_CODE_DICT.items()}
    
    @staticmethod
    def encode(text: str) -> str:
        """Encode text to Morse code"""
        return ' '.join(MorseCodeUtils.MORSE_CODE_DICT.get(char.upper(), '') 
                       for char in text)
    
    @staticmethod
    def decode(morse: str) -> str:
        """Decode Morse code to text"""
        return ''.join(MorseCodeUtils.REVERSE_MORSE.get(code, '') 
                      for code in morse.split(' '))


class ImageLSBSteganography:
    """
    Least Significant Bit (LSB) Steganography for images
    Hides data in the least significant bits of pixel values
    """
    
    @staticmethod
    def encode_text_in_image(image_array: np.ndarray, text: str) -> np.ndarray:
        """
        Encode text into image using LSB
        
        Args:
            image_array: NumPy array of image
            text: Text to hide
        
        Returns:
            Modified image array with hidden text
        """
        # Convert text to binary
        binary_text = ''.join(format(ord(char), '08b') for char in text)
        binary_text += '1111111111111110'  # End marker
        
        # Flatten image
        flat_image = image_array.flatten()
        
        if len(binary_text) > len(flat_image):
            raise ValueError("Text too long for image capacity")
        
        # Embed binary data in LSB
        for i, bit in enumerate(binary_text):
            flat_image[i] = (flat_image[i] & 0xFE) | int(bit)
        
        # Reshape back to original shape
        return flat_image.reshape(image_array.shape)
    
    @staticmethod
    def decode_text_from_image(image_array: np.ndarray) -> str:
        """
        Extract hidden text from image using LSB
        
        Args:
            image_array: NumPy array of stego image
        
        Returns:
            Hidden text
        """
        # Flatten image
        flat_image = image_array.flatten()
        
        # Extract LSBs
        binary_text = ''
        for pixel in flat_image:
            binary_text += str(pixel & 1)
        
        # Find end marker
        end_marker = '1111111111111110'
        end_pos = binary_text.find(end_marker)
        
        if end_pos == -1:
            raise ValueError("No hidden message found")
        
        binary_text = binary_text[:end_pos]
        
        # Convert binary to text
        text = ''
        for i in range(0, len(binary_text), 8):
            byte = binary_text[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        
        return text
    
    @staticmethod
    def create_stego_image(original_image_path: str, text: str, output_path: str):
        """
        Create a steganographic image file
        
        Args:
            original_image_path: Path to original image
            text: Text to hide
            output_path: Path to save stego image
        """
        # Load image
        img = Image.open(original_image_path)
        img_array = np.array(img)
        
        # Encode text
        stego_array = ImageLSBSteganography.encode_text_in_image(img_array, text)
        
        # Save stego image
        stego_img = Image.fromarray(stego_array.astype('uint8'))
        stego_img.save(output_path)
    
    @staticmethod
    def extract_from_stego_image(stego_image_path: str) -> str:
        """
        Extract hidden text from steganographic image
        
        Args:
            stego_image_path: Path to stego image
        
        Returns:
            Hidden text
        """
        img = Image.open(stego_image_path)
        img_array = np.array(img)
        return ImageLSBSteganography.decode_text_from_image(img_array)


class MultiLayerEncoder:
    """
    Multi-layer encoding with different techniques
    """
    
    @staticmethod
    def encode_with_layers(data: str, layers: List[str]) -> str:
        """
        Apply multiple encoding layers
        
        Args:
            data: Original data
            layers: List of encoding types to apply in order
        
        Returns:
            Multi-encoded data
        """
        encoded = data
        
        encoding_map = {
            'base64': lambda x: base64.b64encode(x.encode()).decode(),
            'base32': lambda x: base64.b32encode(x.encode()).decode(),
            'base85': lambda x: base64.b85encode(x.encode()).decode(),
            'hex': lambda x: binascii.hexlify(x.encode()).decode(),
            'rot13': lambda x: ROT13Utils.encode(x),
            'binary': lambda x: BinaryUtils.encode(x),
            'morse': lambda x: MorseCodeUtils.encode(x),
            'url': lambda x: Base64Utils.encode_urlsafe(x),
        }
        
        for layer in layers:
            if layer in encoding_map:
                encoded = encoding_map[layer](encoded)
        
        return encoded
    
    @staticmethod
    def decode_with_layers(data: str, layers: List[str]) -> str:
        """
        Decode multi-layered encoded data
        
        Args:
            data: Encoded data
            layers: List of encoding types (in reverse order)
        
        Returns:
            Decoded data
        """
        decoded = data
        
        decoding_map = {
            'base64': lambda x: base64.b64decode(x.encode()).decode(),
            'base32': lambda x: base64.b32decode(x.encode()).decode(),
            'base85': lambda x: base64.b85decode(x.encode()).decode(),
            'hex': lambda x: binascii.unhexlify(x.encode()).decode(),
            'rot13': lambda x: ROT13Utils.decode(x),
            'binary': lambda x: BinaryUtils.decode(x),
            'morse': lambda x: MorseCodeUtils.decode(x),
            'url': lambda x: Base64Utils.decode_urlsafe(x),
        }
        
        # Decode in reverse order
        for layer in reversed(layers):
            if layer in decoding_map:
                decoded = decoding_map[layer](decoded)
        
        return decoded


class CaesarCipher:
    """Caesar cipher implementation"""
    
    @staticmethod
    def encrypt(text: str, shift: int) -> str:
        """Encrypt text with Caesar cipher"""
        result = []
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                shifted = (ord(char) - ascii_offset + shift) % 26 + ascii_offset
                result.append(chr(shifted))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def decrypt(text: str, shift: int) -> str:
        """Decrypt Caesar cipher"""
        return CaesarCipher.encrypt(text, -shift)
    
    @staticmethod
    def brute_force(ciphertext: str) -> List[Tuple[int, str]]:
        """Try all possible Caesar shifts"""
        results = []
        for shift in range(26):
            decrypted = CaesarCipher.decrypt(ciphertext, shift)
            results.append((shift, decrypted))
        return results


class WhitespaceStego:
    """
    Whitespace steganography - hide data in spaces and tabs
    """
    
    @staticmethod
    def encode(text: str, data: str) -> str:
        """
        Hide data in whitespace at end of lines
        
        Args:
            text: Cover text
            data: Data to hide
        
        Returns:
            Text with hidden data in whitespace
        """
        # Convert data to binary
        binary_data = ''.join(format(ord(c), '08b') for c in data)
        
        lines = text.split('\n')
        result = []
        
        for i, line in enumerate(lines):
            if i < len(binary_data):
                # Add space for 0, tab for 1
                whitespace = ' ' if binary_data[i] == '0' else '\t'
                result.append(line + whitespace)
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    @staticmethod
    def decode(text: str) -> str:
        """
        Extract data from whitespace
        
        Args:
            text: Text with hidden data
        
        Returns:
            Hidden data
        """
        lines = text.split('\n')
        binary_data = ''
        
        for line in lines:
            if line.endswith(' '):
                binary_data += '0'
            elif line.endswith('\t'):
                binary_data += '1'
        
        # Convert binary to text
        result = ''
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            if len(byte) == 8:
                result += chr(int(byte, 2))
        
        return result


def generate_encoded_flag(flag: str, difficulty: str = "medium") -> dict:
    """
    Generate an encoded flag based on difficulty
    
    Args:
        flag: Original flag
        difficulty: Challenge difficulty
    
    Returns:
        Dict with encoded flag and hints
    """
    if difficulty == "easy":
        # Single Base64 encoding
        encoded = base64.b64encode(flag.encode()).decode()
        return {
            "encoded_flag": encoded,
            "encoding_layers": ["base64"],
            "hint": "This looks like Base64 encoding..."
        }
    
    elif difficulty == "medium":
        # Multiple encodings
        layers = ["base64", "hex", "base64"]
        encoded = MultiLayerEncoder.encode_with_layers(flag, layers)
        return {
            "encoded_flag": encoded,
            "encoding_layers": layers,
            "hint": "Multiple encoding layers detected. Work backwards!"
        }
    
    elif difficulty == "hard":
        # Complex multi-layer
        layers = ["rot13", "base64", "hex", "base32", "base64"]
        encoded = MultiLayerEncoder.encode_with_layers(flag, layers)
        return {
            "encoded_flag": encoded,
            "encoding_layers": layers,
            "hint": "5 layers of encoding. Can you identify each one?"
        }
    
    else:  # expert
        # Extremely complex
        layers = ["morse", "base85", "hex", "base64", "base32", "rot13", "base64"]
        encoded = MultiLayerEncoder.encode_with_layers(flag, layers)
        return {
            "encoded_flag": encoded,
            "encoding_layers": layers,
            "hint": "This is madness! 7 encoding layers await you..."
        }
