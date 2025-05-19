import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from algorithms.kem.kyber import KyberBenchmark
from algorithms.kem.bike import BikeBenchmark
from algorithms.signature.signature import SignatureBenchmark
from visualization import plot_key_sizes, \
    plot_total_time_comparison, plot_operation_times_bike, plot_operation_times_kyber, plot_key_sizes_signature, \
    plot_keygen_times, plot_sign_times, plot_verify_times, plot_total_times
import os
from pathlib import Path

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PQCrypto Benchmark Tool")
        self.root.geometry("400x200")

        tk.Label(root, text="Wybierz tryb:").pack(pady=10)
        tk.Button(root, text="KEM Benchmark", command=self.open_kem_window).pack(pady=10)
        tk.Button(root, text="Signature Benchmark & Signing", command=self.open_sig_window).pack(pady=10)

    def open_kem_window(self):
        KemWindow(self.root)

    def open_sig_window(self):
        SigWindow(self.root)

class KemWindow:
    def __init__(self, master):
        self.KEM_VARIANTS = [
            "Kyber512",
            "Kyber768",
            "Kyber1024",
            "BIKE-L1",
            "BIKE-L3",
            "BIKE-L5"
        ]

        self.window = tk.Toplevel(master)
        self.window.title("KEM Benchmark")
        self.window.geometry("600x700")
        self.window.resizable(False, False)

        tk.Label(self.window, text="Liczba iteracji:").pack(pady=10)
        self.iter_entry = tk.Entry(self.window)
        self.iter_entry.insert(0, "10")
        self.iter_entry.pack(pady=5)

        # Checkboxy do wyboru algorytmów
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

        self.table_button = tk.Button(self.window, text="Pokaż tabelę wyników", command=self.show_results_table)
        self.table_button.pack(pady=10)

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
            self.append_output(f"Uruchamiam {name}...\n")
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

RESULTS_DIR = "results/sig"
RESULTS_FILE = os.path.join(RESULTS_DIR, "signature_results.json")


