import customtkinter as ctk
from tkinter import messagebox
from constants import (
    BG_MAIN, CARD_BG, TEXT_PRIMARY,
    FONT_H1, FONT_H2, BTN_H, P,
    DANGER_BTN, DANGER_HOVER, DANGER_TEXT,
    PRIMARY_BTN, PRIMARY_HOVER,
    COL_WEIGHTS_WITH_ACTION,
    COL_WEIGHTS_ARCHIVED,
)
from table_view import TableView
import sortify_database as database

class DatasetMixin:
    def _build_dataset_page(self):
        page = ctk.CTkFrame(self.main, fg_color=BG_MAIN)
        ctk.CTkLabel(page, text="Dataset", font=FONT_H1, text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        tables = ctk.CTkFrame(page, fg_color=BG_MAIN)
        tables.pack(fill="x")

        self.dataset_active_table = TableView(
            self, tables, title="Active Dataset",
            show_actions=True, action_mode="archive",
            col_weights=COL_WEIGHTS_WITH_ACTION,
            actions_align="e",
        )

        archived_toggle = ctk.CTkFrame(tables, fg_color="transparent")
        archived_toggle.pack(fill="x", pady=(10, 0))
        self.btn_toggle_archived = ctk.CTkButton(
            archived_toggle, text="Show Archived Dataset", height=BTN_H,
            fg_color=PRIMARY_BTN, hover_color=PRIMARY_HOVER,
            command=self._toggle_archived_section,
        )
        self.btn_toggle_archived.pack(anchor="w")

        self.archived_section = ctk.CTkFrame(tables, fg_color=BG_MAIN)
        self.archived_visible = False

        archive_header = ctk.CTkFrame(self.archived_section, fg_color="transparent")
        archive_header.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(archive_header, text="Archived Dataset", font=FONT_H2, text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(
            archive_header, text="Permanently Delete All Archived", height=BTN_H,
            fg_color=DANGER_BTN, hover_color=DANGER_HOVER, text_color=DANGER_TEXT,
            command=self._on_delete_all_archived,
        ).pack(side="right")

        self.dataset_archived_table = TableView(
            self, self.archived_section, title="",
            show_actions=True, action_mode="delete_archived",
            col_weights=COL_WEIGHTS_ARCHIVED,
            actions_align="e",
            always_show_scrollbar=True,
        )
        self.dataset_archived_table.title_label.pack_forget()
        return page

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