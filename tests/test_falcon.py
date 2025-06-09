import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import oqs

import pytest
from algorithms.signature.falcon import FalconBenchmark

@pytest.mark.parametrize("variant", ["Falcon-512", "Falcon-1024"])
def test_falcon_benchmark_output(variant):
    benchmark = FalconBenchmark(variant=variant, message_length=128)
    results = benchmark.run_benchmark(iterations=3)

    assert len(results) == 1
    result = results[0]
    for key in ['keygen_time_ms', 'avg_sign_time_ms', 'avg_verify_time_ms']:
        assert result[key] > 0
    for key in ['public_key_size', 'private_key_size', 'signature_size', 'message_size']:
        assert result[key] > 0


def test_falcon_signing_time_limit():
    benchmark = FalconBenchmark(variant="Falcon-512", message_length=64)

    msg = b"performance test"
    with oqs.Signature(benchmark.algorithm_name) as signer:
        public_key = signer.generate_keypair()
        secret_key = signer.export_secret_key()

        start = time.time()
        signature = signer.sign(msg)
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 100


def test_falcon_tampered_signature_fails():
    algorithm_name = "Falcon-512"
    msg = b"secure message"

    with oqs.Signature(algorithm_name) as signer:
        public_key = signer.generate_keypair()
        secret_key = signer.export_secret_key()
        signature = signer.sign(msg)

        tampered_sig = bytearray(signature)
        tampered_sig[0] ^= 0xFF

        assert not signer.verify(msg, bytes(tampered_sig), public_key)