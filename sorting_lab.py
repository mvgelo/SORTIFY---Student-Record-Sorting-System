import customtkinter as ctk
from tkinter import messagebox
from constants import (
    BG_MAIN, CARD_BG, ALGO_INFO_BG, TEXT_PRIMARY, TEXT_SECONDARY,
    FONT_H1, FONT_H2, FONT_BODY, FONT_SMALL,
    BTN_H, P, EMPTY_SORTED_ROWS, VISIBLE_ROWS,
    PRIMARY_BTN, PRIMARY_HOVER,
    SORT_KEY_BY_COLUMN, ALGO_INFO,
)
from table_view import TableView
import sortify_database as database
from sorting import (
    quick_sort_students,
    bubble_sort_students,
    insertion_sort_students,
    merge_sort_students,
)

class SortingLabMixin:
    def _build_sorting_page(self):
        page = ctk.CTkFrame(self.main, fg_color=BG_MAIN)

        ctk.CTkLabel(page, text="Sorting Lab", font=FONT_H1, text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        controls = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=10)
        controls.pack(fill="x")
        controls.grid_columnconfigure(0, weight=4)
        controls.grid_columnconfigure(1, weight=4)
        controls.grid_columnconfigure(2, weight=2)

        ctk.CTkLabel(controls, text="Sorting Algorithm", font=FONT_BODY).grid(row=0, column=0, sticky="w", padx=P, pady=(8, 2))
        ctk.CTkLabel(controls, text="Sort By", font=FONT_BODY).grid(row=0, column=1, sticky="w", padx=P, pady=(8, 2))
        ctk.CTkLabel(controls, text="Order", font=FONT_BODY).grid(row=0, column=2, sticky="w", padx=P, pady=(8, 2))

        self.combo_algo = ctk.CTkComboBox(
            controls,
            values=["Quick Sort", "Bubble Sort", "Insertion Sort", "Merge Sort"], height=BTN_H,
            command=self._on_algo_changed,
        )
        self.combo_algo.set("Quick Sort")
        self.combo_algo.grid(row=1, column=0, sticky="ew", padx=P, pady=(0, 8))

        self.combo_sort_by = ctk.CTkComboBox(controls, values=["Name", "ID", "Age", "GWA", "Year"], height=BTN_H)
        self.combo_sort_by.set("Name")
        self.combo_sort_by.grid(row=1, column=1, sticky="ew", padx=P, pady=(0, 6))

        self.switch_desc = ctk.StringVar(value="off")
        ctk.CTkSwitch(controls, text="Inverse (Descending)", variable=self.switch_desc,
                      onvalue="on", offvalue="off").grid(row=1, column=2, sticky="w", padx=P, pady=(0, 6))

        ctk.CTkButton(controls, text="Run Sort", width=140, height=BTN_H,
                      fg_color=PRIMARY_BTN, hover_color=PRIMARY_HOVER,
                      command=self._on_run_sort).grid(row=2, column=0, columnspan=3, sticky="w", padx=P, pady=(0, 8))

        self.label_dataset = ctk.CTkLabel(controls, text="Current Dataset: 0 records",
                                          font=FONT_SMALL, text_color=TEXT_SECONDARY)
        self.label_dataset.grid(row=3, column=0, columnspan=3, sticky="e", padx=P, pady=(0, 8))

        info = ctk.CTkFrame(page, fg_color=ALGO_INFO_BG, corner_radius=10)
        info.pack(fill="x", pady=(10, 0))
        self.label_algo_title = ctk.CTkLabel(info, text="Quick Sort", font=FONT_H2, text_color=TEXT_PRIMARY)
        self.label_algo_title.pack(anchor="w", padx=P, pady=(8, 2))
        self.label_algo_desc = ctk.CTkLabel(info, text="", font=FONT_BODY, text_color=TEXT_PRIMARY, wraplength=1080, justify="left")
        self.label_algo_desc.pack(anchor="w", padx=P)
        self.label_time = ctk.CTkLabel(info, text="", font=FONT_SMALL, text_color=TEXT_PRIMARY)
        self.label_time.pack(anchor="w", padx=P, pady=(4, 0))
        self.label_space = ctk.CTkLabel(info, text="", font=FONT_SMALL, text_color=TEXT_PRIMARY)
        self.label_space.pack(anchor="w", padx=P, pady=(0, 8))
        self._on_algo_changed("Quick Sort")

        tables_wrap = ctk.CTkFrame(page, fg_color=BG_MAIN)
        tables_wrap.pack(fill="x", pady=(10, 0))
        self.sorted_table = TableView(
            self, tables_wrap, title="Sorted Data",
            show_actions=False, visible_rows=3,
        )

        tables_wrap = ctk.CTkFrame(page, fg_color=BG_MAIN)
        tables_wrap.pack(fill="x", pady=(10, 0))
        self.original_table = TableView(
            self, tables_wrap, title="Original Data (0 records)",
            show_actions=False,
        )
        self.sorted_table.set_visible_rows(EMPTY_SORTED_ROWS)
        return page

    def _refresh_sorting_page(self, active_rows, reset_sorted=False, sorted_rows=None):
        self.label_dataset.configure(text=f"Current Dataset: {len(active_rows)} records")
        self.original_table.set_title(f"Original Data ({len(active_rows)} records)")
        self.original_table.render_rows(active_rows, "No records yet.")

        if reset_sorted:
            self.has_sorted_results = False
            self.sorted_table.set_visible_rows(EMPTY_SORTED_ROWS)
            self.sorted_table.render_rows([], "Run sort to see ordered results.")
        elif sorted_rows is not None:
            self.has_sorted_results = True
            self.sorted_table.set_visible_rows(VISIBLE_ROWS)
            self.sorted_table.render_rows(sorted_rows, "No records to display.")

    def _on_algo_changed(self, algo_name):
        info = ALGO_INFO.get(algo_name, ALGO_INFO["Quick Sort"])
        self.label_algo_title.configure(text=algo_name)
        self.label_algo_desc.configure(text=info["desc"])
        self.label_time.configure(text=f"Time: {info['time']}")
        self.label_space.configure(text=f"Space: {info['space']}")

    def _on_run_sort(self):
        rows = database.get_all_students()
        if not rows:
            messagebox.showinfo("Sort", "No records to sort.")
            self._refresh_sorting_page(rows, reset_sorted=True)
            return

        key_idx = SORT_KEY_BY_COLUMN[self.combo_sort_by.get()]
        algo = self.combo_algo.get()

        if algo == "Quick Sort":
            sorted_rows = quick_sort_students(rows, key_idx)
        elif algo == "Bubble Sort":
            sorted_rows = bubble_sort_students(rows, key_idx)
        elif algo == "Insertion Sort":
            sorted_rows = insertion_sort_students(rows, key_idx)
        else:
            sorted_rows = merge_sort_students(rows, key_idx)

        if self.switch_desc.get() == "on":
            sorted_rows = list(reversed(sorted_rows))

        self._refresh_sorting_page(rows, reset_sorted=False, sorted_rows=sorted_rows)