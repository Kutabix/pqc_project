import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithms.kem.kyber import KyberBenchmark
from algorithms.kem.bike import BikeBenchmark
from benchmarks.sig_bench import run_complete_benchmark, PDFSigner, PDF_FILE, ALGORITHMS
from visualization import generate_advanced_plots, generate_keygen_plot, plot_key_sizes, \
    plot_total_time_comparison, plot_operation_times_bike, plot_operation_times_kyber
import pandas as pd
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

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, height=700)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class KemWindow:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("KEM Benchmark")
        self.window.geometry("500x400")

        tk.Label(self.window, text="Liczba iteracji:").pack(pady=10)
        self.iter_entry = tk.Entry(self.window)
        self.iter_entry.insert(0, "10")
        self.iter_entry.pack(pady=5)

        self.run_button = tk.Button(self.window, text="Uruchom benchmark (512, 768, 1024)", command=self.run_benchmarks)
        self.run_button.pack(pady=10)

        self.output = tk.Text(self.window, height=10, width=50)
        self.output.pack(pady=10)
        self.output.config(state=tk.DISABLED)


        tk.Button(self.window, text="Pokaż wszystkie wykresy", command=self.show_all_plots).pack(pady=20)

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
        except Exception:
            messagebox.showerror("Błąd", "Niepoprawna liczba iteracji")
            return

        kem_variants = [
            ("Kyber512", KyberBenchmark("512")),
            ("Kyber768", KyberBenchmark("768")),
            ("Kyber1024", KyberBenchmark("1024")),
            ("BIKE-L1", BikeBenchmark("L1")),
            ("BIKE-L3", BikeBenchmark("L3")),
            ("BIKE-L5", BikeBenchmark("L5"))
        ]

        all_results = []
        self.append_output("Start benchmarku KEM...\n")

        for name, benchmark in kem_variants:
            self.append_output(f"Uruchamiam {name}...\n")
            result = benchmark.run_benchmark(iterations=iterations)
            all_results.append(result)
            self.append_output(f"{name} ukończony.\n")

        self.save_results(all_results)
        self.append_output("Benchmark KEM zakończony i zapisany.\n")

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

        titles = ["Operation Times", "Key Sizes", "Total Time Comparison"]

        for fig, title in zip(figs, titles):
            # Ustawiamy rozmiar figury matplotlib na mniejszy, np. (8, 5)
            fig.set_size_inches(8, 5)
            fig.tight_layout(pad=2.0)  # dopasuj marginesy

            # Nowe okno
            plot_window = tk.Toplevel(self.window)
            plot_window.title(title)
            plot_window.geometry("900x600")  # trochę większe okno niż figura

            frame = tk.Frame(plot_window, padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            w = canvas.get_tk_widget()
            w.pack(padx=10, pady=10)

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

        columns = ['variant', 'keygen_time', 'encap_time', 'decap_time', 'public_key_size', 'ciphertext_size',
                   'secret_key_size']

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


class SigWindow:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("Signature Benchmark & Signing")
        self.window.geometry("700x600")

        tk.Label(self.window, text="Wybierz algorytm:").pack()
        self.alg_var = tk.StringVar(value=ALGORITHMS[0])
        ttk.Combobox(self.window, values=ALGORITHMS, textvariable=self.alg_var).pack()

        tk.Label(self.window, text="Wpisz tekst do podpisania:").pack(pady=5)
        self.text_entry = tk.Text(self.window, height=5, width=60)
        self.text_entry.pack()

        tk.Button(self.window, text="Wybierz plik PDF", command=self.select_file).pack(pady=5)
        self.selected_file = None
        self.file_label = tk.Label(self.window, text="Brak wybranego pliku")
        self.file_label.pack()

        tk.Label(self.window, text="Liczba iteracji do benchmarku:").pack()
        self.iter_entry = tk.Entry(self.window)
        self.iter_entry.insert(0, "10")
        self.iter_entry.pack()

        tk.Button(self.window, text="Uruchom benchmark podpisu", command=self.run_signature_benchmark).pack(pady=10)
        tk.Button(self.window, text="Podpisz i zweryfikuj (tekst lub plik)", command=self.sign_and_verify).pack(pady=10)

        self.output = tk.Text(self.window, height=15, width=80)
        self.output.pack()

    def select_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if filepath:
            self.selected_file = filepath
            self.file_label.config(text=f"Wybrano: {os.path.basename(filepath)}")
        else:
            self.file_label.config(text="Brak wybranego pliku")

    def run_signature_benchmark(self):
        iterations = int(self.iter_entry.get())
        self.output.insert(tk.END, "Start benchmarku podpisu...\n")
        self.window.update()
        results = run_complete_benchmark(PDF_FILE, ALGORITHMS, iterations)
        self.save_signature_results(results)
        self.output.insert(tk.END, "Benchmark podpisu zakończony i zapisany.\n")

    def save_signature_results(self, results):
        base_dir = "results/sig"
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(results)
        csv_path = os.path.join(base_dir, "signature_results.csv")
        df.to_csv(csv_path, index=False)

    def sign_and_verify(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        file_to_sign = self.selected_file

        if not text and not file_to_sign:
            messagebox.showwarning("Brak danych", "Proszę wpisać tekst lub wybrać plik PDF do podpisania.")
            return

        algorithm = self.alg_var.get()
        signer = PDFSigner(algorithm)

        self.output.insert(tk.END, f"Generowanie kluczy dla {algorithm}...\n")
        keys = signer.generate_keys()

        try:
            if file_to_sign:
                self.output.insert(tk.END, f"Podpisywanie pliku {os.path.basename(file_to_sign)}...\n")
                sign_result = signer.sign_pdf(file_to_sign)
            else:
                # Jeśli chcemy podpisać tekst, możemy to zrobić przez zapisanie do pliku tymczasowego i podpisanie lub bezpośrednio, zależy jak implementacja signer'a.
                # Tu uprościmy i użyjemy metody sign_pdf na pliku PDF (wymaga pliku), więc jeśli jest tekst, trzeba by napisać metodę podpisującą tekst.
                self.output.insert(tk.END, "Podpisywanie tekstu nie jest wspierane w implementacji signer.\n")
                return

            self.output.insert(tk.END, "Podpisanie zakończone.\nWeryfikacja podpisu...\n")
            verify_result = signer.verify_pdf(file_to_sign if file_to_sign else PDF_FILE, sign_result['signature'], keys['public_key'])
            self.output.insert(tk.END, f"Weryfikacja zakończona. Czas: {verify_result['verify_time_ms']:.2f} ms\n")
        except Exception as e:
            messagebox.showerror("Błąd podczas podpisywania/weryfikacji", str(e))


def main():
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
