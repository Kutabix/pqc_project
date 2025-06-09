import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithms.kem.kyber import KyberBenchmark
from algorithms.kem.bike import BikeBenchmark
from visualization import plot_key_sizes, plot_total_time_comparison, plot_operation_times_bike, plot_operation_times_kyber

class KemWindow:
    KEM_VARIANTS = [
        "Kyber512",
        "Kyber768",
        "Kyber1024",
        "BIKE-L1",
        "BIKE-L3",
        "BIKE-L5"
    ]

    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("KEM Benchmark")
        self.window.geometry("600x700")
        self.window.resizable(False, False)

        tk.Label(self.window, text="Liczba iteracji:").pack(pady=10)
        self.iter_entry = tk.Entry(self.window)
        self.iter_entry.insert(0, "10")
        self.iter_entry.pack(pady=5)

        self.check_vars = {}
        frame = tk.Frame(self.window)
        frame.pack(pady=5)
        for variant in self.KEM_VARIANTS:
            var = tk.IntVar(value=1)
            cb = tk.Checkbutton(frame, text=variant, variable=var)
            cb.pack(side=tk.LEFT, padx=5)
            self.check_vars[variant] = var

        self.run_button = tk.Button(self.window, text="Uruchom benchmark Kyber, BIKE", command=self.run_benchmarks)
        self.run_button.pack(pady=10)

        self.output = tk.Text(self.window, height=20, width=80)
        self.output.pack(pady=10)
        self.output.config(state=tk.DISABLED)

        tk.Button(self.window, text="Pokaż wykresy", command=self.show_all_plots).pack(pady=10)
        tk.Button(self.window, text="Pokaż tabelę wyników", command=self.show_results_table).pack(pady=10)

    def append_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)
        self.window.update()

    def clear_output(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete('1.0', tk.END)
        self.output.config(state=tk.DISABLED)

    def run_benchmarks(self):
        self.clear_output()

        try:
            iterations = int(self.iter_entry.get())
        except ValueError:
            messagebox.showerror("Błąd", "Niepoprawna liczba iteracji")
            return

        selected_variants = [variant for variant, var in self.check_vars.items() if var.get() == 1]

        if not selected_variants:
            messagebox.showerror("Błąd", "Wybierz przynajmniej jeden algorytm!")
            return

        kem_variants = {
            "Kyber512": KyberBenchmark("512"),
            "Kyber768": KyberBenchmark("768"),
            "Kyber1024": KyberBenchmark("1024"),
            "BIKE-L1": BikeBenchmark("L1"),
            "BIKE-L3": BikeBenchmark("L3"),
            "BIKE-L5": BikeBenchmark("L5")
        }

        all_results = []
        self.append_output("Start benchmarku KEM...\n")

        for name in selected_variants:
            benchmark = kem_variants[name]
            result = benchmark.run_benchmark(iterations=iterations)
            all_results.append(result)

            self.append_output(f"Algorytm: {result['variant']}\n")
            self.append_output(f" - Czas generowania klucza: {result['time_avg']['keygen']:.2f} ms\n")
            self.append_output(f" - Średni czas enkapsulacji: {result['time_avg']['encap']:.2f} ms\n")
            self.append_output(f" - Średni czas dekapsulacji: {result['time_avg']['decap']:.2f} ms\n")
            self.append_output(f" - Rozmiar klucza publicznego: {result['size_avg']['public_key']} bajtów\n")
            self.append_output(f" - Rozmiar klucza prywatnego: {result['size_avg']['secret_key']} bajtów\n")
            self.append_output(f" - Rozmiar szyfrogramu: {result['size_avg']['ciphertext']} bajtów\n")
            self.append_output(f" - Liczba iteracji: {iterations}\n\n")

        self.save_results(all_results)

    def save_results(self, results):
        base_dir = "results/kem"
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        json_path = os.path.join(base_dir, "kem_results.json")
        with open(json_path, "w") as f:
            json.dump(results, f, indent=2)

    def show_all_plots(self):
        figs = [
            plot_operation_times_kyber(),
            plot_operation_times_bike(),
            plot_key_sizes(),
            plot_total_time_comparison()
        ]

        titles = ["Operation Times Kyber", "Operation Times Bike", "Key Sizes", "Total Time Comparison"]

        for fig, title in zip(figs, titles):
            fig.set_size_inches(8, 5)
            fig.tight_layout(pad=2.0)

            plot_window = tk.Toplevel(self.window)
            plot_window.title(title)
            plot_window.geometry("900x600")

            frame = tk.Frame(plot_window, padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            w = canvas.get_tk_widget()
            w.pack(padx=10, pady=10)

            plot_window.grab_set()
            plot_window.wait_window(plot_window)

    def show_results_table(self):
        base_dir = "results/kem"
        json_path = os.path.join(base_dir, "kem_results.json")
        if not os.path.exists(json_path):
            messagebox.showerror("Błąd", "Plik wyników nie istnieje!")
            return

        with open(json_path) as f:
            results = json.load(f)

        table_window = tk.Toplevel(self.window)
        table_window.title("Tabela wyników benchmarku KEM")
        table_window.geometry("900x300")

        frame = tk.Frame(table_window, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ['variant', 'keygen_time', 'encap_time', 'decap_time', 'public_key_size', 'ciphertext_size', 'secret_key_size']
        tree = ttk.Treeview(frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').capitalize())
            tree.column(col, width=120, anchor='center')

        for result in results:
            tree.insert('', tk.END, values=(
                result['variant'],
                round(result['time_avg']['keygen'], 2),
                round(result['time_avg']['encap'], 2),
                round(result['time_avg']['decap'], 2),
                result['size_avg']['public_key'],
                result['size_avg']['ciphertext'],
                result['size_avg']['secret_key']
            ))

        tree.pack(fill=tk.BOTH, expand=True)
