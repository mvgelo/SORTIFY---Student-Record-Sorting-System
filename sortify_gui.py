import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

import sortify_database as database

#  THEME 

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Backgrounds
BG_MAIN = "#f0f2f5"
CARD_BG = "#ffffff"
CARD_BORDER = "#e0e3e8"

# Text
TEXT_PRIMARY = "#1e293b"
TEXT_SECONDARY = "#64748b"

# Buttons
PRIMARY_BTN = "#5c6ac4"
PRIMARY_HOVER = "#4f51c0"
NEUTRAL_BTN = "#e5e7eb"
NEUTRAL_HOVER = "#d1d5db"

# Fonts
FONT_H1 = ("Segoe UI Variable", 32, "bold")
FONT_H2 = ("Segoe UI Variable", 24, "bold")
FONT_BODY = ("Segoe UI Variable", 15, "normal")
FONT_SMALL = ("Segoe UI Variable", 13, "normal")
FONT_MONO = ("Fira Code", 14, "normal")

P = 24  # padding

# Columns: Student ID | Name | Age | GWA | Program | Year | Actions
COL_W = [2, 2, 2, 2, 2, 2, 0]

SORT_KEY_BY_COLUMN = {
    "Name": 1,
    "Student ID": 0,
    "Age": 2,
    "GWA": 3,
    "Enrollment Year": 5,
}


