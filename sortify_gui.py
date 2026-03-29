import customtkinter as ctk
import tkinter as tk

# ---------------- THEME ----------------

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


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SORTIFY")
        self.geometry("1400x900")
        self.configure(fg_color=BG_MAIN)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_scroll_container()

        # build UI
        self._build_page()
        self._build_content(self.page)

    # ---------- scrollable root ----------
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

        # keep page width synced to canvas width
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
        self.canvas.yview_scroll(-int(event.delta / 120), "units")

    # ---------- page layout ----------
    def _build_page(self):
        # centered middle column
        self.page.columnconfigure(0, weight=1)
        self.page.columnconfigure(1, weight=8)
        self.page.columnconfigure(2, weight=1)

    def _build_content(self, root: ctk.CTkFrame):
        content = ctk.CTkFrame(root, fg_color=BG_MAIN)
        content.grid(row=0, column=1, sticky="nsew", padx=P, pady=P)

        # allow vertical expansion
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

    # ---------- header ----------
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

    # ---------- ADD STUDENT ----------
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
        self.entry_name = ctk.CTkEntry(card, placeholder_text="e.g., Juan Dela Cruz", font=FONT_BODY, height=44, state="normal")
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

        btn_add = ctk.CTkButton(
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
        )
        btn_clear = ctk.CTkButton(
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
        )

        btn_add.grid(row=0, column=0, sticky="ew", padx=(0, 25))
        btn_clear.grid(row=0, column=1, sticky="ew", padx=(25, 0))

    # ---------- CONTROL PANEL ----------
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

        # Row 2 comboboxes
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

        # Row 3 buttons
        btn_run = ctk.CTkButton(
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
        )
        btn_clear = ctk.CTkButton(
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
        )

        btn_run.grid(row=3, column=0, sticky="ew", padx=P, pady=(12, P))
        btn_clear.grid(row=3, column=1, sticky="ew", padx=P, pady=(12, P))

        # Row 4 dataset label
        self.label_dataset = ctk.CTkLabel(
            card, text="Current Dataset: 0 records", font=FONT_BODY, text_color=TEXT_SECONDARY, justify="left"
        )
        self.label_dataset.grid(row=4, column=0, columnspan=2, sticky="e", padx=P, pady=(0, P))

    # ---------- algorithm info card ----------
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

    # ---------- data sections ----------
    def _build_data_sections(self, parent):
        container = ctk.CTkFrame(parent, fg_color=BG_MAIN)
        container.grid(row=4, column=0, sticky="nsew", pady=(P, P))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        container.rowconfigure(3, weight=1)

        self.orig_title = ctk.CTkLabel(
            container, text="Original Data (0 records)", font=FONT_H2, text_color=TEXT_PRIMARY, justify="left"
        )
        self.orig_title.grid(row=0, column=0, sticky="ew", pady=(0, 8), padx=P)

        self.orig_card = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=16)
        self.orig_card.grid(row=1, column=0, sticky="nsew", padx=P)
        self.orig_card.rowconfigure(0, weight=1)
        self.orig_card.columnconfigure(0, weight=1)

        self.orig_table = ctk.CTkScrollableFrame(self.orig_card, fg_color=CARD_BG)
        self.orig_table.grid(row=0, column=0, sticky="nsew", padx=P, pady=P)
        self.orig_table.grid_columnconfigure(0, weight=1)

        self.sorted_title = ctk.CTkLabel(
            container, text="Sorted Data", font=FONT_H2, text_color=TEXT_PRIMARY, justify="left"
        )
        self.sorted_title.grid(row=2, column=0, sticky="ew", pady=(P, 8), padx=P)

        self.sorted_card = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=16)
        self.sorted_card.grid(row=3, column=0, sticky="nsew", padx=P)
        self.sorted_card.rowconfigure(0, weight=1)
        self.sorted_card.columnconfigure(0, weight=1)

        self.sorted_table = ctk.CTkScrollableFrame(self.sorted_card, fg_color=CARD_BG)
        self.sorted_table.grid(row=0, column=0, sticky="nsew", padx=P, pady=P)
        self.sorted_table.grid_columnconfigure(0, weight=1)

        # headers + placeholder rows
        self._build_table_header(self.orig_table, with_actions=True)
        self._build_empty_placeholder_row(self.orig_table, columns=7)

        self._build_table_header(self.sorted_table, with_actions=False)
        self._build_empty_placeholder_row(self.sorted_table, columns=7, show_action_blank=True)

    def _build_table_header(self, parent, with_actions: bool):
        header = ctk.CTkFrame(parent, fg_color="#e5e7eb", corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        for i, w in enumerate(COL_W):
            header.columnconfigure(i, weight=w)

        labels = ["Student ID", "Name", "Age", "GWA", "Program", "Year"]
        for col, text in enumerate(labels):
            ctk.CTkLabel(header, text=text, font=FONT_BODY, text_color=TEXT_PRIMARY, justify="left").grid(
                row=0, column=col, padx=8, pady=8, sticky="w"
            )

        # action column header
        if with_actions:
            ctk.CTkLabel(header, text="Actions", font=FONT_BODY, text_color=TEXT_PRIMARY, justify="left").grid(
                row=0, column=6, padx=8, pady=8, sticky="e"
            )
        else:
            ctk.CTkLabel(header, text="", font=FONT_BODY, text_color=TEXT_PRIMARY, justify="left").grid(
                row=0, column=6, padx=8, pady=8, sticky="e"
            )

    def _build_empty_placeholder_row(self, parent, columns: int, show_action_blank: bool = False):
        row = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=0)
        row.grid(row=1, column=0, sticky="ew", pady=4)

        for i in range(columns):
            row.columnconfigure(i, weight=COL_W[i])

        label = ctk.CTkLabel(
            row,
            text="No records yet.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            justify="left",
        )
        label.grid(row=0, column=0, columnspan=6, padx=8, pady=8, sticky="ew")

        if show_action_blank:
            ctk.CTkLabel(row, text="", font=FONT_BODY, text_color=TEXT_SECONDARY, justify="left").grid(
                row=0, column=6, padx=8, pady=8, sticky="e"
            )


if __name__ == "__main__":
    app = App()
    app.mainloop()