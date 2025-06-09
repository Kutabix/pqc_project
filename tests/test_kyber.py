import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from algorithms.kem.kyber import KyberBenchmark
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.mark.parametrize("variant", ["512", "768", "1024"])
def test_kyber_benchmark_output(variant):
    benchmark = KyberBenchmark(variant=variant)
    result = benchmark.run_benchmark(iterations=5)

    assert "time_avg" in result
    assert "size_avg" in result
    for key in ['keygen', 'encap', 'decap']:
        assert result['time_avg'][key] > 0
    for key in ['secret_key', 'public_key', 'ciphertext']:
        assert result['size_avg'][key] > 0


def test_kyber_512_faster_than_1024():
    bench_512 = KyberBenchmark(variant="512")
    bench_1024 = KyberBenchmark(variant="1024")

    time_512 = bench_512.run_benchmark(iterations=3)["time_avg"]["encap"]
    time_1024 = bench_1024.run_benchmark(iterations=3)["time_avg"]["encap"]

    assert time_512 < time_1024

# test_kyber_tamper.py
from algorithms.kem.kyber import KyberBenchmark
