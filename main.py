# from algorithms.kem.kyber import KyberBenchmark
# import json
# import csv
# import os
# from pathlib import Path
# import pandas as pd
#
# from benchmarks.sig_bench import run_complete_benchmark, PDF_FILE, ALGORITHMS
# from visualization import generate_advanced_plots, generate_keygen_plot
#
#
#
# def ensure_dir(path):
#     Path(path).mkdir(parents=True, exist_ok=True)
#
#
# def run_benchmarks():
#     variants = ["512", "768", "1024"]
#     results = []
#
#     for variant in variants:
#         benchmark = KyberBenchmark(variant)
#         results.append(benchmark.run_benchmark(iterations=10))
#
#     return results
#
#
# def save_results(results):
#     base_dir = "results/kem"
#     ensure_dir(base_dir)
#
#     json_path = os.path.join(base_dir,   "kyber_results.json")
#     with open(json_path, 'w') as f:
#         json.dump(results, f, indent=2)
#
#     csv_path = os.path.join(base_dir, "kyber_results.csv")
#     with open(csv_path, 'w', newline='') as csvfile:
#         fieldnames = ['variant', 'keygen_time', 'encap_time', 'decap_time',
#                       'public_key_size', 'ciphertext_size']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#
#         writer.writeheader()
#         for result in results:
#             writer.writerow({
#                 'variant': result['variant'],
#                 'keygen_time': result['time_avg']['keygen'],
#                 'encap_time': result['time_avg']['encap'],
#                 'decap_time': result['time_avg']['decap'],
#                 'public_key_size': result['size_avg']['public_key'],
#                 'ciphertext_size': result['size_avg']['ciphertext']
#             })
#
#     print(f"Results saved to {base_dir}")
#
#
# if __name__ == "__main__":
#     results = run_benchmarks()
#     save_results(results)
#
#
#
#     results = run_complete_benchmark(PDF_FILE, ALGORITHMS, iterations=300)
#
#     generate_keygen_plot(results)
#     generate_advanced_plots(results)
#
#     base_dir = "results/sig"
#     ensure_dir(base_dir)
#
#     csv_path = os.path.join(base_dir, "signature_results.csv")
#
#     df = pd.DataFrame(results)
#     df.to_csv(csv_path, index=False)