class SigWindow:
    def __init__(self, master):
        self.ALGORITHMS = [
            "Dilithium2",
            "Dilithium3",
            "Dilithium5",
            "Falcon-512",
            "Falcon-1024",
        ]
        self.window = tk.Toplevel(master)
        self.window.title("Signature Benchmark & Signing")
        self.window.geometry("700x700")

        tk.Label(self.window, text="Wpisz tekst do podpisania:").pack(pady=5)
        self.text_entry = tk.Text(self.window, height=5, width=60)
        self.text_entry.pack()

        tk.Label(self.window, text="Liczba iteracji do benchmarku:").pack(pady=5)
        self.iter_entry = tk.Entry(self.window)
        self.iter_entry.insert(0, "10")
        self.iter_entry.pack()

        tk.Label(self.window, text="Wybierz algorytmy:").pack(pady=5)
        self.check_vars = []
        frame = tk.Frame(self.window)
        frame.pack(pady=5)
        for alg in self.ALGORITHMS:
            var = tk.IntVar(value=1)  # domyślnie zaznaczone
            cb = tk.Checkbutton(frame, text=alg, variable=var)
            cb.pack(side=tk.LEFT, padx=5)
            self.check_vars.append((alg, var))

        tk.Button(self.window, text="Uruchom benchmark podpisu", command=self.run_signature_benchmark).pack(pady=10)
        tk.Button(self.window, text="Pokaż wykresy z wyników", command=self.show_charts_from_file).pack(pady=5)
        tk.Button(self.window, text="Pokaż tabelę wyników", command=self.show_results_table).pack(pady=5)

        self.output = tk.Text(self.window, height=15, width=80)
        self.output.pack(pady=5)

    def append_output(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

    def run_signature_benchmark(self):
        self.output.delete("1.0", tk.END)

        selected_algorithms = [alg for alg, var in self.check_vars if var.get() == 1]

        if not selected_algorithms:
            self.append_output("Proszę wybrać przynajmniej jeden algorytm!\n")
            return

        message_text = self.text_entry.get("1.0", "end").strip()
        message_bytes = message_text.encode()

        try:
            iterations = int(self.iter_entry.get())
        except ValueError:
            iterations = 10

        all_results = []
        for alg_name in selected_algorithms:
            benchmark = SignatureBenchmark(alg_name, message=message_bytes)
            results = benchmark.run_benchmark(iterations=iterations)
            all_results.extend(results)

            for res in results:
                self.append_output(f"Algorytm: {res['algorithm']}\n")
                self.append_output(f" - Czas generowania klucza: {res['keygen_time_ms']:.2f} ms\n")
                self.append_output(f" - Średni czas podpisu: {res['avg_sign_time_ms']:.2f} ms\n")
                self.append_output(f" - Średni czas weryfikacji: {res['avg_verify_time_ms']:.2f} ms\n")
                self.append_output(f" - Rozmiar klucza publicznego: {res['public_key_size']} bajtów\n")
                self.append_output(f" - Rozmiar klucza prywatnego: {res['private_key_size']} bajtów\n")
                self.append_output(f" - Rozmiar podpisu: {res['signature_size']} bajtów\n")
                self.append_output(f" - Rozmiar wiadomości: {res['message_size']} bajtów\n\n")

        os.makedirs("results/sig", exist_ok=True)
        with open("results/sig/signature_results.json", "w") as f:
            json.dump({
                "message_size": len(message_bytes),
                "iterations": iterations,
                "results": all_results
            }, f, indent=2)

        self.append_output("Wyniki zapisano do results/sig/signature_results.json\n")

    def show_charts_from_file(self):
        try:
            with open("results/sig/signature_results.json", "r") as f:
                data = json.load(f)
        except Exception as e:
            self.append_output(f"Błąd podczas wczytywania wyników: {e}\n")
            return

        selected_algs = [alg for alg, var in self.check_vars if var.get()]
        if not selected_algs:
            self.append_output("Nie wybrano żadnego algorytmu do wyświetlenia wykresów.\n")
            return

        filtered_results = [r for r in data["results"] if r["algorithm"] in selected_algs]

        figs = [
            plot_keygen_times(filtered_results, data["message_size"]),
            plot_sign_times(filtered_results, data["message_size"]),
            plot_verify_times(filtered_results, data["message_size"]),
            plot_total_times(filtered_results, data["message_size"]),
            plot_key_sizes_signature(filtered_results, data["message_size"])
        ]

        titles = [
            "Czasy generowania kluczy",
            "Czasy podpisywania",
            "Czasy weryfikacji",
            "Czasy całkowite",
            "Rozmiary kluczy i podpisów"
        ]

        for fig, title in zip(figs, titles):
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
        try:
            with open("results/sig/signature_results.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Błąd", "Plik wyników nie istnieje!")
            return

        results = data["results"]

        # Tworzenie nowego okna
        table_window = tk.Toplevel(self.window)
        table_window.title("Tabela wyników benchmarku podpisu")
        table_window.geometry("900x400")

        frame = tk.Frame(table_window, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ['algorithm', 'keygen_time_ms', 'avg_sign_time_ms', 'avg_verify_time_ms',
                   'public_key_size', 'private_key_size', 'signature_size', 'message_size']

        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').capitalize())
            tree.column(col, width=120, anchor='center')

        for result in results:
            tree.insert('', tk.END, values=(
                result['algorithm'],
                round(result['keygen_time_ms'], 2),
                round(result['avg_sign_time_ms'], 2),
                round(result['avg_verify_time_ms'], 2),
                result['public_key_size'],
                result['private_key_size'],
                result['signature_size'],
                result['message_size']
            ))

        tree.pack(fill=tk.BOTH, expand=True)


def main():
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
