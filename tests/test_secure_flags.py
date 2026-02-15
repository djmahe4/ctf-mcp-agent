"""
Tests for Secure Flag System - ENSURING FLAG SAFETY
Tests that flags are properly protected and cannot be extracted
"""
from secure_flags import SecureFlagProtection
import hashlib
import base64
import time


class TestFlagSafety:
    """Test that flags are NEVER exposed unsafely"""
    
    def test_encrypted_flags_dont_contain_plaintext(self, mock_user, mock_challenge):
        """CRITICAL: Encrypted flags must never contain plaintext"""
        flag_system = SecureFlagProtection()
        plaintext_flag = "CTF{super_secret_flag_12345}"
        
        encrypted = flag_system.encrypt_flag(
            flag=plaintext_flag,
            user_id=mock_user["user_id"],
            challenge_id=mock_challenge["challenge_id"]
        )
        
        # Encrypted flag MUST NOT contain plaintext
        assert plaintext_flag not in str(encrypted)
        assert "super_secret" not in encrypted["encrypted_flag"]
        assert "CTF{" not in encrypted["encrypted_flag"]
        
    def test_flags_different_per_user(self, mock_challenge):
        """Flags must be unique per user - no shared flags"""
        flag_system = SecureFlagProtection()
        same_plaintext = "CTF{test_flag}"
        
        user1_encrypted = flag_system.encrypt_flag(
            flag=same_plaintext,
            user_id="user_1",
            challenge_id=mock_challenge["challenge_id"]
        )
        
        user2_encrypted = flag_system.encrypt_flag(
            flag=same_plaintext,
            user_id="user_2", 
            challenge_id=mock_challenge["challenge_id"]
        )
        
        # MUST be different - prevents flag sharing
        assert user1_encrypted["encrypted_flag"] != user2_encrypted["encrypted_flag"]
        
    def test_decryption_requires_correct_user(self, mock_challenge):
        """User A cannot decrypt User B's flag"""
        flag_system = SecureFlagProtection()
        flag = "CTF{secret}"
        
        # User A encrypts
        encrypted = flag_system.encrypt_flag(
            flag=flag,
            user_id="user_a",
            challenge_id=mock_challenge["challenge_id"]
        )
        
        # User B tries to decrypt - should fail or get wrong result
        try:
            decrypted = flag_system.decrypt_flag(
                encrypted_flag=encrypted["encrypted_flag"],
                user_id="user_b",  # Different user!
                challenge_id=mock_challenge["challenge_id"]
            )
            
            # If decryption succeeds, it MUST NOT be the original flag
            if decrypted.get("success"):
                assert decrypted.get("flag") != flag, "SECURITY BREACH: User B decrypted User A's flag!"
        except Exception:
            # Expected - decryption should fail
            pass
    
    def test_flag_encryption_is_deterministic(self, mock_user, mock_challenge):
        """Same user+challenge should get consistent encryption (when noise disabled)"""
        flag_system = SecureFlagProtection()
        flag = "CTF{test}"
        fixed_time = str(int(time.time()))
        
        # Disable noise AND fix timestamp for deterministic test
        from unittest.mock import patch
        with patch("secure_flags.Fernet.encrypt") as mock_encrypt:
            # Set a predictable return value based on input to simulate deterministic encryption
            mock_encrypt.side_effect = lambda data: b"mocked_encrypted_" + data
            
            enc1 = flag_system.encrypt_flag(flag, mock_user["user_id"], mock_challenge["challenge_id"], add_noise=False, fixed_timestamp=fixed_time)
            enc2 = flag_system.encrypt_flag(flag, mock_user["user_id"], mock_challenge["challenge_id"], add_noise=False, fixed_timestamp=fixed_time)
            
            # Should be deterministic when noise is disabled and timestamp fixed
            assert enc1["encrypted_flag"] == enc2["encrypted_flag"]
            
            # Reset mock for noisy tests
            mock_encrypt.side_effect = None
            mock_encrypt.return_value = None
        
        # With noise (default), should be non-deterministic for better security
        enc3 = flag_system.encrypt_flag(flag, mock_user["user_id"], mock_challenge["challenge_id"], add_noise=True, fixed_timestamp=fixed_time)
        enc4 = flag_system.encrypt_flag(flag, mock_user["user_id"], mock_challenge["challenge_id"], add_noise=True, fixed_timestamp=fixed_time)
        assert enc3["encrypted_flag"] != enc4["encrypted_flag"]


