import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from algorithms.kem.bike import BikeBenchmark
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.mark.parametrize("variant", ["L1", "L3", "L5"])
def test_bike_benchmark_output(variant):
    benchmark = BikeBenchmark(variant=variant)
    result = benchmark.run_benchmark(iterations=5)

    assert "time_avg" in result
    assert "size_avg" in result
    for key in ['keygen', 'encap', 'decap']:
        assert result['time_avg'][key] > 0
    for key in ['secret_key', 'public_key', 'ciphertext']:
        assert result['size_avg'][key] > 0
