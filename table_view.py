import customtkinter as ctk
from constants import (
    CARD_BG, TABLE_HEADER_BG, TEXT_PRIMARY, TEXT_SECONDARY,
    FONT_H2, FONT_BODY, FONT_SMALL,
    P, ROW_HEIGHT, NEUTRAL_BTN, NEUTRAL_HOVER,
    DANGER_BTN, DANGER_HOVER, DANGER_TEXT,
)

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
        visible_rows=10,
        show_scrollbar=True,
        actions_align="w",
        always_show_scrollbar=False,
    ):
        if col_weights is None:
            from constants import COL_WEIGHTS_NO_ACTION as cw
            col_weights = cw
        self.app = app
        self.show_actions = show_actions
        self.action_mode = action_mode
        self.include_actions_header = include_actions_header
        self.col_weights = col_weights
        self.show_scrollbar = show_scrollbar
        self.actions_align = actions_align
        self.always_show_scrollbar = always_show_scrollbar

        self.table_height = ROW_HEIGHT * visible_rows + 18

        self.title_label = ctk.CTkLabel(parent, text=title, font=FONT_H2, text_color=TEXT_PRIMARY)
        self.title_label.pack(anchor="w", pady=(0, 4))

        self.card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
        self.card.pack(fill="x")

        self.header = ctk.CTkFrame(self.card, fg_color=TABLE_HEADER_BG, corner_radius=0)
        self.header.pack(fill="x", padx=P, pady=(P, 6))

        self.table = ctk.CTkScrollableFrame(self.card, fg_color=CARD_BG, height=self.table_height)
        self.table.pack(fill="x", padx=P, pady=(0, P))
        self.table.grid_columnconfigure(0, weight=1)

        # ---- make the scrollable frame work like a TableView for scrolling ----
        self.table.is_scrollable = self.is_scrollable
        self.table._update_scrollbar_visibility = self._update_scrollbar_visibility

        self._draw_header()
        self._schedule_header_alignment()
        self._force_inner_width()
        self.app._bind_table_hover_scroll(self.table)

    def is_scrollable(self):
        if not self.show_scrollbar:
            return False
        try:
            canvas = self.table._parent_canvas
            bbox = canvas.bbox("all")
            if bbox:
                content_height = bbox[3] - bbox[1]
                return content_height > canvas.winfo_height()
        except Exception:
            pass
        return False

    def _force_inner_width(self):
        def set_width():
            try:
                canvas = self.table._parent_canvas
                inner = canvas.find_withtag("inner_frame")
                if inner:
                    canvas.itemconfigure(inner, width=canvas.winfo_width())
            except Exception:
                pass
        self.app.after(10, set_width)

    def _update_scrollbar_visibility(self):
        try:
            self.app.update_idletasks()
            scrollbar = getattr(self.table, "_scrollbar", None)
            canvas = getattr(self.table, "_parent_canvas", None)
            if not scrollbar or not canvas:
                return

            if self.always_show_scrollbar:
                scrollbar.grid()
                self._sync_header_padding(True)
                return

            start, end = canvas.yview()
            visible = start > 0.0 or end < 1.0
            if self.show_scrollbar and visible:
                scrollbar.grid()
            else:
                scrollbar.grid_remove()
            self._sync_header_padding(visible if self.show_scrollbar else False)
        except Exception:
            pass

    def _sync_header_padding(self, scrollbar_visible):
        if scrollbar_visible:
            try:
                sb_width = self.table._scrollbar.winfo_reqwidth()
            except Exception:
                sb_width = 12
            self._scrollbar_spacer.configure(width=sb_width)
        else:
            self._scrollbar_spacer.configure(width=0)

    def _schedule_header_alignment(self):
        self.app.after(15, self._update_scrollbar_visibility)
        self.app.after(50, self._force_inner_width)

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
                row=0, column=6, sticky=self.actions_align, padx=6, pady=6
            )

        self._scrollbar_spacer = ctk.CTkFrame(self.header, width=0, height=1, fg_color="transparent")
        self._scrollbar_spacer.grid(row=0, column=99, sticky="ns")

    def set_visible_rows(self, visible_rows):
        self.table_height = ROW_HEIGHT * visible_rows + 18
        self.table.configure(height=self.table_height)
        self._schedule_header_alignment()

    def set_title(self, text):
        self.title_label.configure(text=text)

    def _cell_sticky(self, col_idx):
        if col_idx == 6 and self.show_actions:
            return self.actions_align
        return "w"

    def _configure_columns(self, widget):
        for i, weight in enumerate(self.col_weights):
            widget.columnconfigure(i, weight=weight, uniform="table_cols")
        widget.columnconfigure(len(self.col_weights), weight=0)

    def _clear(self):
        for w in self.table.winfo_children():
            w.destroy()

    def _placeholder(self, text):
        row = ctk.CTkFrame(self.table, fg_color=CARD_BG)
        row.pack(fill="x", pady=2)
        self._configure_columns(row)
        span = len(self.col_weights)
        ctk.CTkLabel(row, text=text, font=FONT_BODY, text_color=TEXT_SECONDARY).grid(
            row=0, column=0, columnspan=span, sticky="w", padx=6, pady=6
        )

    def _render_row(self, data, row_idx, archived_rowid=None):
        row = ctk.CTkFrame(self.table, fg_color=CARD_BG)
        row.pack(fill="x", pady=1)
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
            box.grid(row=0, column=6, sticky=self.actions_align, padx=6)
            if self.action_mode == "archive":
                ctk.CTkButton(
                    box, text="Archive", width=40, height=28,
                    fg_color=NEUTRAL_BTN, hover_color=NEUTRAL_HOVER,
                    text_color=TEXT_PRIMARY,
                    command=lambda s=sid: self.app._on_archive_student(s),
                ).grid(row=0, column=0)
            elif self.action_mode == "delete_archived":
                ctk.CTkButton(
                    box, text="Restore", width=72, height=28,
                    fg_color=NEUTRAL_BTN, hover_color=NEUTRAL_HOVER,
                    text_color=TEXT_PRIMARY,
                    command=lambda r=archived_rowid: self.app._on_restore_archived(r),
                ).grid(row=0, column=0, padx=(0, 4))
                ctk.CTkButton(
                    box, text="Delete", width=70, height=28,
                    fg_color=DANGER_BTN, hover_color=DANGER_HOVER,
                    text_color=DANGER_TEXT,
                    command=lambda r=archived_rowid: self.app._on_delete_archived(r),
                ).grid(row=0, column=1)

    def render_rows(self, rows, placeholder, archived=False):
        self._clear()
        if not rows:
            self._placeholder(placeholder)
            self._update_scrollbar_visibility()
            return

        for i, row in enumerate(rows):
            if archived:
                archive_rowid = row[0]
                payload = row[1:]
                self._render_row(payload, i, archived_rowid=archive_rowid)
            else:
                self._render_row(row, i)

        self._update_scrollbar_visibility()
        self._force_inner_width()