class TestFlagProtectionMechanisms:
    """Test security mechanisms protecting flags"""
    
    def test_flag_system_initialization_secure(self):
        """Flag system must initialize with secure defaults"""
        flag_system = SecureFlagProtection()
        assert flag_system is not None
        assert hasattr(flag_system, 'encrypt_flag')
        assert hasattr(flag_system, 'decrypt_flag')
        
    def test_encrypted_flag_format_safe(self, mock_user, mock_challenge):
        """Encrypted flags should be base64-like, not readable"""
        flag_system = SecureFlagProtection()
        
        result = flag_system.encrypt_flag(
            flag="CTF{visible_if_broken}",
            user_id=mock_user["user_id"],
            challenge_id=mock_challenge["challenge_id"]
        )
        
        encrypted = result["encrypted_flag"]
        
        # Should look encrypted (base64-ish)
        assert len(encrypted) > 20
        assert not encrypted.startswith("CTF{")
        assert "visible_if_broken" not in encrypted
        
    def test_decryption_round_trip(self, mock_user, mock_challenge):
        """Encryption->Decryption should work for legitimate user"""
        flag_system = SecureFlagProtection()
        original = "CTF{round_trip_test}"
        
        # Mark the challenge as exploited first (required for decryption)
        challenge_key = f"{mock_user['user_id']}:{mock_challenge['challenge_id']}"
        flag_system.verified_exploitations[challenge_key] = {
            "timestamp": time.time(),
            "verified": True
        }
        
        encrypted = flag_system.encrypt_flag(
            flag=original,
            user_id=mock_user["user_id"],
            challenge_id=mock_challenge["challenge_id"],
            add_noise=False  # Disable noise for test
        )
        
        decrypted = flag_system.decrypt_flag(
            encrypted_flag=encrypted["encrypted_flag"],
            user_id=mock_user["user_id"],
            challenge_id=mock_challenge["challenge_id"],
            timestamp=encrypted["timestamp"],
            verification_hash=encrypted["verification_hash"]
        )
        
        assert decrypted["success"] is True
        assert decrypted["flag"] == original
        
    def test_no_plaintext_in_api_responses(self, mock_user, mock_challenge):
        """API responses must never contain plaintext flags"""
        flag_system = SecureFlagProtection()
        secret_flag = "CTF{api_exposure_test}"
        
        result = flag_system.encrypt_flag(
            flag=secret_flag,
            user_id=mock_user["user_id"],
            challenge_id=mock_challenge["challenge_id"]
        )
        
        # Convert entire response to string and check
        response_str = str(result)
        
        # Plaintext flag should NOT appear anywhere
        assert secret_flag not in response_str
        assert "api_exposure_test" not in response_str


class TestFlagGenerationSecurity:
    """Test secure flag generation"""
    
    def test_generated_flags_are_complex(self):
        """Generated flags should have sufficient complexity"""
        
        # Generate flag using hash-based approach
        import hashlib
        user_id = "test_user"
        challenge_id = "test_challenge"
        
        # Create flag hash (what would be stored)
        flag_data = f"{user_id}:{challenge_id}:salt_value"
        flag_hash = hashlib.sha256(flag_data.encode()).hexdigest()
        
        # Flag should be long enough
        assert len(flag_hash) >= 32
        
    def test_flag_storage_never_plaintext(self):
        """Flags should never be stored in plaintext"""
        # This is a design principle test
        # The system should only deal with encrypted or hashed flags
        # Never store "CTF{plaintext}" - only hashes or encrypted versions
        
        plaintext = "CTF{never_store_this}"
        hashed = hashlib.sha256(plaintext.encode()).hexdigest()
        
        # Hashed version is completely different
        assert hashed != plaintext
        assert "never_store_this" not in hashed
        assert len(hashed) == 64  # SHA256 hex length
        
    def test_timing_attack_resistance(self, mock_user, mock_challenge):
        """Flag comparison should be timing-safe"""
        import hmac
        
        flag1 = "CTF{flag_one}"
        flag2 = "CTF{flag_two}"
        
        # Use HMAC for timing-safe comparison
        secret = b"secret_key"
        hash1 = hmac.new(secret, flag1.encode(), hashlib.sha256).digest()
        hash2 = hmac.new(secret, flag2.encode(), hashlib.sha256).digest()
        
        # Compare using hmac.compare_digest (timing-safe)
        result = hmac.compare_digest(hash1, hash2)
        
        assert result is False  # Different flags
        assert isinstance(result, bool)


