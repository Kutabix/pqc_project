from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import json
import os
from pathlib import Path

import pandas as pd
import seaborn as sns


def generate_advanced_plots(results):
    base_dir = "results/sig"
    os.makedirs(base_dir, exist_ok=True)

    df = pd.DataFrame(results)

    grouped = df.groupby('algorithm').mean().reset_index()

    plot_config = [
        ("sign_time_ms", "Czas podpisywania [ms]"),
        ("verify_time_ms", "Czas weryfikacji [ms]"),
        ("signature_size", "Rozmiar podpisu [B]"),
        ("public_key_size", "Rozmiar klucza publicznego [B]"),
        ("secret_key_size", "Rozmiar klucza prywatnego [B]")
    ]

    for metric, title in plot_config:
        plt.figure(figsize=(10, 6))
        sns.barplot(x="algorithm", y=metric, hue="algorithm", data=grouped, palette="Set2")
        plt.title(title)
        plt.ylabel(title)
        plt.xlabel("Algorytm")
        plt.xticks(rotation=45)
        plt.tight_layout()
        output_path = os.path.join(base_dir, f"{metric}.png")
        plt.savefig(output_path)
        plt.close()

    print("Wykresy zostały zapisane w folderze:", base_dir)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def plot_results():
    base_dir = "results/kem"
    ensure_dir(base_dir)

    json_path = os.path.join(base_dir, "kyber_results.json")
    with open(json_path) as f:
        results = json.load(f)

    variants = [r['variant'] for r in results]

    times = {
        'Key Generation': [r['time_avg']['keygen'] for r in results],
        'Encapsulation': [r['time_avg']['encap'] for r in results],
        'Decapsulation': [r['time_avg']['decap'] for r in results]
    }

    sizes = {
        'Public Key': [r['size_avg']['public_key'] for r in results],
        'Ciphertext': [r['size_avg']['ciphertext'] for r in results],
        'Secret Key': [r['size_avg']['secret_key'] for r in results]
    }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    x = np.arange(len(variants))
    width = 0.25
    multiplier = 0

    for name, measurement in times.items():
        offset = width * multiplier
        rects = ax1.bar(x + offset, measurement, width, label=name)
        multiplier += 1

    ax1.set_ylabel('Time (ms)')
    ax1.set_title('Operation Times')
    ax1.set_xticks(x + width, variants)
    ax1.legend()

    multiplier = 0
    for name, measurement in sizes.items():
        offset = width * multiplier
        rects = ax2.bar(x + offset, measurement, width, label=name)
        multiplier += 1

    ax2.set_ylabel('Size (bytes)')
    ax2.set_title('Key and Ciphertext Sizes')
    ax2.set_xticks(x + width, variants)
    ax2.legend()

    plt.tight_layout()

    plot_path = os.path.join(base_dir, "kyber_benchmark.png")
    plt.savefig(plot_path)
    plt.close()
    print(f"Plot saved to {plot_path}")



def plot_total_time_comparison():
    base_dir = "results/kem"
    ensure_dir(base_dir)

    json_path = os.path.join(base_dir, "kyber_results.json")
    with open(json_path) as f:
        results = json.load(f)

    variants = [r['variant'] for r in results]
    total_times = [r['time_avg']['keygen'] + r['time_avg']['encap'] + r['time_avg']['decap'] for r in results]

    plt.figure(figsize=(10, 6))

    bars = plt.bar(variants, total_times, color=['#1f77b4', '#ff7f0e', '#2ca02c'])

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f} ms',
                ha='center', va='bottom')

    plt.ylabel('Total Time (ms)')
    plt.title('Total Execution Time Comparison for Kyber Variants')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plot_path = os.path.join(base_dir, "kyber_total_time_comparison.png")
    plt.savefig(plot_path)
    plt.close()
    print(f"Total time comparison plot saved to {plot_path}")


def generate_keygen_plot(results):
    base_dir = "results/sig"
    ensure_dir(base_dir)
    df = pd.DataFrame(results)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df,
        x='algorithm',
        y='keygen_time_ms',
        hue='algorithm',
        palette="rocket",
        estimator=np.mean,
        errorbar=('ci', 95)
    )

    plt.title("Czas generowania par kluczy\n(dla różnych algorytmów)")
    plt.xlabel("Algorytm")
    plt.ylabel("Czas [ms]")
    plt.xticks(rotation=45)

    for i, row in df.groupby('algorithm').mean().iterrows():
        plt.text(
            x=df['algorithm'].unique().tolist().index(i),
            y=row['keygen_time_ms'] + 0.5,
            s=f"{row['keygen_time_ms']:.1f} ms",
            ha='center'
        )

    plot_path = os.path.join(base_dir, 'keygen_benchmark.png')
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Wykres czasów generowania kluczy zapisano w: {plot_path}")

if __name__ == "__main__":
    plot_results()
    plot_total_time_comparison()