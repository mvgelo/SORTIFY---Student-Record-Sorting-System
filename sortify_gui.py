import customtkinter as ctk
from tkinter import messagebox
import time

import sortify_database as database

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG_MAIN = ("#f0f2f5", "#0f172a")
BG_SIDEBAR = ("#ffffff", "#111827")
CARD_BG = ("#ffffff", "#1f2937")
TABLE_HEADER_BG = ("#e5e7eb", "#374151")
ALGO_INFO_BG = ("#e5f0ff", "#1e3a8a")
TEXT_PRIMARY = ("#1e293b", "#e5e7eb")
TEXT_SECONDARY = ("#64748b", "#9ca3af")
PRIMARY_BTN = ("#5c6ac4", "#4f46e5")
PRIMARY_HOVER = ("#4f51c0", "#4338ca")
NEUTRAL_BTN = ("#e5e7eb", "#374151")
NEUTRAL_HOVER = ("#d1d5db", "#4b5563")
DANGER_BTN = ("#fecaca", "#7f1d1d")
DANGER_HOVER = ("#f87171", "#991b1b")
DANGER_TEXT = ("#7f1d1d", "#fecaca")

FONT_H1 = ("Segoe UI Variable", 24, "bold")
FONT_H2 = ("Segoe UI Variable", 18, "bold")
FONT_BODY = ("Segoe UI Variable", 13, "normal")
FONT_SMALL = ("Segoe UI Variable", 12, "normal")

P = 12
ROW_HEIGHT = 34
VISIBLE_ROWS = 10
TABLE_HEIGHT = ROW_HEIGHT * VISIBLE_ROWS + 18
BTN_H = 36
EMPTY_SORTED_ROWS = 2
COL_WEIGHTS_NO_ACTION = [2, 5, 2, 2, 4, 2]
COL_WEIGHTS_WITH_ACTION = [2, 5, 2, 2, 4, 2, 4]

SORT_KEY_BY_COLUMN = {
    "Name": 1,
    "ID": 0,
    "Age": 2,
    "GWA": 3,
    "Year": 5,
}

ALGO_INFO = {
    "Quick Sort": {
        "desc": "Divide-and-conquer algorithm that partitions data around a pivot and recursively sorts both sides.",
        "time": "Best: O(n log n) | Average: O(n log n) | Worst: O(n^2)",
        "space": "Best: O(log n) | Average: O(log n) | Worst: O(n)",
    },
    "Bubble Sort": {
        "desc": "Simple comparison algorithm that repeatedly swaps adjacent out-of-order elements until sorted.",
        "time": "Best: O(n) | Average: O(n^2) | Worst: O(n^2)",
        "space": "Best: O(1) | Average: O(1) | Worst: O(1)",
    },
    "Insertion Sort": {
        "desc": "Builds the sorted portion one element at a time by inserting each item into its correct position.",
        "time": "Best: O(n) | Average: O(n^2) | Worst: O(n^2)",
        "space": "Best: O(1) | Average: O(1) | Worst: O(1)",
    },
    "Merge Sort": {
        "desc": "Stable divide-and-conquer algorithm that splits input, recursively sorts parts, then merges them.",
        "time": "Best: O(n log n) | Average: O(n log n) | Worst: O(n log n)",
        "space": "Best: O(n) | Average: O(n) | Worst: O(n)",
    },
}