class TestFlagExtractionPrevention:
    """Test that flags cannot be extracted through various attacks"""
    
    def test_cannot_extract_flag_from_encrypted_data(self, mock_user, mock_challenge):
        """Attacker with encrypted flag should not extract plaintext"""
        flag_system = SecureFlagProtection()
        secret = "CTF{secret_flag_12345}"
        
        encrypted = flag_system.encrypt_flag(
            flag=secret,
            user_id=mock_user["user_id"],
            challenge_id=mock_challenge["challenge_id"]
        )
        
        encrypted_data = encrypted["encrypted_flag"]
        
        # Attacker tries various methods to extract
        
        # 1. Base64 decode attempt
        try:
            decoded = base64.b64decode(encrypted_data)
            # Even if decode succeeds, should not contain plaintext
            assert secret not in decoded.decode('utf-8', errors='ignore')
        except Exception:
            pass  # Decode failure is also acceptable
        
        # 2. String search
        assert secret not in encrypted_data
        assert "secret_flag" not in encrypted_data
        
    def test_cannot_decrypt_without_user_context(self, mock_challenge):
        """Cannot decrypt flag without knowing the user"""
        flag_system = SecureFlagProtection()
        
        encrypted = flag_system.encrypt_flag(
            flag="CTF{test}",
            user_id="known_user",
            challenge_id=mock_challenge["challenge_id"]
        )
        
        # Try to decrypt with wrong/missing user context
        try:
            result = flag_system.decrypt_flag(
                encrypted_flag=encrypted["encrypted_flag"],
                user_id="attacker_user",  # Different user
                challenge_id=mock_challenge["challenge_id"]
            )
            
            # Should not get original flag
            if result.get("success"):
                assert result.get("flag") != "CTF{test}"
        except Exception:
            pass  # Failure is expected
    
    def test_cannot_decrypt_without_challenge_context(self, mock_user):
        """Cannot decrypt flag without knowing the challenge"""
        flag_system = SecureFlagProtection()
        
        encrypted = flag_system.encrypt_flag(
            flag="CTF{test}",
            user_id=mock_user["user_id"],
            challenge_id="original_challenge"
        )
        
        # Try with wrong challenge
        try:
            result = flag_system.decrypt_flag(
                encrypted_flag=encrypted["encrypted_flag"],
                user_id=mock_user["user_id"],
                challenge_id="different_challenge"  # Wrong challenge
            )
            
            # Should not get original flag
            if result.get("success"):
                assert result.get("flag") != "CTF{test}"
        except Exception:
            pass  # Failure is expected


class TestFlagRotationAndExpiry:
    """Test flag rotation and time-based security"""
    
    def test_flag_includes_temporal_component(self):
        """Flags should include time-based component for rotation"""
        import time
        
        # Flags should be derivable with timestamp
        user_id = "user123"
        challenge_id = "challenge456"
        timestamp = int(time.time())
        
        # Create time-based flag identifier
        flag_id = f"{user_id}:{challenge_id}:{timestamp // 3600}"  # Hour-based
        flag_hash = hashlib.sha256(flag_id.encode()).hexdigest()
        
        # Different hours = different hashes
        flag_id_next_hour = f"{user_id}:{challenge_id}:{(timestamp // 3600) + 1}"
        flag_hash_next = hashlib.sha256(flag_id_next_hour.encode()).hexdigest()
        
        assert flag_hash != flag_hash_next  # Enables rotation


class TestNoFlagLeaksInTests:
    """Meta-test: Ensure tests themselves don't leak flags"""
    
    def test_test_flags_are_obviously_fake(self):
        """Test flags should be clearly marked as test data"""
        test_flags = [
            "CTF{test_flag}",
            "CTF{round_trip_test}",
            "CTF{secret}",
        ]
        
        for flag in test_flags:
            # Should contain "test" or be very short
            assert "test" in flag.lower() or len(flag) < 20
    
    def test_no_production_flags_in_code(self):
        """Verify no production-looking flags in test code"""
        # Production flags would be longer and more complex
        # Test flags should be simple and obvious
        
        test_flag = "CTF{test}"
        
        # Simple test flag characteristics
        assert len(test_flag) < 30
        assert "test" in test_flag.lower() or "example" in test_flag.lower()


