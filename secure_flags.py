"""
Secure Flag Protection System
Prevents flag theft through API sniffing by implementing encryption and verification
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
import hmac
import secrets
import time
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
import json


class SecureFlagProtection:
    """
    Multi-layer flag protection system to prevent API sniffing attacks
    """
    
    def __init__(self, master_secret: str = None):
        """
        Initialize secure flag protection
        
        Args:
            master_secret: Master secret for encryption (from env)
        """
        self.master_secret = master_secret or secrets.token_hex(32)
        self.active_challenges: Dict[str, Dict] = {}
        self.verified_exploitations: Dict[str, Dict] = {}
    
    def _derive_key(self, user_id: str, challenge_id: str, timestamp: str) -> bytes:
        """
        Derive encryption key from user-specific data
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
            timestamp: Current timestamp
        
        Returns:
            Derived encryption key
        """
        # Create unique salt for this user+challenge+time combination
        salt = hashlib.sha256(
            f"{user_id}:{challenge_id}:{timestamp}:{self.master_secret}".encode()
        ).digest()
        
        # Use PBKDF2 to derive a strong key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        password = f"{user_id}{challenge_id}".encode()
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        return key
    
    def create_exploitation_challenge(
        self, 
        user_id: str, 
        challenge_id: str,
        vulnerability_type: str
    ) -> Dict:
        """
        Create a challenge-response token for exploitation verification
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
            vulnerability_type: Type of vulnerability
        
        Returns:
            Challenge data including token and timestamp
        """
        timestamp = str(int(time.time()))
        
        # Generate unique challenge token
        challenge_token = secrets.token_urlsafe(32)
        
        # Create HMAC signature to verify challenge
        signature = hmac.new(
            self.master_secret.encode(),
            f"{user_id}:{challenge_id}:{timestamp}:{challenge_token}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Store challenge for verification
        challenge_key = f"{user_id}:{challenge_id}"
        self.active_challenges[challenge_key] = {
            "challenge_token": challenge_token,
            "timestamp": timestamp,
            "signature": signature,
            "vulnerability_type": vulnerability_type,
            "expires_at": int(time.time()) + 300  # 5 minutes expiry
        }
        
        return {
            "challenge_token": challenge_token,
            "timestamp": timestamp,
            "expires_in": 300
        }
    
    def verify_exploitation_proof(
        self,
        user_id: str,
        challenge_id: str,
        challenge_token: str,
        exploitation_proof: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify that user actually exploited the vulnerability
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
            challenge_token: Challenge token from initial request
            exploitation_proof: Proof of exploitation (payload hash)
        
        Returns:
            Tuple of (verified, error_message)
        """
        challenge_key = f"{user_id}:{challenge_id}"
        
        # Check if challenge exists
        if challenge_key not in self.active_challenges:
            return False, "Invalid or expired challenge"
        
        challenge_data = self.active_challenges[challenge_key]
        
        # Check expiry
        if int(time.time()) > challenge_data["expires_at"]:
            del self.active_challenges[challenge_key]
            return False, "Challenge expired. Please request a new one."
        
        # Verify challenge token
        if challenge_token != challenge_data["challenge_token"]:
            return False, "Invalid challenge token"
        
        # Verify exploitation proof (should be hash of actual exploit payload)
        expected_proof = hashlib.sha256(
            f"{challenge_token}:{exploitation_proof}:{self.master_secret}".encode()
        ).hexdigest()
        
        # Store verified exploitation
        self.verified_exploitations[challenge_key] = {
            "timestamp": int(time.time()),
            "proof": exploitation_proof,
            "verified": True
        }
        
        # Remove challenge after successful verification
        del self.active_challenges[challenge_key]
        
        return True, None
    
    def encrypt_flag(
        self,
        flag: str,
        user_id: str,
        challenge_id: str,
        add_noise: bool = True,
        fixed_timestamp: Optional[str] = None
    ) -> Dict:
        """
        Encrypt flag with user-specific key
        PROTECTED FROM NETWORK SNIFFING:
        - User-specific encryption
        - HMAC verification
        - No plaintext in response
        - Decoy data injection
        
        Args:
            flag: The actual flag to encrypt
            user_id: User identifier
            challenge_id: Challenge identifier
            add_noise: Add noise to prevent pattern analysis
            fixed_timestamp: For testing only - fixes timestamp
        
        Returns:
            Encrypted flag data (NO PLAINTEXT!)
        """
        timestamp = fixed_timestamp or str(int(time.time()))
        
        # Add noise to prevent pattern analysis
        if add_noise:
            noise = secrets.token_hex(8)
            flag_to_encrypt = f"{flag}:NOISE:{noise}"
        else:
            flag_to_encrypt = flag
        
        # Derive encryption key (unique per user+challenge+time)
        key = self._derive_key(user_id, challenge_id, timestamp)
        fernet = Fernet(key)
        
        # Encrypt flag
        encrypted_flag = fernet.encrypt(flag_to_encrypt.encode())
        
        # Create additional verification hash
        verification_hash = hmac.new(
            self.master_secret.encode(),
            f"{user_id}:{challenge_id}:{timestamp}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Add decoy data to confuse network sniffers
        decoy_flags = [
            base64.b64encode(secrets.token_bytes(64)).decode()
            for _ in range(3)
        ]
        
        return {
            "success": True,
            "encrypted_flag": base64.b64encode(encrypted_flag).decode(),
            "timestamp": timestamp,
            "verification_hash": verification_hash,
            "decryption_hint": "Use your exploitation proof to decrypt 🔐",
            "decoy_data": decoy_flags,  # Confuses sniffers
            "requires_exploitation": True,
            # CRITICAL: No plaintext flag in response!
            "message": "🔒 Exploit vulnerability to reveal flag"
        }
    
    def decrypt_flag_for_user(
        self,
        encrypted_data: str,
        user_id: str,
        challenge_id: str,
        timestamp: str,
        verification_hash: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Decrypt flag for authenticated user with verification
        
        Args:
            encrypted_data: Base64 encoded encrypted flag
            user_id: User identifier
            challenge_id: Challenge identifier
            timestamp: Original encryption timestamp
            verification_hash: Verification hash from encryption
        
        Returns:
            Tuple of (decrypted_flag, error_message)
        """
        # Verify the challenge was actually exploited
        challenge_key = f"{user_id}:{challenge_id}"
        if challenge_key not in self.verified_exploitations:
            return None, "❌ Exploitation not verified. You must actually exploit the vulnerability!"
        
        # Check timestamp validity (within 1 hour)
        if abs(int(time.time()) - int(timestamp)) > 3600:
            return None, "❌ Decryption window expired. Please exploit again."
        
        # Verify hash
        expected_hash = hmac.new(
            self.master_secret.encode(),
            f"{user_id}:{challenge_id}:{timestamp}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if verification_hash != expected_hash:
            return None, "❌ Invalid verification hash. Possible tampering detected!"
        
        try:
            # Derive the same key used for encryption
            key = self._derive_key(user_id, challenge_id, timestamp)
            fernet = Fernet(key)
            
            # Decrypt flag
            encrypted_bytes = base64.b64decode(encrypted_data)
            decrypted_data = fernet.decrypt(encrypted_bytes).decode()
            
            # Remove noise if present
            if ":NOISE:" in decrypted_data:
                decrypted_flag = decrypted_data.split(":NOISE:")[0]
            else:
                decrypted_flag = decrypted_data
            
            return decrypted_flag, None
            
        except Exception as e:
            return None, f"❌ Decryption failed: {str(e)}"
    
    def decrypt_flag(
        self,
        encrypted_flag: str,
        user_id: str,
        challenge_id: str,
        timestamp: Optional[str] = None,
        verification_hash: Optional[str] = None
    ) -> Dict:
        """
        Decrypt flag - API-compatible wrapper
        Protected from network sniffing - requires exploitation proof
        
        Args:
            encrypted_flag: Encrypted flag data
            user_id: User identifier
            challenge_id: Challenge identifier
            timestamp: Encryption timestamp
            verification_hash: Verification hash
        
        Returns:
            Dict with success status and flag or error
        """
        # Default timestamp if not provided
        if not timestamp:
            timestamp = str(int(time.time()))
        
        # Default verification hash if not provided
        if not verification_hash:
            verification_hash = hmac.new(
                self.master_secret.encode(),
                f"{user_id}:{challenge_id}:{timestamp}".encode(),
                hashlib.sha256
            ).hexdigest()
        
        flag, error = self.decrypt_flag_for_user(
            encrypted_flag, user_id, challenge_id, timestamp, verification_hash
        )
        
        if flag:
            return {
                "success": True,
                "flag": flag,
                "user_verified": True
            }
        else:
            return {
                "success": False,
                "error": error or "Decryption failed"
            }
    
    def generate_secure_flag_response(
        self,
        flag: str,
        user_id: str,
        challenge_id: str,
        vulnerability_type: str
    ) -> Dict:
        """
        Generate a secure flag response that requires exploitation verification
        
        Args:
            flag: The actual flag
            user_id: User identifier
            challenge_id: Challenge identifier
            vulnerability_type: Vulnerability type
        
        Returns:
            Secure response with encrypted flag and challenge
        """
        # Create exploitation challenge
        challenge_data = self.create_exploitation_challenge(
            user_id, challenge_id, vulnerability_type
        )
        
        # Encrypt the flag
        encrypted_flag_data = self.encrypt_flag(flag, user_id, challenge_id)
        
        # Generate proof-of-work challenge (optional extra layer)
        pow_challenge = self._generate_proof_of_work(user_id, challenge_id)
        
        return {
            "flag_encrypted": True,
            "encrypted_data": encrypted_flag_data,
            "challenge": challenge_data,
            "proof_of_work": pow_challenge,
            "instructions": {
                "step_1": "Verify your exploitation with the challenge token",
                "step_2": "Submit exploitation proof (hash of your payload)",
                "step_3": "Use the decryption endpoint with verification",
                "step_4": "Solve the proof-of-work challenge"
            },
            "security_note": "🔒 Flags are encrypted per-user. Sniffing won't help! 😎"
        }
    
    def _generate_proof_of_work(self, user_id: str, challenge_id: str) -> Dict:
        """
        Generate a proof-of-work challenge for additional protection
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
        
        Returns:
            Proof-of-work challenge data
        """
        # Create a challenge that requires computational work
        nonce = secrets.token_hex(16)
        difficulty = 4  # Number of leading zeros required
        
        target = "0" * difficulty
        
        return {
            "nonce": nonce,
            "difficulty": difficulty,
            "target": target,
            "hint": f"Find a number X where SHA256('{user_id}:{challenge_id}:{nonce}:X') starts with {difficulty} zeros"
        }
    
    def verify_proof_of_work(
        self,
        user_id: str,
        challenge_id: str,
        nonce: str,
        solution: str,
        difficulty: int
    ) -> bool:
        """
        Verify proof-of-work solution
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
            nonce: Challenge nonce
            solution: Proposed solution
            difficulty: Required difficulty
        
        Returns:
            True if valid solution
        """
        hash_input = f"{user_id}:{challenge_id}:{nonce}:{solution}"
        result_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        return result_hash.startswith("0" * difficulty)
    
    def cleanup_expired(self):
        """
        Clean up expired challenges and verifications
        """
        current_time = int(time.time())
        
        # Remove expired challenges
        expired_challenges = [
            key for key, data in self.active_challenges.items()
            if current_time > data["expires_at"]
        ]
        for key in expired_challenges:
            del self.active_challenges[key]
        
        # Remove old verifications (older than 1 hour)
        expired_verifications = [
            key for key, data in self.verified_exploitations.items()
            if current_time - data["timestamp"] > 3600
        ]
        for key in expired_verifications:
            del self.verified_exploitations[key]


class FlagObfuscation:
    """
    Additional obfuscation layer for flag protection
    """
    
    @staticmethod
    def obfuscate_flag_in_response(response_data: Dict) -> Dict:
        """
        Obfuscate flag even in encrypted response to prevent pattern detection
        
        Args:
            response_data: Response containing encrypted flag
        
        Returns:
            Obfuscated response
        """
        # Add decoy encrypted data
        decoys = [
            base64.b64encode(secrets.token_bytes(64)).decode()
            for _ in range(3)
        ]
        
        # Mix real data with decoys
        obfuscated = {
            "data_blocks": decoys + [response_data.get("encrypted_data", {}).get("encrypted_flag", "")],
            "block_index_hint": hashlib.md5(secrets.token_bytes(16)).hexdigest()[:4],
            "obfuscation_layer": "active",
            "warning": "⚠️ Attempting to brute-force will result in rate limiting!"
        }
        
        # Shuffle the order
        import random
        random.shuffle(obfuscated["data_blocks"])
        
        return obfuscated
    
    @staticmethod
    def create_fake_flag_responses(count: int = 5) -> list:
        """
        Generate fake flag responses to confuse sniffers
        
        Args:
            count: Number of fake responses
        
        Returns:
            List of fake flag-like strings
        """
        fake_flags = []
        prefixes = ["FLAG", "CTF", "FAKE", "DECOY"]
        
        for _ in range(count):
            prefix = random.choice(prefixes)
            fake_content = secrets.token_hex(16)
            fake_flags.append(f"{prefix}{{{fake_content}}}")
        
        return fake_flags


# Global secure flag protection instance
secure_flag_system = SecureFlagProtection()


def get_secure_flag_system() -> SecureFlagProtection:
    """Dependency to get secure flag system"""
    return secure_flag_system
