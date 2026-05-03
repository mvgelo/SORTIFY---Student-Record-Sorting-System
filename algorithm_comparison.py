import customtkinter as ctk
import time
from tkinter import messagebox
from constants import (
    BG_MAIN, CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY,
    PRIMARY_BTN, PRIMARY_HOVER,
    FONT_H1, FONT_BODY, FONT_SMALL,
    BTN_H, P, SORT_KEY_BY_COLUMN,
)
import sortify_database as database
from sorting import (
    quick_sort_students,
    bubble_sort_students,
    insertion_sort_students,
    merge_sort_students,
)

class AlgorithmComparisonMixin:
    def _build_comparison_page(self):
        page = ctk.CTkFrame(self.main, fg_color=BG_MAIN)
        ctk.CTkLabel(page, text="Algorithm Comparison", font=FONT_H1, text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        controls = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=10)
        controls.pack(fill="x")
        controls.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(controls, text="Dataset sizes (comma-separated)", font=FONT_BODY).grid(row=0, column=0, sticky="w", padx=P, pady=(8, 2))
        ctk.CTkLabel(controls, text="Sort Key", font=FONT_BODY).grid(row=0, column=1, sticky="w", padx=P, pady=(8, 2))
        self.entry_sizes = ctk.CTkEntry(controls, height=BTN_H, placeholder_text="e.g., 100, 500, 1000")
        self.entry_sizes.insert(0, "100, 500, 1000")
        self.entry_sizes.grid(row=1, column=0, sticky="ew", padx=P, pady=(0, 8))
        self.combo_compare_key = ctk.CTkComboBox(controls, values=["Name", "ID", "Age", "GWA", "Year"], height=BTN_H)
        self.combo_compare_key.set("GWA")
        self.combo_compare_key.grid(row=1, column=1, sticky="ew", padx=P, pady=(0, 8))

        ctk.CTkLabel(controls, text="Runs per size", font=FONT_BODY).grid(row=2, column=0, sticky="w", padx=P, pady=(0, 2))
        self.entry_runs = ctk.CTkEntry(controls, height=BTN_H, width=120, placeholder_text="e.g., 5")
        self.entry_runs.insert(0, "5")
        self.entry_runs.grid(row=3, column=0, sticky="w", padx=P, pady=(0, 8))

        ctk.CTkButton(
            controls, text="Run Benchmark", width=160, height=BTN_H,
            fg_color=PRIMARY_BTN, hover_color=PRIMARY_HOVER,
            command=self._on_run_benchmark,
        ).grid(row=3, column=1, sticky="w", padx=P, pady=(0, 8))

        self.compare_chart = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=10)
        self.compare_chart.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(
            self.compare_chart, text="Timing Growth (relative by size and algorithm)",
            font=FONT_BODY, text_color=TEXT_SECONDARY,
        ).pack(anchor="w", padx=10, pady=(8, 4))
        self.compare_chart_body = ctk.CTkFrame(self.compare_chart, fg_color="transparent")
        self.compare_chart_body.pack(fill="x", padx=10, pady=(0, 8))

        self.compare_output = ctk.CTkTextbox(page, height=360, fg_color=CARD_BG)
        self.compare_output.pack(fill="both", expand=True, pady=(10, 0))
        self.compare_output.insert("end", "Benchmark results will appear here.\n")
        self.compare_output.configure(state="disabled")
        return page

    def _clone_records_for_size(self, records, target_size):
        if not records:
            generated = []
            for i in range(target_size):
                sid = f"AUTO-{i+1:05d}"
                generated.append((sid, f"Surname{i}, Name{i}", 18 + (i % 8), 1.0 + (i % 30) / 20.0, "BSCS", 2020 + (i % 6)))
            return generated
        out = []
        idx = 0
        while len(out) < target_size:
            base = records[idx % len(records)]
            sid = f"{base[0]}-{idx}"
            out.append((sid, base[1], int(base[2]), float(base[3]), base[4], int(base[5])))
            idx += 1
        return out

    def _run_sort_algo(self, algo_name, records, key_idx):
        if algo_name == "Quick Sort":
            return quick_sort_students(records, key_idx)
        if algo_name == "Bubble Sort":
            return bubble_sort_students(records, key_idx)
        if algo_name == "Insertion Sort":
            return insertion_sort_students(records, key_idx)
        return merge_sort_students(records, key_idx)

    def _on_run_benchmark(self):
        raw = self.entry_sizes.get().strip()
        try:
            sizes = [int(x.strip()) for x in raw.split(",") if x.strip()]
            sizes = [s for s in sizes if s > 0]
        except ValueError:
            messagebox.showerror("Benchmark", "Invalid sizes. Use comma-separated integers, e.g., 100, 500, 1000")
            return
        if not sizes:
            messagebox.showerror("Benchmark", "Please provide at least one valid dataset size.")
            return
        try:
            runs = int(self.entry_runs.get().strip())
            if runs < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Benchmark", "Runs per size must be a positive integer.")
            return

        key_idx = SORT_KEY_BY_COLUMN[self.combo_compare_key.get()]
        base_rows = database.get_all_students()
        algos = ["Quick Sort", "Merge Sort", "Insertion Sort", "Bubble Sort"]

        lines = [f"Algorithm Comparison (average of {runs} runs, time in ms)", "-" * 56]
        growth = {algo: [] for algo in algos}
        for size in sizes:
            dataset = self._clone_records_for_size(base_rows, size)
            lines.append(f"\nN = {size}")
            for algo in algos:
                total = 0.0
                for _ in range(runs):
                    sample = list(dataset)
                    t0 = time.perf_counter()
                    self._run_sort_algo(algo, sample, key_idx)
                    total += (time.perf_counter() - t0) * 1000
                avg = total / runs
                growth[algo].append((size, avg))
                lines.append(f"  {algo:<14} {avg:>9.3f} ms")

        self.compare_output.configure(state="normal")
        self.compare_output.delete("1.0", "end")
        self.compare_output.insert("end", "\n".join(lines))
        self.compare_output.configure(state="disabled")

        for w in self.compare_chart_body.winfo_children():
            w.destroy()
        max_ms = max((ms for vals in growth.values() for _, ms in vals), default=1.0)
        for algo in algos:
            ctk.CTkLabel(self.compare_chart_body, text=algo, font=FONT_SMALL, text_color=TEXT_PRIMARY).pack(
                anchor="w", pady=(4, 2))
            for size, ms in growth[algo]:
                row = ctk.CTkFrame(self.compare_chart_body, fg_color="transparent")
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(row, text=f"N={size}", width=70, anchor="w", font=FONT_SMALL).pack(side="left")
                bar = ctk.CTkProgressBar(row, progress_color=PRIMARY_BTN)
                bar.pack(side="left", fill="x", expand=True, padx=(8, 6))
                bar.set(ms / max_ms if max_ms else 0)
                ctk.CTkLabel(row, text=f"{ms:.2f} ms", width=80, anchor="e", font=FONT_SMALL,
                             text_color=TEXT_SECONDARY).pack(side="right")