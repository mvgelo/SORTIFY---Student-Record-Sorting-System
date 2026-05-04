import customtkinter as ctk
from constants import (
    BG_MAIN, BG_SIDEBAR, TEXT_PRIMARY, TEXT_SECONDARY,
    FONT_SMALL, BTN_H, P,
    PRIMARY_BTN, NEUTRAL_HOVER,
)
import sortify_database as database

from dashboard import DashboardMixin
from add_records import AddRecordsMixin
from sorting_lab import SortingLabMixin
from algorithm_comparison import AlgorithmComparisonMixin
from dataset import DatasetMixin

class App(ctk.CTk,
          DashboardMixin,
          AddRecordsMixin,
          SortingLabMixin,
          AlgorithmComparisonMixin,
          DatasetMixin):
    def __init__(self):
        super().__init__()
        database.create_table()

        self.title("SORTIFY")
        width = int(800 * 1.2)
        height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
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
        self.after(50, lambda: self.sorted_table.set_visible_rows(2))

        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0, width=230)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="SORTIFY", font=("Segoe UI Variable", 30, "bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, padx=20, pady=(18, 0), sticky="w")
        ctk.CTkLabel(sidebar, text="Student Record Sorting System", font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        names = ["Dashboard", "Add Records", "Sorting Lab", "Algorithm Comparison", "Dataset"]
        for i, name in enumerate(names, start=2):
            btn = ctk.CTkButton(
                sidebar, text=name, height=BTN_H,
                fg_color="transparent", hover_color=NEUTRAL_HOVER,
                text_color=TEXT_PRIMARY, anchor="w", font=FONT_SMALL,
                command=lambda n=name: self._show_page(n),
            )
            btn.grid(row=i, column=0, sticky="ew", padx=12, pady=3)
            self.nav_buttons[name] = btn

        self.dark_mode_var = ctk.StringVar(value="off")
        ctk.CTkSwitch(
            sidebar, text="Dark Mode", variable=self.dark_mode_var,
            onvalue="on", offvalue="off", command=self._toggle_dark_mode,
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
            btn.configure(
                fg_color=PRIMARY_BTN if n == name else "transparent",
                text_color="white" if n == name else TEXT_PRIMARY,
            )
        if name == "Sorting Lab" and not self.has_sorted_results:
            self.sorted_table.set_visible_rows(2)
        self._update_main_scrollbar_visibility()

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

    def _refresh_all_views(self, reset_sorted=False, sorted_rows=None):
        active_rows = database.get_all_students()
        archived_rows = database.get_archived_students()

        self._refresh_dashboard(active_rows, archived_rows)
        self._refresh_add_page(active_rows)
        self._refresh_sorting_page(active_rows, reset_sorted=reset_sorted, sorted_rows=sorted_rows)
        self._refresh_dataset_page(active_rows, archived_rows)
        self._update_main_scrollbar_visibility()


if __name__ == "__main__":
    app = App()
    app.mainloop()