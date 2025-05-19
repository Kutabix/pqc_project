import matplotlib.pyplot as plt
import numpy as np
import json
import os
from pathlib import Path

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def plot_operation_times_kyber(figsize=(12, 5)):
    base_dir = "results/kem"
    ensure_dir(base_dir)

    json_path = os.path.join(base_dir, "kem_results.json")
    with open(json_path) as f:
        results = json.load(f)

    kyber_results = [r for r in results if 'Kyber' in r['variant']]
    variants = [r['variant'] for r in kyber_results]

    times = {
        'Key Generation': [r['time_avg']['keygen'] for r in kyber_results],
        'Encapsulation': [r['time_avg']['encap'] for r in kyber_results],
        'Decapsulation': [r['time_avg']['decap'] for r in kyber_results]
    }

    fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(len(variants))
    width = 0.2
    multiplier = 0

    for name, measurement in times.items():
        offset = width * multiplier
        bars = ax.bar(x + offset, measurement, width, label=name)
        for bar, val in zip(bars, measurement):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{val:.2f} ms", ha='center', va='bottom', fontsize=9)
        multiplier += 1

    ax.set_ylabel('Time (ms)')
    ax.set_title('Kyber Operation Times')
    ax.set_xticks(x + width, variants)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    return fig


def plot_operation_times_bike(figsize=(12, 5)):
    base_dir = "results/kem"
    ensure_dir(base_dir)

    json_path = os.path.join(base_dir, "kem_results.json")
    with open(json_path) as f:
        results = json.load(f)

    # Filtrujemy tylko BIKE
    bike_results = [r for r in results if 'BIKE' in r['variant'].upper()]
    variants = [r['variant'] for r in bike_results]

    times = {
        'Key Generation': [r['time_avg']['keygen'] for r in bike_results],
        'Encapsulation': [r['time_avg']['encap'] for r in bike_results],
        'Decapsulation': [r['time_avg']['decap'] for r in bike_results]
    }

    fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(len(variants))
    width = 0.2
    multiplier = 0

    for name, measurement in times.items():
        offset = width * multiplier
        bars = ax.bar(x + offset, measurement, width, label=name)
        # Dodajemy wartości nad słupkami
        for bar, val in zip(bars, measurement):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{val:.2f} ms", ha='center', va='bottom', fontsize=9)
        multiplier += 1

    ax.set_ylabel('Time (ms)')
    ax.set_title('BIKE Operation Times')
    ax.set_xticks(x + width, variants)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    return fig


def plot_key_sizes(figsize=(12, 5)):
    base_dir = "results/kem"
    ensure_dir(base_dir)

    json_path = os.path.join(base_dir, "kem_results.json")
    with open(json_path) as f:
        results = json.load(f)

    variants = [r['variant'] for r in results]

    sizes = {
        'Public Key': [r['size_avg']['public_key'] for r in results],
        'Ciphertext': [r['size_avg']['ciphertext'] for r in results],
        'Secret Key': [r['size_avg']['secret_key'] for r in results]
    }

    fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(len(variants))
    width = 0.2
    multiplier = 0

    for name, measurement in sizes.items():
        offset = width * multiplier
        bars = ax.bar(x + offset, measurement, width, label=name)
        # Dodajemy wartości nad słupkami (bez ms, bo to bajty)
        for bar, val in zip(bars, measurement):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{int(val)}", ha='center', va='bottom', fontsize=9)
        multiplier += 1

    ax.set_ylabel('Size (bytes)')
    ax.set_title('Key and Ciphertext Sizes')
    ax.set_xticks(x + width, variants)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    return fig


