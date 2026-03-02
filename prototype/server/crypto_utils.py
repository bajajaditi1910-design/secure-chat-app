#!/usr/bin/env python3
"""
Cryptography Utilities for SecureChat
Implements Diffie-Hellman, AES-128, and HMAC
"""

import os
import hmac
import hashlib
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class CryptoManager:
    """Manages encryption/decryption for a client"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.peer_public_key = None
        self.shared_secret = None
        self.aes_key = None
        self.hmac_key = None
        
        # Fixed DH parameters (same as original implementation)
        self.p = int(
            "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
            "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
            "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
            "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
            "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
            "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
            "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
            "670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF",
            16
        )
        self.g = 2
    
    def generate_keys(self):
        """Generate DH key pair"""
        parameters = dh.DHParameterNumbers(self.p, self.g).parameters(default_backend())
        self.private_key = parameters.generate_private_key()
        self.public_key = self.private_key.public_key()
        print("[CRYPTO] Key pair generated")
    
    def get_public_key_pem(self):
        """Get public key in PEM format"""
        if not self.public_key:
            raise ValueError("No public key available")
        
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_bytes.decode('utf-8')
    
    def set_peer_public_key(self, peer_public_key_pem):
        """Set peer's public key from PEM"""
        peer_public_bytes = peer_public_key_pem.encode('utf-8')
        self.peer_public_key = serialization.load_pem_public_key(
            peer_public_bytes,
            backend=default_backend()
        )
        print("[CRYPTO] Peer public key received")
    
    def compute_shared_secret(self):
        """Compute shared secret and derive keys"""
        if not self.private_key or not self.peer_public_key:
            raise ValueError("Keys not available for shared secret computation")
        
        # Compute shared secret
        shared_secret_bytes = self.private_key.exchange(self.peer_public_key)
        
        # Derive master key using SHA-256
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(shared_secret_bytes)
        master_key = digest.finalize()
        
        # Split into AES and HMAC keys
        self.aes_key = master_key[:16]   # First 16 bytes for AES-128
        self.hmac_key = master_key[16:]  # Remaining 16 bytes for HMAC
        
        self.shared_secret = shared_secret_bytes.hex()
        
        print("[CRYPTO] Shared secret computed")
        print("[CRYPTO] AES key derived")
        print("[CRYPTO] HMAC key derived")
        
        return self.shared_secret
    
    def encrypt_message(self, plaintext):
        """Encrypt message with AES-128-CBC and add HMAC"""
        if not self.aes_key or not self.hmac_key:
            raise ValueError("Encryption keys not available")
        
        # Generate random IV
        iv = os.urandom(16)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Add PKCS7 padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        
        # Encrypt
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Generate HMAC
        mac = hmac.new(
            self.hmac_key,
            iv + ciphertext,
            digestmod=hashlib.sha256
        ).digest()
        
        # Return: IV + Ciphertext + HMAC
        return iv + ciphertext + mac
    
    def decrypt_message(self, encrypted_data):
        """Decrypt message and verify HMAC"""
        if not self.aes_key or not self.hmac_key:
            raise ValueError("Decryption keys not available")
        
        # Split the data
        iv = encrypted_data[:16]
        mac_received = encrypted_data[-32:]
        ciphertext = encrypted_data[16:-32]
        
        # Verify HMAC
        mac_calculated = hmac.new(
            self.hmac_key,
            iv + ciphertext,
            digestmod=hashlib.sha256
        ).digest()
        
        if not hmac.compare_digest(mac_received, mac_calculated):
            raise ValueError("HMAC verification failed - Message integrity compromised!")
        
        # Decrypt
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        
        return plaintext.decode('utf-8')


# Standalone test
if __name__ == "__main__":
    print("=" * 50)
    print("Testing CryptoManager")
    print("=" * 50)
    
    # Create two crypto managers (simulating two clients)
    alice = CryptoManager()
    bob = CryptoManager()
    
    # Generate keys
    print("\n1. Generating keys...")
    alice.generate_keys()
    bob.generate_keys()
    
    # Exchange public keys
    print("\n2. Exchanging public keys...")
    alice_pub = alice.get_public_key_pem()
    bob_pub = bob.get_public_key_pem()
    
    alice.set_peer_public_key(bob_pub)
    bob.set_peer_public_key(alice_pub)
    
    # Compute shared secrets
    print("\n3. Computing shared secrets...")
    alice_secret = alice.compute_shared_secret()
    bob_secret = bob.compute_shared_secret()
    
    print(f"\nAlice's secret: {alice_secret[:32]}...")
    print(f"Bob's secret:   {bob_secret[:32]}...")
    print(f"Secrets match:  {alice_secret == bob_secret}")
    
    # Test encryption/decryption
    print("\n4. Testing encryption...")
    message = "Hello, this is a secure message!"
    print(f"Original: {message}")
    
    encrypted = alice.encrypt_message(message)
    print(f"Encrypted: {encrypted.hex()[:64]}...")
    
    decrypted = bob.decrypt_message(encrypted)
    print(f"Decrypted: {decrypted}")
    
    print(f"\nSuccess: {message == decrypted}")
    print("\n" + "=" * 50)
