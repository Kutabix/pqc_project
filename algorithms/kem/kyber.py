import time
import numpy as np
from oqs import KeyEncapsulation


class KyberBenchmark:
    def __init__(self, variant="512"):
        self.variant = f"Kyber{variant}"

    def run_benchmark(self, iterations=100):
        kem = KeyEncapsulation(self.variant)
        metrics = {
            'keygen_times': [],
            'encap_times': [],
            'decap_times': [],
            'secret_key_sizes': [],  # Dodane do śledzenia rozmiarów secret key
            'public_key_sizes': [],
            'ciphertext_sizes': []
        }

        for _ in range(iterations):
            # Key generation
            start = time.perf_counter()
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()  # Pobierz secret key
            metrics['keygen_times'].append(time.perf_counter() - start)

            # Zapisz rozmiar secret key
            metrics['secret_key_sizes'].append(len(secret_key))

            # Encapsulation
            start = time.perf_counter()
            ciphertext, shared_secret = kem.encap_secret(public_key)
            metrics['encap_times'].append(time.perf_counter() - start)

            # Decapsulation
            start = time.perf_counter()
            _ = kem.decap_secret(ciphertext)
            metrics['decap_times'].append(time.perf_counter() - start)

            # Store sizes
            metrics['public_key_sizes'].append(len(public_key))
            metrics['ciphertext_sizes'].append(len(ciphertext))

        return {
            'variant': self.variant,
            'time_avg': {
                'keygen': np.mean(metrics['keygen_times']) * 1000,
                'encap': np.mean(metrics['encap_times']) * 1000,
                'decap': np.mean(metrics['decap_times']) * 1000
            },
            'size_avg': {
                'secret_key': np.mean(metrics['secret_key_sizes']),  # Dodane
                'public_key': np.mean(metrics['public_key_sizes']),
                'ciphertext': np.mean(metrics['ciphertext_sizes'])
            }
        }