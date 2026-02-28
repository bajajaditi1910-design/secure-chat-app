from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.backends import default_backend

def generate_dh_keys():
    parameters = dh.generate_parameters(generator=2, key_size=2048)
    private_key = parameters.generate_private_key()
    return private_key, private_key.public_key()

def derive_shared_key(private_key, peer_public_key):
    shared_secret = private_key.exchange(peer_public_key)
    digest = hashes.Hash(hashes.SHA256())
    digest.update(shared_secret)
    return digest.finalize()

def generate_hmac(key, data):
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(data)
    return h.finalize()

def verify_hmac(key, data, tag):
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(data)
    h.verify(tag)