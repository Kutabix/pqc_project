from algorithms.signature.pdfSigner import PDFSigner


def run_complete_benchmark(pdf_path, algorithms, iterations):
    results = []

    for algo in algorithms:
        print(f"\nBenchmarking {algo}...")
        signer = PDFSigner(algo)

        key_data = signer.generate_keys()
        print(f"Key generation: {key_data['keygen_time_ms']:.2f} ms")

        sign_times = []
        for i in range(iterations):
            result = signer.sign_pdf(pdf_path)
            sign_times.append(result['sign_time_ms'])
            print(f"Signing #{i + 1}: {result['sign_time_ms']:.2f} ms")

            verify_result = signer.verify_pdf(
                pdf_path,
                result['signature'],
                key_data['public_key']
            )
            print(f"Verification: {verify_result['verify_time_ms']:.2f} ms")

            results.append({
                'algorithm': algo,
                'keygen_time_ms': key_data['keygen_time_ms'],
                'sign_time_ms': result['sign_time_ms'],
                'verify_time_ms': verify_result['verify_time_ms'],
                'signature_size': len(result['signature']),
                'public_key_size': len(key_data['public_key']),
                'secret_key_size': len(key_data['secret_key']),
                'file_size_mb': result['file_size_mb'],
                'iterations': iterations
            })

    return results

PDF_FILE = "large_document.pdf"
ALGORITHMS = [
    "Dilithium2",
    "Dilithium3",
    "Dilithium5",
    "Falcon-512",
    "Falcon-1024",
]