def _sort_value(record, col_index):
    v = record[col_index]
    if isinstance(v, str):
        return v.lower()
    return v


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
    pv = _sort_value(pivot, key_index)
    left = [x for x in records if _sort_value(x, key_index) < pv]
    mid = [x for x in records if _sort_value(x, key_index) == pv]
    right = [x for x in records if _sort_value(x, key_index) > pv]
    return quick_sort_students(left, key_index) + mid + quick_sort_students(right, key_index)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        database.create_table()
        self._active_scroll_table = None

        self.title("SORTIFY")
        self.geometry("1400x900")
        self.configure(fg_color=BG_MAIN)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_scroll_container()

        self._build_page()
        self._build_content(self.page)

        self._refresh_original_table()
        self._reset_sorted_table()

    def _set_active_scroll_table(self, table):
        self._active_scroll_table = table

    def _clear_active_scroll_table(self, table):
        if self._active_scroll_table is table:
            self._active_scroll_table = None

    # mouse hover = scroll table
    def _bind_table_hover_scroll(self, table: ctk.CTkScrollableFrame):
        table.bind("<Enter>", lambda e: self._set_active_scroll_table(table))
        table.bind("<Leave>", lambda e: self._clear_active_scroll_table(table))

    def _update_scrollbar_visibility(self, table: ctk.CTkScrollableFrame):
        """
        Hide the scrollbar when the content fits; show it only when scrolling is possible.
        CustomTkinter doesn't expose a stable public API for this everywhere, so we do best-effort.
        """
        try:
            self.update_idletasks()
            scrollbar = getattr(table, "_scrollbar", None)
            canvas = getattr(table, "_parent_canvas", None)
            if scrollbar is None or canvas is None:
                return

            start, end = canvas.yview()
            should_show = (start > 0.0) or (end < 1.0)
            if should_show:
                scrollbar.grid()
            else:
                scrollbar.grid_remove()
        except Exception:
            return

    #  Scrollable Container 
    def _build_scroll_container(self):
        container = ctk.CTkFrame(self, fg_color=BG_MAIN)
        container.grid(row=0, column=0, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(container, bg=BG_MAIN, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.page = ctk.CTkFrame(self.canvas, fg_color=BG_MAIN)

        self.page_window = self.canvas.create_window((0, 0), window=self.page, anchor="nw", width=1)

        self.page.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        def on_canvas_configure(e):
            self.canvas.itemconfig(self.page_window, width=e.width)

        self.canvas.bind("<Configure>", on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        delta = -int(event.delta / 120)

        # Mouse Hover = Scroll Table
        table = self._active_scroll_table
        if table is not None:
            try:
                canvas = getattr(table, "_parent_canvas", None)
                if canvas is not None:
                    canvas.yview_scroll(delta, "units")
                    self._update_scrollbar_visibility(table)
                    return
            except Exception:
                pass


        self.canvas.yview_scroll(delta, "units")

    #  Page Layout 
    def _build_page(self):
        self.page.columnconfigure(0, weight=1)
        self.page.columnconfigure(1, weight=8)
        self.page.columnconfigure(2, weight=1)

    def _build_content(self, root: ctk.CTkFrame):
        content = ctk.CTkFrame(root, fg_color=BG_MAIN)
        content.grid(row=0, column=1, sticky="nsew", padx=P, pady=P)

        content.rowconfigure(0, weight=0)
        content.rowconfigure(1, weight=0)
        content.rowconfigure(2, weight=0)
        content.rowconfigure(3, weight=0)
        content.rowconfigure(4, weight=1)
        content.columnconfigure(0, weight=1)

        self._build_header(content)
        self._build_add_student_card(content)
        self._build_control_panel(content)
        self._build_algo_info_card(content)
        self._build_data_sections(content)

    #  Header 
    def _build_header(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=BG_MAIN)
        frame.grid(row=0, column=0, sticky="ew")

        title = ctk.CTkLabel(
            frame,
            text="SORTIFY: Student Record Sorting System",
            font=FONT_H1,
            text_color=TEXT_PRIMARY,
            justify="left",
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            frame,
            text="Compare and analyze the performance of different sorting algorithms on student data.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            justify="left",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(8, 0))

    #  ADD STUDENT 
    def _build_add_student_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=16)
        card.grid(row=1, column=0, sticky="ew", pady=(P, 0))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            card, text="Add Student Record", font=FONT_H2, text_color=TEXT_PRIMARY, justify="left"
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=P, pady=(P, 6))

        # Row 1 labels
        ctk.CTkLabel(card, text="Student ID", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
            row=1, column=0, sticky="w", padx=P, pady=(4, 0)
        )
        ctk.CTkLabel(card, text="Name", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
            row=1, column=1, sticky="w", padx=P, pady=(4, 0)
        )

        # Row 1 entries
        self.entry_id = ctk.CTkEntry(card, placeholder_text="e.g., 0124-0001", font=FONT_BODY, height=44, state="normal")
        self.entry_name = ctk.CTkEntry(card, placeholder_text="e.g., Dela Cruz, Juan", font=FONT_BODY, height=44, state="normal")
        self.entry_id.grid(row=2, column=0, sticky="ew", padx=P, pady=(4, P // 2))
        self.entry_name.grid(row=2, column=1, sticky="ew", padx=P, pady=(4, P // 2))

        # Row 2 labels
        ctk.CTkLabel(card, text="GWA", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
            row=3, column=0, sticky="w", padx=P, pady=(4, 0)
        )
        ctk.CTkLabel(card, text="Age", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
            row=3, column=1, sticky="w", padx=P, pady=(4, 0)
        )

        # Row 2 entries
        self.entry_gwa = ctk.CTkEntry(card, placeholder_text="e.g., 1.75", font=FONT_BODY, height=44, state="normal")
        self.entry_age = ctk.CTkEntry(card, placeholder_text="e.g., 20", font=FONT_BODY, height=44, state="normal")
        self.entry_gwa.grid(row=4, column=0, sticky="ew", padx=P, pady=(4, P // 2))
        self.entry_age.grid(row=4, column=1, sticky="ew", padx=P, pady=(4, P // 2))

        # Row 3 labels
        ctk.CTkLabel(card, text="Program", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
            row=5, column=0, sticky="w", padx=P, pady=(4, 0)
        )
        ctk.CTkLabel(card, text="Enrollment Year", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
            row=5, column=1, sticky="w", padx=P, pady=(4, 0)
        )

        # Row 3 entries
        self.entry_major = ctk.CTkEntry(card, placeholder_text="e.g., BS Computer Science", font=FONT_BODY, height=44, state="normal")
        self.entry_year = ctk.CTkEntry(card, placeholder_text="e.g., 2024", font=FONT_BODY, height=44, state="normal")
        self.entry_major.grid(row=6, column=0, sticky="ew", padx=P, pady=(4, 8))
        self.entry_year.grid(row=6, column=1, sticky="ew", padx=P, pady=(4, 8))

        # Buttons row
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=8, column=0, columnspan=2, sticky="ew", padx=P, pady=(12, P))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        self.btn_add = ctk.CTkButton(
            btn_frame,
            text="✚  Add Student",
            fg_color=PRIMARY_BTN,
            hover_color=PRIMARY_HOVER,
            text_color="white",
            corner_radius=22,
            font=FONT_BODY,
            width=180,
            height=44,
            state="normal",
            command=self._on_add_student,
        )
        self.btn_clear_form = ctk.CTkButton(
            btn_frame,
            text="🗑  Clear Form",
            fg_color=NEUTRAL_BTN,
            hover_color=NEUTRAL_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=22,
            font=FONT_BODY,
            width=180,
            height=44,
            state="normal",
            command=self._on_clear_form,
        )

        self.btn_add.grid(row=0, column=0, sticky="ew", padx=(0, 25))
        self.btn_clear_form.grid(row=0, column=1, sticky="ew", padx=(25, 0))

    #  CONTROL PANEL 
    def _build_control_panel(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=16)
        card.grid(row=2, column=0, sticky="ew", pady=(P, 0))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        title = ctk.CTkLabel(card, text="Control Panel", font=FONT_H2, text_color=TEXT_PRIMARY, justify="left")
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=P, pady=(P, 6))

        # Row 1 labels
        ctk.CTkLabel(card, text="Sorting Algorithm", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
            row=1, column=0, sticky="w", padx=P, pady=(4, 0)
        )
        ctk.CTkLabel(card, text="Sort By", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(
            row=1, column=1, sticky="w", padx=P, pady=(4, 0)
        )

        # Row 2 ComboBoxes
        self.combo_algo = ctk.CTkComboBox(
            card, values=["Quick Sort", "Bubble Sort", "Insertion Sort"], font=FONT_BODY, height=44, state="normal"
        )
        self.combo_algo.set("Quick Sort")

        self.combo_sort_by = ctk.CTkComboBox(
            card, values=["Name", "Student ID", "Age", "GWA", "Enrollment Year"], font=FONT_BODY, height=44, state="normal"
        )
        self.combo_sort_by.set("Name")

        self.combo_algo.grid(row=2, column=0, sticky="ew", padx=P, pady=(4, 8))
        self.combo_sort_by.grid(row=2, column=1, sticky="ew", padx=P, pady=(4, 8))

        # Row 3 Buttons
        self.btn_run = ctk.CTkButton(
            card,
            text="▶︎  Run Sort",
            fg_color=PRIMARY_BTN,
            hover_color=PRIMARY_HOVER,
            text_color="white",
            corner_radius=22,
            font=FONT_BODY,
            width=180,
            height=44,
            state="normal",
            command=self._on_run_sort,
        )
        self.btn_clear_all = ctk.CTkButton(
            card,
            text="🗑  Clear All Data",
            fg_color=NEUTRAL_BTN,
            hover_color=NEUTRAL_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=22,
            font=FONT_BODY,
            width=180,
            height=44,
            state="normal",
            command=self._on_clear_all,
        )

        self.btn_run.grid(row=3, column=0, sticky="ew", padx=P, pady=(12, P))
        self.btn_clear_all.grid(row=3, column=1, sticky="ew", padx=P, pady=(12, P))

        # Row 4 Dataset Label
        self.label_dataset = ctk.CTkLabel(
            card, text="Current Dataset: 0 records", font=FONT_BODY, text_color=TEXT_SECONDARY, justify="left"
        )
        self.label_dataset.grid(row=4, column=0, columnspan=2, sticky="e", padx=P, pady=(0, P))

    #  Algorithm Info 
    def _build_algo_info_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#e5f0ff", corner_radius=16)
        card.grid(row=3, column=0, sticky="ew", pady=(P, 0))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        self.card_height = 240
        card.grid_propagate(True)
        card.configure(height=self.card_height)

        self.label_algo_title = ctk.CTkLabel(card, text="Quick Sort", font=FONT_H2, text_color=TEXT_PRIMARY, justify="left")
        self.label_algo_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=P, pady=(P, 6))

        self.label_algo_desc = ctk.CTkLabel(
            card,
            text="Divide and conquer algorithm that picks a pivot and partitions the array around it.",
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            wraplength=1000,
            justify="left",
        )
        self.label_algo_desc.grid(row=1, column=0, columnspan=2, sticky="w", padx=P, pady=(0, 10))

        time_title = ctk.CTkLabel(card, text="Time Complexity", font=FONT_BODY, text_color=TEXT_PRIMARY, justify="left")
        space_title = ctk.CTkLabel(card, text="Space Complexity", font=FONT_BODY, text_color=TEXT_PRIMARY, justify="left")
        time_title.grid(row=2, column=0, sticky="w", padx=P, pady=(6, 0))
        space_title.grid(row=2, column=1, sticky="w", padx=P, pady=(6, 0))

        self.label_time = ctk.CTkLabel(
            card, text="Best: O(n log n)\nAverage: O(n log n)\nWorst: O(n^2)",
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            justify="left",
        )
        self.label_space = ctk.CTkLabel(
            card, text="Best: O(log n)\nAverage: O(log n)\nWorst: O(n)",
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            justify="left",
        )

        self.label_time.grid(row=3, column=0, sticky="w", padx=P, pady=(0, P))
        self.label_space.grid(row=3, column=1, sticky="w", padx=P, pady=(0, P))

    #  Data Sections 
    def _build_data_sections(self, parent):
        container = ctk.CTkFrame(parent, fg_color=BG_MAIN)
        container.grid(row=4, column=0, sticky="nsew", pady=(P, P))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        container.rowconfigure(3, weight=1)

        self.table_body_height = 440

        self.orig_title = ctk.CTkLabel(
            container, text="Original Data (0 records)", font=FONT_H2, text_color=TEXT_PRIMARY, justify="left"
        )
        self.orig_title.grid(row=0, column=0, sticky="ew", pady=(0, 8), padx=P)

        self.orig_card = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=16)
        self.orig_card.grid(row=1, column=0, sticky="nsew", padx=P)
        self.orig_card.rowconfigure(0, weight=0)
        self.orig_card.rowconfigure(1, weight=1)
        self.orig_card.columnconfigure(0, weight=1)

        # Sticky header
        self.orig_header = ctk.CTkFrame(self.orig_card, fg_color="#e5e7eb", corner_radius=10)
        self.orig_header.grid(row=0, column=0, sticky="ew", padx=P, pady=(P, 8))
        self.orig_header.grid_columnconfigure(0, weight=1)

        # Scrollable body
        self.orig_table = ctk.CTkScrollableFrame(self.orig_card, fg_color=CARD_BG, height=self.table_body_height)
        self.orig_table.grid(row=1, column=0, sticky="nsew", padx=P, pady=(0, P))
        self.orig_table.grid_columnconfigure(0, weight=1)

        self.sorted_title = ctk.CTkLabel(
            container, text="Sorted Data", font=FONT_H2, text_color=TEXT_PRIMARY, justify="left"
        )
        self.sorted_title.grid(row=2, column=0, sticky="ew", pady=(P, 8), padx=P)

        self.sorted_card = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=16)
        self.sorted_card.grid(row=3, column=0, sticky="nsew", padx=P)
        self.sorted_card.rowconfigure(0, weight=0)
        self.sorted_card.rowconfigure(1, weight=1)
        self.sorted_card.columnconfigure(0, weight=1)

        # Sticky header
        self.sorted_header = ctk.CTkFrame(self.sorted_card, fg_color="#e5e7eb", corner_radius=10)
        self.sorted_header.grid(row=0, column=0, sticky="ew", padx=P, pady=(P, 8))
        self.sorted_header.grid_columnconfigure(0, weight=1)

        # Scrollable body
        self.sorted_table = ctk.CTkScrollableFrame(self.sorted_card, fg_color=CARD_BG, height=self.table_body_height)
        self.sorted_table.grid(row=1, column=0, sticky="nsew", padx=P, pady=(0, P))
        self.sorted_table.grid_columnconfigure(0, weight=1)

        self._build_table_header(self.orig_header, with_actions=True)
        self._build_empty_placeholder_row(
            self.orig_table,
            columns=7,
            grid_row=0,
            message="No records yet. Add a student or load from the database.",
        )

        self._build_table_header(self.sorted_header, with_actions=False)
        self._build_empty_placeholder_row(
            self.sorted_table,
            columns=7,
            grid_row=0,
            show_action_blank=True,
            message="Run sort to see ordered results.",
        )

        self._bind_table_hover_scroll(self.orig_table)
        self._bind_table_hover_scroll(self.sorted_table)

        self._update_scrollbar_visibility(self.orig_table)
        self._update_scrollbar_visibility(self.sorted_table)

    def _build_table_header(self, parent, with_actions: bool):
        header = parent
        for w in header.winfo_children():
            w.destroy()

        for i, w in enumerate(COL_W):
            header.columnconfigure(i, weight=w)

        labels = ["Student ID", "Name", "Age", "GWA", "Program", "Year"]
        for col, text in enumerate(labels):
            ctk.CTkLabel(header, text=text, font=FONT_BODY, text_color=TEXT_PRIMARY, justify="left").grid(
                row=0, column=col, padx=8, pady=8, sticky="w"
            )

        if with_actions:
            ctk.CTkLabel(header, text="Actions", font=FONT_BODY, text_color=TEXT_PRIMARY, justify="left").grid(
                row=0, column=6, padx=8, pady=8, sticky="e"
            )
        else:
            ctk.CTkLabel(header, text="", font=FONT_BODY, text_color=TEXT_PRIMARY, justify="left").grid(
                row=0, column=6, padx=8, pady=8, sticky="e"
            )

    def _build_empty_placeholder_row(
        self,
        parent,
        columns: int,
        grid_row: int = 0,
        show_action_blank: bool = False,
        message: str = "No records yet.",
    ):
        row = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=0)
        row.grid(row=grid_row, column=0, sticky="ew", pady=4)

        for i in range(columns):
            row.columnconfigure(i, weight=COL_W[i])

        label = ctk.CTkLabel(
            row,
            text=message,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            justify="left",
        )
        label.grid(row=0, column=0, columnspan=6, padx=8, pady=8, sticky="ew")

        if show_action_blank:
            ctk.CTkLabel(row, text="", font=FONT_BODY, text_color=TEXT_SECONDARY, justify="left").grid(
                row=0, column=6, padx=8, pady=8, sticky="e"
            )

    def _update_dataset_labels(self, count: int):
        self.label_dataset.configure(text=f"Current Dataset: {count} records")
        self.orig_title.configure(text=f"Original Data ({count} records)")

    def _clear_table_widgets(self, table: ctk.CTkScrollableFrame):
        for w in table.winfo_children():
            w.destroy()

    def _refresh_original_table(self):
        self._clear_table_widgets(self.orig_table)
        students = database.get_all_students()
        n = len(students)
        self._update_dataset_labels(n)
        if n == 0:
            self._build_empty_placeholder_row(
                self.orig_table,
                columns=7,
                grid_row=0,
                message="No records yet. Add a student or load from the database.",
            )
            self._update_scrollbar_visibility(self.orig_table)
            return
        for i, row_data in enumerate(students):
            self._build_data_row(self.orig_table, row_data, grid_row=i, with_delete=True)
        self._update_scrollbar_visibility(self.orig_table)

    def _reset_sorted_table(self):
        self._clear_table_widgets(self.sorted_table)
        self._build_empty_placeholder_row(
            self.sorted_table,
            columns=7,
            grid_row=0,
            show_action_blank=True,
            message="Run sort to see ordered results.",
        )
        self._update_scrollbar_visibility(self.sorted_table)

    def _show_sorted_rows(self, rows):
        self._clear_table_widgets(self.sorted_table)
        if not rows:
            self._build_empty_placeholder_row(
                self.sorted_table,
                columns=7,
                grid_row=0,
                show_action_blank=True,
                message="No records to display.",
            )
            self._update_scrollbar_visibility(self.sorted_table)
            return
        for i, row_data in enumerate(rows):
            self._build_data_row(self.sorted_table, row_data, grid_row=i, with_delete=False)
        self._update_scrollbar_visibility(self.sorted_table)

    def _build_data_row(self, parent, data: tuple, grid_row: int, with_delete: bool):
        row = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=0)
        row.grid(row=grid_row, column=0, sticky="ew", pady=4)

        for i in range(7):
            row.columnconfigure(i, weight=COL_W[i])

        sid, name, age, gwa, program, year = data
        cells = [sid, name, str(age), f"{float(gwa):.2f}", program, str(year)]
        for col, text in enumerate(cells):
            ctk.CTkLabel(row, text=text, font=FONT_SMALL, text_color=TEXT_PRIMARY, justify="left").grid(
                row=0, column=col, padx=8, pady=8, sticky="w"
            )

        if with_delete:
            student_id = sid

            def do_delete():
                self._on_delete_student(student_id)

            ctk.CTkButton(
                row,
                text="Delete",
                width=72,
                height=32,
                corner_radius=10,
                fg_color="#fecaca",
                hover_color="#f87171",
                text_color="#7f1d1d",
                font=FONT_SMALL,
                command=do_delete,
            ).grid(row=0, column=6, padx=8, pady=4, sticky="e")
        else:
            ctk.CTkLabel(row, text="", font=FONT_SMALL, text_color=TEXT_PRIMARY, justify="left").grid(
                row=0, column=6, padx=8, pady=8, sticky="e"
            )

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

        # Require name as "Surname, Firstname"
        if "," not in name:
            messagebox.showerror("Validation", 'Name must be in the format "Surname, Firstname".')
            return
        surname, firstname = [p.strip() for p in name.split(",", 1)]
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

        data = (sid, name, age, gwa, program, year)
        database.add_student(data)
        self._refresh_original_table()
        self._reset_sorted_table()
        self._on_clear_form()

    def _on_clear_form(self):
        for e in (self.entry_id, self.entry_name, self.entry_gwa, self.entry_age, self.entry_major, self.entry_year):
            e.delete(0, "end")

    def _on_delete_student(self, student_id: str):
        database.delete_student(student_id)
        self._refresh_original_table()
        self._reset_sorted_table()

    def _on_clear_all(self):
        if not messagebox.askyesno("Clear all", "Remove every student record from the database?"):
            return
        database.delete_all_students()
        self._refresh_original_table()
        self._reset_sorted_table()

    def _on_run_sort(self):
        records = database.get_all_students()
        if not records:
            messagebox.showinfo("Sort", "No records to sort.")
            self._reset_sorted_table()
            return

        sort_by = self.combo_sort_by.get()
        key_index = SORT_KEY_BY_COLUMN[sort_by]
        algo = self.combo_algo.get()

        if algo == "Quick Sort":
            sorted_rows = quick_sort_students(records, key_index)
        elif algo == "Bubble Sort":
            sorted_rows = bubble_sort_students(records, key_index)
        else:
            sorted_rows = insertion_sort_students(records, key_index)

        self._show_sorted_rows(sorted_rows)


if __name__ == "__main__":
    app = App()
    app.mainloop()