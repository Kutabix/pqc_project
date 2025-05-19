from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import json
import os
from pathlib import Path

import pandas as pd
import seaborn as sns

#algorytmy signature
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

def plot_operation_times_kyber(figsize=(12, 5)):
    base_dir = "results/kem"
    ensure_dir(base_dir)

    json_path = os.path.join(base_dir, "kem_results.json")
    with open(json_path) as f:
        results = json.load(f)

    # Filtrujemy tylko Kyber
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
        ax.bar(x + offset, measurement, width, label=name)
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
        ax.bar(x + offset, measurement, width, label=name)
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
        ax.bar(x + offset, measurement, width, label=name)
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

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f} ms',
                ha='center', va='bottom')

    ax.set_ylabel('Total Time (ms)')
    ax.set_title('Total Execution Time Comparison for Kyber Variants')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    return fig

def generate_keygen_plot(results):
    base_dir = "results/sig"
    ensure_dir(base_dir)
    df = pd.DataFrame(results)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=df,
        x='algorithm',
        y='keygen_time_ms',
        hue='algorithm',
        palette="rocket",
        estimator=np.mean,
        errorbar=('ci', 95),
        ax=ax
    )

    ax.set_title("Czas generowania par kluczy\n(dla różnych algorytmów)")
    ax.set_xlabel("Algorytm")
    ax.set_ylabel("Czas [ms]")
    plt.setp(ax.get_xticklabels(), rotation=45)

    for i, row in df.groupby('algorithm').mean().iterrows():
        ax.text(
            x=df['algorithm'].unique().tolist().index(i),
            y=row['keygen_time_ms'] + 0.5,
            s=f"{row['keygen_time_ms']:.1f} ms",
            ha='center'
        )

    plt.tight_layout()

    return fig
