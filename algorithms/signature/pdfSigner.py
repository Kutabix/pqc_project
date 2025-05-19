# import hashlib
# from oqs import Signature
# import time
# import json
# import os
# from pathlib import Path
#
#
# class PDFSigner:
#     CHUNK_SIZE = 4096
#
#     def __init__(self, algorithm):
#         self.algorithm = algorithm
#         self.signer = Signature(algorithm)
#
#     def _calculate_hash(self, file_path):
#         sha256 = hashlib.sha256()
#         with open(file_path, 'rb') as f:
#             while chunk := f.read(self.CHUNK_SIZE):
#                 sha256.update(chunk)
#         return sha256.digest()
#
#     def generate_keys(self):
#         start = time.perf_counter()
#         self.public_key = self.signer.generate_keypair()
#         self.secret_key = self.signer.export_secret_key()
#         return {
#             'public_key': self.public_key,
#             'secret_key': self.secret_key,
#             'keygen_time_ms': (time.perf_counter() - start) * 1000
#         }
#
#     def sign_pdf(self, pdf_path):
#         file_hash = self._calculate_hash(pdf_path)
#
#         start = time.perf_counter()
#         signature = self.signer.sign(file_hash)
#         return {
#             'signature': signature,
#             'sign_time_ms': (time.perf_counter() - start) * 1000,
#             'file_size_mb': os.path.getsize(pdf_path) / (1024 ** 2)
#         }
#
#     def verify_pdf(self, pdf_path, signature, public_key):
#         file_hash = self._calculate_hash(pdf_path)
#
#         start = time.perf_counter()
#         is_valid = self.signer.verify(file_hash, signature, public_key)
#         return {
#             'is_valid': is_valid,
#             'verify_time_ms': (time.perf_counter() - start) * 1000
#         }
#
#     def save_signature(self, signature, output_path):
#         with open(output_path, 'wb') as f:
#             f.write(signature)
#
#     def load_signature(self, signature_path):
#         with open(signature_path, 'rb') as f:
#             return f.read()

import oqs
import time
import random
import string
from pathlib import Path


class SignatureBenchmark:
    def __init__(self, algorithm_name, message_length=1024, message=None, file_path=None):
        self.algorithm_name = algorithm_name
        if message:
            self.message = message.encode()
        elif file_path:
            self.message = self.load_file(file_path)
        else:
            self.message = self.generate_random_message(message_length)

    def generate_random_message(self, length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).encode()

    def load_file(self, file_path):
        with open(file_path, 'rb') as f:
            return f.read()

    def run_benchmark(self, iterations=10):
        results = []
        with oqs.Signature(self.algorithm_name) as signer:
            # Generate keypair
            start_time = time.time()
            public_key, private_key = signer.generate_keypair()
            keygen_time = (time.time() - start_time) * 1000  # ms

            # Benchmark signing
            sign_times = []
            signatures = []
            for _ in range(iterations):
                start_time = time.time()
                signature = signer.sign(self.message, private_key)
                sign_times.append((time.time() - start_time) * 1000)
                signatures.append(signature)
            avg_sign_time = sum(sign_times) / iterations

            # Benchmark verification
            verify_times = []
            for signature in signatures:
                start_time = time.time()
                signer.verify(self.message, signature, public_key)
                verify_times.append((time.time() - start_time) * 1000)
            avg_verify_time = sum(verify_times) / iterations

            results.append({
                'algorithm': self.algorithm_name,
                'keygen_time_ms': keygen_time,
                'avg_sign_time_ms': avg_sign_time,
                'avg_verify_time_ms': avg_verify_time,
                'public_key_size': len(public_key),
                'private_key_size': len(private_key),
                'signature_size': len(signatures[0]),
                'message_size': len(self.message)
            })

        return results


class DilithiumBenchmark(SignatureBenchmark):
    def __init__(self, variant="Dilithium2", message=None, file_path=None, message_length=1024):
        super().__init__(variant, message_length, message, file_path)


class FalconBenchmark(SignatureBenchmark):
    def __init__(self, variant="Falcon-512", message=None, file_path=None, message_length=1024):
        super().__init__(variant, message_length, message, file_path)
