import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from algorithms.signature.dilithium import DilithiumBenchmark
from algorithms.signature.falcon import FalconBenchmark
from visualization import plot_keygen_times, plot_sign_times, plot_verify_times, plot_total_times, plot_key_sizes_signature

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
            # Wybór odpowiedniej klasy benchmarku
            if alg_name.startswith("Dilithium"):
                benchmark = DilithiumBenchmark(variant=alg_name, message=message_bytes)
            elif alg_name.startswith("Falcon"):
                benchmark = FalconBenchmark(variant=alg_name, message=message_bytes)
            else:
                self.append_output(f"Nieobsługiwany algorytm: {alg_name}\n")
                continue

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
        print(filtered_results)
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
