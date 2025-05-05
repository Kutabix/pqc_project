import hashlib
from oqs import Signature
import time
import json
import os
from pathlib import Path


class PDFSigner:
    CHUNK_SIZE = 4096

    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.signer = Signature(algorithm)

    def _calculate_hash(self, file_path):
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(self.CHUNK_SIZE):
                sha256.update(chunk)
        return sha256.digest()

    def generate_keys(self):
        start = time.perf_counter()
        self.public_key = self.signer.generate_keypair()
        self.secret_key = self.signer.export_secret_key()
        return {
            'public_key': self.public_key,
            'secret_key': self.secret_key,
            'keygen_time_ms': (time.perf_counter() - start) * 1000
        }

    def sign_pdf(self, pdf_path):
        file_hash = self._calculate_hash(pdf_path)

        start = time.perf_counter()
        signature = self.signer.sign(file_hash)
        print(len(signature))
        return {
            'signature': signature,
            'sign_time_ms': (time.perf_counter() - start) * 1000,
            'file_size_mb': os.path.getsize(pdf_path) / (1024 ** 2)
        }

    def verify_pdf(self, pdf_path, signature, public_key):
        file_hash = self._calculate_hash(pdf_path)

        start = time.perf_counter()
        is_valid = self.signer.verify(file_hash, signature, public_key)
        return {
            'is_valid': is_valid,
            'verify_time_ms': (time.perf_counter() - start) * 1000
        }

    def save_signature(self, signature, output_path):
        with open(output_path, 'wb') as f:
            f.write(signature)

    def load_signature(self, signature_path):
        with open(signature_path, 'rb') as f:
            return f.read()