class TableView:
    def __init__(
        self,
        app,
        parent,
        title,
        show_actions=False,
        action_mode="archive",
        col_weights=None,
        include_actions_header=True,
        visible_rows=VISIBLE_ROWS,
    ):
        self.app = app
        self.show_actions = show_actions
        self.action_mode = action_mode
        self.include_actions_header = include_actions_header
        self.col_weights = col_weights or (COL_WEIGHTS_WITH_ACTION if show_actions else COL_WEIGHTS_NO_ACTION)

        self.table_height = ROW_HEIGHT * visible_rows + 18

        self.title_label = ctk.CTkLabel(parent, text=title, font=FONT_H2, text_color=TEXT_PRIMARY)
        self.title_label.pack(anchor="w", pady=(0, 4))

        self.card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
        self.card.pack(fill="x")

        self.header = ctk.CTkFrame(self.card, fg_color=TABLE_HEADER_BG, corner_radius=8)
        self.header.pack(fill="x", padx=P, pady=(P, 6))

        self.table = ctk.CTkScrollableFrame(self.card, fg_color=CARD_BG, height=self.table_height)
        self.table.pack(fill="x", padx=P, pady=(0, P))
        self.table.grid_columnconfigure(0, weight=1)

        self._draw_header()
        self.app._bind_table_hover_scroll(self.table)
        self.app._update_scrollbar_visibility(self.table)

    def set_visible_rows(self, visible_rows):
        self.table_height = ROW_HEIGHT * visible_rows + 18
        self.table.configure(height=self.table_height)
        self.app.update_idletasks()
        self.app._update_scrollbar_visibility(self.table)

    def _cell_sticky(self, col_idx):
        return "w"

    def _configure_columns(self, widget):
        for i, weight in enumerate(self.col_weights):
            widget.columnconfigure(i, weight=weight, uniform="table_cols")

    def _draw_header(self):
        for w in self.header.winfo_children():
            w.destroy()

        self._configure_columns(self.header)

        labels = ["Student ID", "Name", "Age", "GWA", "Program", "Year"]
        for i, label in enumerate(labels):
            sticky = self._cell_sticky(i)
            ctk.CTkLabel(self.header, text=label, font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
                row=0, column=i, sticky=sticky, padx=6, pady=6
            )

        if self.show_actions and self.include_actions_header:
            ctk.CTkLabel(self.header, text="Actions", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
                row=0, column=6, sticky="w", padx=6, pady=6
            )

    def set_title(self, text):
        self.title_label.configure(text=text)

    def _clear(self):
        for w in self.table.winfo_children():
            w.destroy()

    def _placeholder(self, text):
        row = ctk.CTkFrame(self.table, fg_color=CARD_BG)
        row.grid(row=0, column=0, sticky="ew", pady=2)
        self._configure_columns(row)
        span = len(self.col_weights)
        ctk.CTkLabel(row, text=text, font=FONT_BODY, text_color=TEXT_SECONDARY).grid(
            row=0, column=0, columnspan=span, sticky="w", padx=6, pady=6
        )

    def _render_row(self, data, row_idx, archived_rowid=None):
        row = ctk.CTkFrame(self.table, fg_color=CARD_BG)
        row.grid(row=row_idx, column=0, sticky="ew", pady=1)
        row.grid_propagate(False)
        row.configure(height=ROW_HEIGHT)
        self._configure_columns(row)

        sid, name, age, gwa, program, year = data
        values = [sid, name, str(age), f"{float(gwa):.2f}", program, str(year)]

        for col, val in enumerate(values):
            sticky = self._cell_sticky(col)
            ctk.CTkLabel(row, text=val, font=FONT_SMALL, text_color=TEXT_PRIMARY).grid(
                row=0, column=col, sticky=sticky, padx=6, pady=6
            )

        if self.show_actions:
            box = ctk.CTkFrame(row, fg_color="transparent")
            box.grid(row=0, column=6, sticky="w", padx=6)
            if self.action_mode == "archive":
                ctk.CTkButton(
                    box,
                    text="Archive",
                    width=74,
                    height=28,
                    fg_color=NEUTRAL_BTN,
                    hover_color=NEUTRAL_HOVER,
                    text_color=TEXT_PRIMARY,
                    command=lambda s=sid: self.app._on_archive_student(s),
                ).grid(row=0, column=0)
            elif self.action_mode == "delete_archived":
                ctk.CTkButton(
                    box,
                    text="Restore",
                    width=72,
                    height=28,
                    fg_color=NEUTRAL_BTN,
                    hover_color=NEUTRAL_HOVER,
                    text_color=TEXT_PRIMARY,
                    command=lambda r=archived_rowid: self.app._on_restore_archived(r),
                ).grid(row=0, column=0, padx=(0, 4))
                ctk.CTkButton(
                    box,
                    text="Delete",
                    width=70,
                    height=28,
                    fg_color=DANGER_BTN,
                    hover_color=DANGER_HOVER,
                    text_color=DANGER_TEXT,
                    command=lambda r=archived_rowid: self.app._on_delete_archived(r),
                ).grid(row=0, column=1)

    def render_rows(self, rows, placeholder, archived=False):
        self._clear()
        if not rows:
            self._placeholder(placeholder)
            self.app._update_scrollbar_visibility(self.table)
            return

        for i, row in enumerate(rows):
            if archived:
                archive_rowid = row[0]
                payload = row[1:]
                self._render_row(payload, i, archived_rowid=archive_rowid)
            else:
                self._render_row(row, i)

        self.app._update_scrollbar_visibility(self.table)


