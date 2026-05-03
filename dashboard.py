import customtkinter as ctk
from constants import (
    BG_MAIN, CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY,
    PRIMARY_BTN, FONT_H1, FONT_BODY, FONT_SMALL,
)
from table_view import TableView
import sortify_database as database

class DashboardMixin:
    def _build_dashboard_page(self):
        page = ctk.CTkFrame(self.main, fg_color=BG_MAIN)
        page.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(page, text="Dashboard", font=FONT_H1, text_color=TEXT_PRIMARY).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self.card_total = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=10)
        self.card_total.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        self.card_archive = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=10)
        self.card_archive.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

        ctk.CTkLabel(self.card_total, text="Active Records", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(
            anchor="w", padx=10, pady=(8, 0))
        self.dashboard_active = ctk.CTkLabel(self.card_total, text="0",
                                             font=("Segoe UI Variable", 30, "bold"),
                                             text_color=PRIMARY_BTN)
        self.dashboard_active.pack(anchor="w", padx=10, pady=(0, 8))

        ctk.CTkLabel(self.card_archive, text="Archived Records", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(
            anchor="w", padx=10, pady=(8, 0))
        self.dashboard_archived = ctk.CTkLabel(self.card_archive, text="0",
                                               font=("Segoe UI Variable", 30, "bold"),
                                               text_color="#64748b")
        self.dashboard_archived.pack(anchor="w", padx=10, pady=(0, 8))

        charts_wrap = ctk.CTkFrame(page, fg_color=BG_MAIN)
        charts_wrap.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        charts_wrap.grid_columnconfigure((0, 1, 2), weight=1)

        program_card = ctk.CTkFrame(charts_wrap, fg_color=CARD_BG, corner_radius=10)
        program_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(program_card, text="Program", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(
            anchor="w", padx=10, pady=(8, 4))
        self.program_chart_frame = ctk.CTkFrame(program_card, fg_color="transparent")
        self.program_chart_frame.pack(fill="x", padx=10, pady=(0, 10))

        age_card = ctk.CTkFrame(charts_wrap, fg_color=CARD_BG, corner_radius=10)
        age_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(age_card, text="Age", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(
            anchor="w", padx=10, pady=(8, 4))
        self.age_chart_frame = ctk.CTkFrame(age_card, fg_color="transparent")
        self.age_chart_frame.pack(fill="x", padx=10, pady=(0, 10))

        year_card = ctk.CTkFrame(charts_wrap, fg_color=CARD_BG, corner_radius=10)
        year_card.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(year_card, text="Enrollment Year", font=FONT_BODY, text_color=TEXT_SECONDARY).pack(
            anchor="w", padx=10, pady=(8, 4))
        self.year_chart_frame = ctk.CTkFrame(year_card, fg_color="transparent")
        self.year_chart_frame.pack(fill="x", padx=10, pady=(0, 10))

        preview_wrap = ctk.CTkFrame(page, fg_color=BG_MAIN)
        preview_wrap.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.dashboard_preview = TableView(
            self, preview_wrap, title="Latest Records",
            show_actions=False,
            visible_rows=5,
)

        return page

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