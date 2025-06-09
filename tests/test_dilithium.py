import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from algorithms.signature.dilithium import DilithiumBenchmark
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.mark.parametrize("variant", ["Dilithium2", "Dilithium3", "Dilithium5"])
def test_dilithium_benchmark_output(variant):
    benchmark = DilithiumBenchmark(variant=variant, message_length=128)
    results = benchmark.run_benchmark(iterations=3)

    assert len(results) == 1
    result = results[0]
    for key in ['keygen_time_ms', 'avg_sign_time_ms', 'avg_verify_time_ms']:
        assert result[key] > 0
    for key in ['public_key_size', 'private_key_size', 'signature_size', 'message_size']:
        assert result[key] > 0