def _sort_value(record, idx):
    v = record[idx]
    if idx in (2, 5):
        return int(v)
    if idx == 3:
        return float(v)
    return str(v).lower()


def bubble_sort_students(records, key_index):
    a = list(records)
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if _sort_value(a[j], key_index) > _sort_value(a[j + 1], key_index):
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


def insertion_sort_students(records, key_index):
    a = list(records)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and _sort_value(a[j], key_index) > _sort_value(key, key_index):
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def quick_sort_students(records, key_index):
    if len(records) <= 1:
        return list(records)
    pivot = records[len(records) // 2]
    p = _sort_value(pivot, key_index)
    left = [r for r in records if _sort_value(r, key_index) < p]
    mid = [r for r in records if _sort_value(r, key_index) == p]
    right = [r for r in records if _sort_value(r, key_index) > p]
    return quick_sort_students(left, key_index) + mid + quick_sort_students(right, key_index)


def merge_sort_students(records, key_index):
    if len(records) <= 1:
        return list(records)
    mid = len(records) // 2
    left = merge_sort_students(records[:mid], key_index)
    right = merge_sort_students(records[mid:], key_index)

    out = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if _sort_value(left[i], key_index) <= _sort_value(right[j], key_index):
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        database.create_table()

        self.title("SORTIFY")
        self.geometry("1500x930")
        self.configure(fg_color=BG_MAIN)

        self._active_table = None
        self.nav_buttons = {}
        self.pages = {}
        self.current_page = None
        self.has_sorted_results = False

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self._build_pages()

        self._show_page("Dashboard")
        self._refresh_all_views(reset_sorted=True)
        self.after(50, lambda: self.sorted_table.set_visible_rows(EMPTY_SORTED_ROWS))

        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0, width=230)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="SORTIFY", font=("Segoe UI Variable", 30, "bold"), text_color=TEXT_PRIMARY).grid(
            row=0, column=0, padx=20, pady=(18, 0), sticky="w"
        )
        ctk.CTkLabel(sidebar, text="Student Record Sorting System", font=FONT_SMALL, text_color=TEXT_SECONDARY).grid(
            row=1, column=0, padx=20, pady=(0, 10), sticky="w"
        )

        names = ["Dashboard", "Add Records", "Sorting Lab", "Algorithm Comparison", "Dataset"]
        for i, name in enumerate(names, start=2):
            btn = ctk.CTkButton(
                sidebar,
                text=name,
                height=BTN_H,
                fg_color="transparent",
                hover_color=NEUTRAL_HOVER,
                text_color=TEXT_PRIMARY,
                anchor="w",
                font=FONT_BODY,
                command=lambda n=name: self._show_page(n),
            )
            btn.grid(row=i, column=0, sticky="ew", padx=12, pady=3)
            self.nav_buttons[name] = btn

        self.dark_mode_var = ctk.StringVar(value="off")
        ctk.CTkSwitch(
            sidebar,
            text="Dark Mode",
            variable=self.dark_mode_var,
            onvalue="on",
            offvalue="off",
            command=self._toggle_dark_mode,
        ).grid(row=len(names) + 3, column=0, sticky="w", padx=14, pady=(10, 0))

    def _build_main_area(self):
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN)
        self.main_scroll.grid(row=0, column=1, sticky="nsew")
        self.main_scroll.grid_rowconfigure(0, weight=1)
        self.main_scroll.grid_columnconfigure(0, weight=1)

        self.main = ctk.CTkFrame(self.main_scroll, fg_color=BG_MAIN)
        self.main.grid(row=0, column=0, sticky="nsew")
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

    def _build_pages(self):
        self.pages["Dashboard"] = self._build_dashboard_page()
        self.pages["Add Records"] = self._build_add_page()
        self.pages["Sorting Lab"] = self._build_sorting_page()
        self.pages["Algorithm Comparison"] = self._build_comparison_page()
        self.pages["Dataset"] = self._build_dataset_page()

    def _show_page(self, name):
        if self.current_page:
            self.pages[self.current_page].grid_forget()
        self.current_page = name
        self.pages[name].grid(row=0, column=0, sticky="nsew", padx=P, pady=P)

        for n, btn in self.nav_buttons.items():
            btn.configure(fg_color=PRIMARY_BTN if n == name else "transparent", text_color="white" if n == name else TEXT_PRIMARY)
        if name == "Sorting Lab" and not self.has_sorted_results:
            self.sorted_table.set_visible_rows(EMPTY_SORTED_ROWS)
        self._update_main_scrollbar_visibility()

    def _build_dashboard_page(self):
        page = ctk.CTkFrame(self.main, fg_color=BG_MAIN)
        page.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(page, text="Dashboard", font=FONT_H1, text_color=TEXT_PRIMARY).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self.card_total = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=10)
        self.card_total.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        self.card_archive = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=10)
        self.card_archive.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

        ctk.CTkLabel(self.card_total, text="Active Records", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(8, 0))
        self.dashboard_active = ctk.CTkLabel(self.card_total, text="0", font=("Segoe UI Variable", 30, "bold"), text_color=PRIMARY_BTN)
        self.dashboard_active.pack(anchor="w", padx=10, pady=(0, 8))

        ctk.CTkLabel(self.card_archive, text="Archived Records", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(8, 0))
        self.dashboard_archived = ctk.CTkLabel(self.card_archive, text="0", font=("Segoe UI Variable", 30, "bold"), text_color="#64748b")
        self.dashboard_archived.pack(anchor="w", padx=10, pady=(0, 8))

        charts_wrap = ctk.CTkFrame(page, fg_color=BG_MAIN)
        charts_wrap.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        charts_wrap.grid_columnconfigure((0, 1, 2), weight=1)

        program_card = ctk.CTkFrame(charts_wrap, fg_color=CARD_BG, corner_radius=10)
        program_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(program_card, text="Program", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(8, 4))
        self.program_chart_frame = ctk.CTkFrame(program_card, fg_color="transparent")
        self.program_chart_frame.pack(fill="x", padx=10, pady=(0, 10))

        age_card = ctk.CTkFrame(charts_wrap, fg_color=CARD_BG, corner_radius=10)
        age_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(age_card, text="Age", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(8, 4))
        self.age_chart_frame = ctk.CTkFrame(age_card, fg_color="transparent")
        self.age_chart_frame.pack(fill="x", padx=10, pady=(0, 10))

        year_card = ctk.CTkFrame(charts_wrap, fg_color=CARD_BG, corner_radius=10)
        year_card.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(year_card, text="Enrollment Year", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(8, 4))
        self.year_chart_frame = ctk.CTkFrame(year_card, fg_color="transparent")
        self.year_chart_frame.pack(fill="x", padx=10, pady=(0, 10))

        preview_wrap = ctk.CTkFrame(page, fg_color=BG_MAIN)
        preview_wrap.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.dashboard_preview = TableView(
            self,
            preview_wrap,
            title="Latest Records",
            show_actions=False,
            col_weights=COL_WEIGHTS_NO_ACTION,
            visible_rows=5,
        )
        return page

    def _build_add_page(self):
        page = ctk.CTkFrame(self.main, fg_color=BG_MAIN)
        page.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(page, text="Add Records", font=FONT_H1, text_color=TEXT_PRIMARY).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        form = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=10)
        form.grid(row=1, column=0, columnspan=2, sticky="ew")
        form.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(form, text="Student ID", font=FONT_BODY).grid(row=0, column=0, sticky="w", padx=P, pady=(8, 2))
        ctk.CTkLabel(form, text="Name (Surname, Firstname)", font=FONT_BODY).grid(row=0, column=1, sticky="w", padx=P, pady=(8, 2))
        self.entry_id = ctk.CTkEntry(form, height=36, placeholder_text="e.g., 0124-0001")
        self.entry_name = ctk.CTkEntry(form, height=36, placeholder_text="e.g., Dela Cruz, Juan")
        self.entry_id.grid(row=1, column=0, sticky="ew", padx=P, pady=(0, 6))
        self.entry_name.grid(row=1, column=1, sticky="ew", padx=P, pady=(0, 6))

        ctk.CTkLabel(form, text="GWA", font=FONT_BODY).grid(row=2, column=0, sticky="w", padx=P, pady=(2, 2))
        ctk.CTkLabel(form, text="Age", font=FONT_BODY).grid(row=2, column=1, sticky="w", padx=P, pady=(2, 2))
        self.entry_gwa = ctk.CTkEntry(form, height=36, placeholder_text="e.g., 1.75")
        self.entry_age = ctk.CTkEntry(form, height=36, placeholder_text="e.g., 20")
        self.entry_gwa.grid(row=3, column=0, sticky="ew", padx=P, pady=(0, 6))
        self.entry_age.grid(row=3, column=1, sticky="ew", padx=P, pady=(0, 6))

        ctk.CTkLabel(form, text="Program", font=FONT_BODY).grid(row=4, column=0, sticky="w", padx=P, pady=(2, 2))
        ctk.CTkLabel(form, text="Enrollment Year", font=FONT_BODY).grid(row=4, column=1, sticky="w", padx=P, pady=(2, 2))
        self.entry_major = ctk.CTkEntry(form, height=36, placeholder_text="e.g., BSCS")
        self.entry_year = ctk.CTkEntry(form, height=36, placeholder_text="e.g., 2024")
        self.entry_major.grid(row=5, column=0, sticky="ew", padx=P, pady=(0, 8))
        self.entry_year.grid(row=5, column=1, sticky="ew", padx=P, pady=(0, 8))

        btn_box = ctk.CTkFrame(form, fg_color="transparent")
        btn_box.grid(row=6, column=0, columnspan=2, sticky="w", padx=P, pady=(0, 8))
        ctk.CTkButton(btn_box, text="Add Student", height=BTN_H, width=140, fg_color=PRIMARY_BTN, hover_color=PRIMARY_HOVER, command=self._on_add_student).grid(
            row=0, column=0, sticky="w", padx=(0, 6)
        )
        ctk.CTkButton(btn_box, text="Clear Form", height=BTN_H, width=140, fg_color=NEUTRAL_BTN, hover_color=NEUTRAL_HOVER, text_color=TEXT_PRIMARY, command=self._on_clear_form).grid(
            row=0, column=1, sticky="w", padx=(6, 0)
        )

        preview_wrap = ctk.CTkFrame(page, fg_color=BG_MAIN)
        preview_wrap.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.add_preview = TableView(
            self,
            preview_wrap,
            title="Latest Records Preview",
            show_actions=False,
            col_weights=COL_WEIGHTS_NO_ACTION,
            visible_rows=5,
        )
        return page

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
            values=["Quick Sort", "Bubble Sort", "Insertion Sort", "Merge Sort"],
            command=self._on_algo_changed,
            width=220,
        )
        self.combo_algo.set("Quick Sort")
        self.combo_algo.configure(height=BTN_H)
        self.combo_algo.grid(row=1, column=0, sticky="ew", padx=P, pady=(0, 8))

        self.combo_sort_by = ctk.CTkComboBox(controls, values=["Name", "ID", "Age", "GWA", "Year"], width=180)
        self.combo_sort_by.set("Name")
        self.combo_sort_by.configure(height=BTN_H)
        self.combo_sort_by.grid(row=1, column=1, sticky="ew", padx=P, pady=(0, 6))

        self.switch_desc = ctk.StringVar(value="off")
        ctk.CTkSwitch(controls, text="Inverse (Descending)", variable=self.switch_desc, onvalue="on", offvalue="off").grid(
            row=1, column=2, sticky="w", padx=P, pady=(0, 6)
        )

        ctk.CTkButton(controls, text="Run Sort", width=140, height=BTN_H, fg_color=PRIMARY_BTN, hover_color=PRIMARY_HOVER, command=self._on_run_sort).grid(
            row=2, column=0, columnspan=3, sticky="w", padx=P, pady=(0, 8)
        )

        self.label_dataset = ctk.CTkLabel(controls, text="Current Dataset: 0 records", font=FONT_SMALL, text_color=TEXT_SECONDARY)
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
            self,
            tables_wrap,
            title="Sorted Data",
            show_actions=False,
            col_weights=COL_WEIGHTS_NO_ACTION,
            visible_rows=3,
        )

        tables_wrap = ctk.CTkFrame(page, fg_color=BG_MAIN)
        tables_wrap.pack(fill="x", pady=(10, 0))
        
        self.original_table = TableView(
            self,
            tables_wrap,
            title="Original Data (0 records)",
            show_actions=False,
            col_weights=COL_WEIGHTS_NO_ACTION,
        )
        self.sorted_table.set_visible_rows(EMPTY_SORTED_ROWS)
        return page

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
            controls,
            text="Run Benchmark",
            width=160,
            height=BTN_H,
            fg_color=PRIMARY_BTN,
            hover_color=PRIMARY_HOVER,
            command=self._on_run_benchmark,
        ).grid(row=3, column=1, sticky="w", padx=P, pady=(0, 8))

        self.compare_chart = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=10)
        self.compare_chart.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(
            self.compare_chart,
            text="Timing Growth (relative by size and algorithm)",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w", padx=10, pady=(8, 4))
        self.compare_chart_body = ctk.CTkFrame(self.compare_chart, fg_color="transparent")
        self.compare_chart_body.pack(fill="x", padx=10, pady=(0, 8))

        self.compare_output = ctk.CTkTextbox(page, height=360, fg_color=CARD_BG)
        self.compare_output.pack(fill="both", expand=True, pady=(10, 0))
        self.compare_output.insert("end", "Benchmark results will appear here.\n")
        self.compare_output.configure(state="disabled")
        return page

    def _build_dataset_page(self):
        page = ctk.CTkFrame(self.main, fg_color=BG_MAIN)
        ctk.CTkLabel(page, text="Dataset", font=FONT_H1, text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        tables = ctk.CTkFrame(page, fg_color=BG_MAIN)
        tables.pack(fill="x")

        self.dataset_active_table = TableView(
            self,
            tables,
            title="Active Dataset",
            show_actions=True,
            action_mode="archive",
            col_weights=COL_WEIGHTS_WITH_ACTION,
        )

        active_actions = ctk.CTkFrame(tables, fg_color=CARD_BG, corner_radius=10)
        active_actions.pack(fill="x", pady=(8, 0))
        ctk.CTkButton(
            active_actions,
            text="Archive All Active",
            height=BTN_H,
            fg_color=NEUTRAL_BTN,
            hover_color=NEUTRAL_HOVER,
            text_color=TEXT_PRIMARY,
            command=self._on_archive_all,
        ).pack(anchor="w", padx=10, pady=8)

        archived_toggle = ctk.CTkFrame(tables, fg_color="transparent")
        archived_toggle.pack(fill="x", pady=(10, 0))
        self.btn_toggle_archived = ctk.CTkButton(
            archived_toggle,
            text="Show Archived Dataset",
            height=BTN_H,
            fg_color=PRIMARY_BTN,
            hover_color=PRIMARY_HOVER,
            command=self._toggle_archived_section,
        )
        self.btn_toggle_archived.pack(anchor="w")

        self.archived_section = ctk.CTkFrame(tables, fg_color=BG_MAIN)
        self.archived_visible = False

        archive_action = ctk.CTkFrame(self.archived_section, fg_color=CARD_BG, corner_radius=10)
        archive_action.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(
            archive_action,
            text="Permanently Delete All Archived",
            height=BTN_H,
            fg_color=DANGER_BTN,
            hover_color=DANGER_HOVER,
            text_color=DANGER_TEXT,
            command=self._on_delete_all_archived,
        ).pack(anchor="w", padx=10, pady=8)

        self.dataset_archived_table = TableView(
            self,
            self.archived_section,
            title="Archived Dataset",
            show_actions=True,
            action_mode="delete_archived",
            col_weights=COL_WEIGHTS_WITH_ACTION,
        )
        return page

    def _bind_table_hover_scroll(self, table):
        table.bind("<Enter>", lambda _e: self._set_active_table(table))
        table.bind("<Leave>", lambda _e: self._clear_active_table(table))

    def _set_active_table(self, table):
        self._active_table = table

    def _clear_active_table(self, table):
        if self._active_table is table:
            self._active_table = None

    def _on_mousewheel(self, event):
        raw_steps = int(event.delta / 120) if event.delta else 0
        steps = max(1, abs(raw_steps))
        delta = -steps if raw_steps >= 0 else steps
        delta *= 30
        if self._active_table is not None:
            canvas = getattr(self._active_table, "_parent_canvas", None)
            if canvas is not None:
                canvas.yview_scroll(delta, "units")
                self._update_scrollbar_visibility(self._active_table)
                return

        main_canvas = getattr(self.main_scroll, "_parent_canvas", None)
        if main_canvas is not None:
            start, end = main_canvas.yview()
            if start > 0.0 or end < 1.0:
                main_canvas.yview_scroll(delta, "units")

    def _toggle_dark_mode(self):
        mode = "dark" if self.dark_mode_var.get() == "on" else "light"
        ctk.set_appearance_mode(mode)
        self._refresh_all_views(reset_sorted=not self.has_sorted_results)

    def _update_main_scrollbar_visibility(self):
        try:
            self.update_idletasks()
            scrollbar = getattr(self.main_scroll, "_scrollbar", None)
            canvas = getattr(self.main_scroll, "_parent_canvas", None)
            if not scrollbar or not canvas:
                return
            scrollbar.grid()
        except Exception:
            pass

    def _update_scrollbar_visibility(self, table):
        try:
            self.update_idletasks()
            scrollbar = getattr(table, "_scrollbar", None)
            canvas = getattr(table, "_parent_canvas", None)
            if not scrollbar or not canvas:
                return
            start, end = canvas.yview()
            if start > 0.0 or end < 1.0:
                scrollbar.grid()
            else:
                scrollbar.grid_remove()
        except Exception:
            pass

    def _refresh_dashboard(self, active_rows, archived_rows):
        self.dashboard_active.configure(text=str(len(active_rows)))
        self.dashboard_archived.configure(text=str(len(archived_rows)))
        self._draw_program_bar_chart(active_rows)
        self._draw_age_histogram(active_rows)
        self._draw_year_line_chart(active_rows)

        self.dashboard_preview.render_rows(active_rows[:5], "No records yet.")

    def _draw_program_bar_chart(self, rows):
        for w in self.program_chart_frame.winfo_children():
            w.destroy()

        counts = {}
        for r in rows:
            p = str(r[4]).strip() or "N/A"
            counts[p] = counts.get(p, 0) + 1
        top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        if not top:
            ctk.CTkLabel(self.program_chart_frame, text="No data", text_color=TEXT_SECONDARY, font=FONT_SMALL).pack(anchor="w")
            return
        max_v = max(v for _, v in top)
        for name, v in top:
            row = ctk.CTkFrame(self.program_chart_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{name} ({v})", width=130, anchor="w", font=FONT_SMALL).pack(side="left")
            bar = ctk.CTkProgressBar(row)
            bar.pack(side="left", fill="x", expand=True, padx=(8, 0))
            bar.set(v / max_v if max_v else 0)

    def _draw_age_histogram(self, rows):
        for w in self.age_chart_frame.winfo_children():
            w.destroy()

        ages = []
        for r in rows:
            try:
                ages.append(int(r[2]))
            except Exception:
                continue
        if not ages:
            ctk.CTkLabel(self.age_chart_frame, text="No data", text_color=TEXT_SECONDARY, font=FONT_SMALL).pack(anchor="w")
            return

        bins = {}
        for age in ages:
            bucket = (age // 2) * 2
            bins[bucket] = bins.get(bucket, 0) + 1
        keys = sorted(bins.keys())[:8]
        max_v = max(bins[k] for k in keys)
        for k in keys:
            v = bins[k]
            row = ctk.CTkFrame(self.age_chart_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{k}-{k+1}", width=70, anchor="w", font=FONT_SMALL).pack(side="left")
            bar = ctk.CTkProgressBar(row, progress_color="#93c5fd")
            bar.pack(side="left", fill="x", expand=True, padx=(8, 0))
            bar.set(v / max_v if max_v else 0)

    def _draw_year_line_chart(self, rows):
        for w in self.year_chart_frame.winfo_children():
            w.destroy()

        counts = {}
        for r in rows:
            try:
                y = int(r[5])
            except Exception:
                continue
            counts[y] = counts.get(y, 0) + 1
        years = sorted(counts.keys())
        if not years:
            ctk.CTkLabel(self.year_chart_frame, text="No data", text_color=TEXT_SECONDARY, font=FONT_SMALL).pack(anchor="w")
            return

        max_v = max(counts[y] for y in years)
        for y in years:
            v = counts[y]
            row = ctk.CTkFrame(self.year_chart_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=str(y), width=70, anchor="w", font=FONT_SMALL).pack(side="left")
            bar = ctk.CTkProgressBar(row, progress_color=PRIMARY_BTN)
            bar.pack(side="left", fill="x", expand=True, padx=(8, 0))
            bar.set(v / max_v if max_v else 0)

    def _refresh_add_page(self, active_rows):
        self.add_preview.render_rows(active_rows[:5], "No records yet.")

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

    def _refresh_dataset_page(self, active_rows, archived_rows):
        self.dataset_active_table.render_rows(active_rows, "No active records.")
        self.dataset_archived_table.render_rows(archived_rows, "No archived records.", archived=True)

    def _toggle_archived_section(self):
        self.archived_visible = not self.archived_visible
        if self.archived_visible:
            self.archived_section.pack(fill="x", pady=(8, 0))
            self.btn_toggle_archived.configure(text="Hide Archived Dataset")
        else:
            self.archived_section.pack_forget()
            self.btn_toggle_archived.configure(text="Show Archived Dataset")

    def _refresh_all_views(self, reset_sorted=False, sorted_rows=None):
        active_rows = database.get_all_students()
        archived_rows = database.get_archived_students()

        self._refresh_dashboard(active_rows, archived_rows)
        self._refresh_add_page(active_rows)
        self._refresh_sorting_page(active_rows, reset_sorted=reset_sorted, sorted_rows=sorted_rows)
        self._refresh_dataset_page(active_rows, archived_rows)
        self._update_main_scrollbar_visibility()

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
            ctk.CTkLabel(self.compare_chart_body, text=algo, font=FONT_SMALL, text_color=TEXT_PRIMARY).pack(anchor="w", pady=(4, 2))
            for size, ms in growth[algo]:
                row = ctk.CTkFrame(self.compare_chart_body, fg_color="transparent")
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(row, text=f"N={size}", width=70, anchor="w", font=FONT_SMALL).pack(side="left")
                bar = ctk.CTkProgressBar(row, progress_color=PRIMARY_BTN)
                bar.pack(side="left", fill="x", expand=True, padx=(8, 6))
                bar.set(ms / max_ms if max_ms else 0)
                ctk.CTkLabel(row, text=f"{ms:.2f} ms", width=80, anchor="e", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="right")

    def _on_algo_changed(self, algo_name):
        info = ALGO_INFO.get(algo_name, ALGO_INFO["Quick Sort"])
        self.label_algo_title.configure(text=algo_name)
        self.label_algo_desc.configure(text=info["desc"])
        self.label_time.configure(text=f"Time: {info['time']}")
        self.label_space.configure(text=f"Space: {info['space']}")

    def _on_add_student(self):
        sid = self.entry_id.get().strip()
        name = self.entry_name.get().strip()
        gwa_raw = self.entry_gwa.get().strip()
        age_raw = self.entry_age.get().strip()
        program = self.entry_major.get().strip()
        year_raw = self.entry_year.get().strip()

        if not sid or not name or not gwa_raw or not age_raw or not program or not year_raw:
            messagebox.showerror("Validation", "Please fill in all fields.")
            return

        if "," not in name:
            messagebox.showerror("Validation", 'Name must be in the format "Surname, Firstname".')
            return
        surname, firstname = [part.strip() for part in name.split(",", 1)]
        if not surname or not firstname:
            messagebox.showerror("Validation", 'Name must be in the format "Surname, Firstname".')
            return

        try:
            age = int(age_raw)
            gwa = float(gwa_raw)
            year = int(year_raw)
        except ValueError:
            messagebox.showerror("Validation", "Age, GWA, and enrollment year must be valid numbers.")
            return

        if database.student_id_exists(sid):
            messagebox.showerror("Duplicate", f"Student ID {sid!r} already exists.")
            return

        database.add_student((sid, name, age, gwa, program, year))
        self._on_clear_form()
        self._refresh_all_views(reset_sorted=True)

    def _on_clear_form(self):
        for entry in (self.entry_id, self.entry_name, self.entry_gwa, self.entry_age, self.entry_major, self.entry_year):
            entry.delete(0, "end")

    def _on_archive_student(self, student_id):
        if not messagebox.askyesno("Archive record", f"Archive student {student_id}?"):
            return
        database.archive_student(student_id)
        self._refresh_all_views(reset_sorted=True)

    def _on_archive_all(self):
        if not messagebox.askyesno("Archive all", "Archive all active records?"):
            return
        database.archive_all_students()
        self._refresh_all_views(reset_sorted=True)

    def _on_delete_archived(self, archive_rowid):
        if archive_rowid is None:
            return
        if not messagebox.askyesno("Delete archived", "Permanently delete this archived record?"):
            return
        database.delete_archived_student(archive_rowid)
        self._refresh_all_views(reset_sorted=False)

    def _on_restore_archived(self, archive_rowid):
        if archive_rowid is None:
            return
        if not messagebox.askyesno("Restore archived", "Restore this archived record to active dataset?"):
            return
        database.restore_archived_student(archive_rowid)
        self._refresh_all_views(reset_sorted=True)

    def _on_delete_all_archived(self):
        if not messagebox.askyesno("Delete all archived", "Permanently delete all archived records?"):
            return
        database.clear_archived_students()
        self._refresh_all_views(reset_sorted=False)

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


if __name__ == "__main__":
    app = App()
    app.mainloop()
