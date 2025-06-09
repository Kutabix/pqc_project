import tkinter as tk
from .kem_window import KemWindow
from .sig_window import SigWindow


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Algorytmy Post Kwantowe")
        self.root.geometry("400x200")

        tk.Label(root, text="Wybierz tryb:").pack(pady=10)
        tk.Button(root, text="KEM Benchmark", command=self.open_kem_window).pack(pady=10)
        tk.Button(root, text="Signature Benchmark & Signing", command=self.open_sig_window).pack(pady=10)

    def open_kem_window(self):
        KemWindow(self.root)

    def open_sig_window(self):
        SigWindow(self.root)


def main():
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
