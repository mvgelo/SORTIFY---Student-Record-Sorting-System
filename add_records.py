import customtkinter as ctk
from tkinter import messagebox
from constants import (
    BG_MAIN, CARD_BG, TEXT_PRIMARY,
    FONT_H1, FONT_BODY, BTN_H, P,
    PRIMARY_BTN, PRIMARY_HOVER,
    NEUTRAL_BTN, NEUTRAL_HOVER,
)
from table_view import TableView
import sortify_database as database

class AddRecordsMixin:
    def _build_add_page(self):
        page = ctk.CTkFrame(self.main, fg_color=BG_MAIN)
        page.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(page, text="Add Records", font=FONT_H1, text_color=TEXT_PRIMARY).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

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
        self.entry_major = ctk.CTkEntry(form, height=36, placeholder_text="e.g., BS Computer Science")
        self.entry_year = ctk.CTkEntry(form, height=36, placeholder_text="e.g., 2024")
        self.entry_major.grid(row=5, column=0, sticky="ew", padx=P, pady=(0, 8))
        self.entry_year.grid(row=5, column=1, sticky="ew", padx=P, pady=(0, 8))

        btn_box = ctk.CTkFrame(form, fg_color="transparent")
        btn_box.grid(row=6, column=0, columnspan=2, sticky="w", padx=P, pady=(0, 8))
        ctk.CTkButton(btn_box, text="Add Student", height=BTN_H, width=140,
                      fg_color=PRIMARY_BTN, hover_color=PRIMARY_HOVER,
                      command=self._on_add_student).grid(row=0, column=0, sticky="w", padx=(0, 6))
        ctk.CTkButton(btn_box, text="Clear Form", height=BTN_H, width=140,
                      fg_color=NEUTRAL_BTN, hover_color=NEUTRAL_HOVER,
                      text_color=TEXT_PRIMARY,
                      command=self._on_clear_form).grid(row=0, column=1, sticky="w", padx=(6, 0))

        preview_wrap = ctk.CTkFrame(page, fg_color=BG_MAIN)
        preview_wrap.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.add_preview = TableView(
            self, preview_wrap, title="Latest Records Preview",
            show_actions=False, visible_rows=5,
            show_scrollbar=False,
        )
        return page

    def _refresh_add_page(self, active_rows):
        self.add_preview.render_rows(active_rows[:5], "No records yet.")

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