def plot_total_time_comparison(figsize=(12, 5)):
    base_dir = "results/kem"
    ensure_dir(base_dir)

    json_path = os.path.join(base_dir, "kem_results.json")
    with open(json_path) as f:
        results = json.load(f)

    variants = [r['variant'] for r in results]
    total_times = [r['time_avg']['keygen'] + r['time_avg']['encap'] + r['time_avg']['decap'] for r in results]

    fig, ax = plt.subplots(figsize=figsize)

    bars = ax.bar(variants, total_times, color=['#1f77b4', '#ff7f0e', '#2ca02c'])

    for bar, val in zip(bars, total_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{val:.2f} ms',
                ha='center', va='bottom', fontsize=9)

    ax.set_ylabel('Total Time (ms)')
    ax.set_title('Total Execution Time Comparison for Kyber Variants')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    return fig



# signature algorithms

def plot_key_sizes_signature(results, message_size):
    algorithms = [r['algorithm'] for r in results]
    public_keys = [r['public_key_size'] for r in results]
    private_keys = [r['private_key_size'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars_pub = ax.bar(algorithms, public_keys, label="Public Key", color='blue')
    bars_priv = ax.bar(algorithms, private_keys, label="Private Key", alpha=0.7, color='green')
    ax.set_title(f"Rozmiary kluczy (wiadomość: {message_size} bajtów)")
    ax.set_xlabel("Algorytm")
    ax.set_ylabel("Rozmiar (bajty)")
    ax.legend()

    for bar in bars_pub:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{int(height)}", ha='center', va='bottom', fontsize=9)
    for bar in bars_priv:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{int(height)}", ha='center', va='bottom', fontsize=9)

    return fig


def plot_signature_sizes(results, message_size):
    algorithms = [r['algorithm'] for r in results]
    signatures = [r['signature_size'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(algorithms, signatures, color="purple")
    ax.set_title(f"Rozmiary podpisów (wiadomość: {message_size} bajtów)")
    ax.set_xlabel("Algorytm")
    ax.set_ylabel("Rozmiar (bajty)")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{int(height)}", ha='center', va='bottom', fontsize=9)

    return fig


def plot_keygen_times(results, message_size):
    algorithms = [r['algorithm'] for r in results]
    keygen_times = [r['keygen_time_ms'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(algorithms, keygen_times, color="orange")
    ax.set_title(f"Czasy generowania kluczy (wiadomość: {message_size} bajtów)")
    ax.set_xlabel("Algorytm")
    ax.set_ylabel("Czas (ms)")

    for bar, time in zip(bars, keygen_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{time:.2f} ms", ha='center', va='bottom', fontsize=9)

    return fig


def plot_sign_times(results, message_size):
    algorithms = [r['algorithm'] for r in results]
    sign_times = [r['avg_sign_time_ms'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(algorithms, sign_times, color="red")
    ax.set_title(f"Czasy podpisu (wiadomość: {message_size} bajtów)")
    ax.set_xlabel("Algorytm")
    ax.set_ylabel("Czas (ms)")

    for bar, time in zip(bars, sign_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{time:.2f} ms", ha='center', va='bottom', fontsize=9)

    return fig


def plot_verify_times(results, message_size):
    algorithms = [r['algorithm'] for r in results]
    verify_times = [r['avg_verify_time_ms'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(algorithms, verify_times, color="cyan")
    ax.set_title(f"Czasy weryfikacji (wiadomość: {message_size} bajtów)")
    ax.set_xlabel("Algorytm")
    ax.set_ylabel("Czas (ms)")

    for bar, time in zip(bars, verify_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{time:.2f} ms", ha='center', va='bottom', fontsize=9)

    return fig


def plot_total_times(results, message_size):
    algorithms = [r['algorithm'] for r in results]
    total_times = [r['keygen_time_ms'] + r['avg_sign_time_ms'] + r['avg_verify_time_ms'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(algorithms, total_times, color="magenta")
    ax.set_title(f"Czas całkowity (wiadomość: {message_size} bajtów)")
    ax.set_xlabel("Algorytm")
    ax.set_ylabel("Czas (ms)")

    for bar, time in zip(bars, total_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + height*0.01, f"{time:.2f} ms", ha='center', va='bottom', fontsize=9)

    return fig
