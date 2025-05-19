import hashlib

import oqs
from oqs import Signature
import time
import json
import os
from pathlib import Path



import oqs
import time
import random
import string


class SignatureBenchmark:
    def __init__(self, algorithm_name, message=None):
        self.algorithm_name = algorithm_name
        if message is None:
            self.message = self.generate_random_message(1024)
        else:
            if isinstance(message, str):
                message = message.encode()
            self.message = message

    def generate_random_message(self, length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).encode()

    def run_benchmark(self, iterations=10):
        results = []
        print(self.message)
        with oqs.Signature(self.algorithm_name) as signer:
            start_time = time.time()
            public_key = signer.generate_keypair()  # public_key to to, co zwraca generate_keypair()
            keygen_time = (time.time() - start_time) * 1000  # ms

            private_key = signer.export_secret_key()

            sign_times = []
            signatures = []
            for _ in range(iterations):
                start = time.time()
                signature = signer.sign(self.message)
                sign_times.append((time.time() - start) * 1000)
                signatures.append(signature)
            avg_sign_time = sum(sign_times) / iterations

            verify_times = []
            for signature in signatures:
                start = time.time()
                valid = signer.verify(self.message, signature, public_key)
                verify_times.append((time.time() - start) * 1000)
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
    def __init__(self, variant="Dilithium2", message_length=1024):
        super().__init__(variant, message_length)


class FalconBenchmark(SignatureBenchmark):
    def __init__(self, variant="Falcon-512", message_length=1024):
        super().__init__(variant, message_length)
