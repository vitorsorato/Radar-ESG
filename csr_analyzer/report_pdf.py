from __future__ import annotations

import os
import unicodedata
from typing import Optional, Tuple

import pandas as pd
from fpdf import FPDF


def _insert_soft_breaks(text: str, max_run: int = 60) -> str:
    """Insert spaces into very long sequences without whitespace to help PDF wrapping.

    This prevents fpdf2 from raising "Not enough horizontal space to render a single character".
    """
    if max_run <= 0:
        return text
    out: list[str] = []
    run = 0
    for ch in text:
        if ch.isspace():
            run = 0
            out.append(ch)
            continue
        run += 1
        out.append(ch)
        if run >= max_run:
            out.append(" ")
            run = 0
    return "".join(out)


def _safe_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    # Replace common unsupported punctuation with ASCII equivalents
    replacements = {
        "\u2022": "-",  # bullet
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u201C": '"',  # left double quote
        "\u201D": '"',  # right double quote
        "\u00A0": " ",  # non-breaking space
        "\u2026": "...",  # ellipsis
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Normalize to NFKC then strip characters not representable in latin-1
    text = unicodedata.normalize("NFKC", text)
    text = text.encode("latin-1", errors="ignore").decode("latin-1", errors="ignore")
    # Insert soft breaks for very long tokens (e.g., URLs)
    text = _insert_soft_breaks(text, max_run=60)
    return text


class AnalysisPDF:
    def __init__(self, title: str = "Análise de Notícias e Relatórios") -> None:
        self.title = title
        self.pdf = FPDF(format="A4")
        self.pdf.set_auto_page_break(auto=True, margin=15)
        # Colors (RGB)
        self.theme_primary: Tuple[int, int, int] = (33, 150, 243)
        self.color_text: Tuple[int, int, int] = (33, 33, 33)
        self.color_pos: Tuple[int, int, int] = (46, 125, 50)
        self.color_neg: Tuple[int, int, int] = (198, 40, 40)
        self.color_neu: Tuple[int, int, int] = (117, 117, 117)
        self.color_muted: Tuple[int, int, int] = (158, 158, 158)
        self.bg_soft: Tuple[int, int, int] = (245, 247, 250)

    def _header(self) -> None:
        # Colored title bar
        left = self.pdf.l_margin
        right = self.pdf.w - self.pdf.r_margin
        bar_height = 12
        self.pdf.set_fill_color(*self.theme_primary)
        self.pdf.rect(left, 12, right - left, bar_height, style="F")
        self.pdf.set_xy(left + 2, 12.5)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font("Helvetica", "B", 16)
        self.pdf.cell(0, 10, _safe_text(self.title), ln=True)
        # Reset text color and add small spacing
        self.pdf.set_text_color(*self.color_text)
        self.pdf.ln(3)

    def _section_title(self, text: str) -> None:
        self.pdf.set_font("Helvetica", "B", 12)
        self.pdf.set_text_color(*self.color_text)
        self.pdf.cell(0, 8, _safe_text(text), ln=True)

    def _body_text(self, text: str) -> None:
        self.pdf.set_font("Helvetica", "", 11)
        # Ensure we start at left margin to avoid narrow remaining width
        self.pdf.set_x(self.pdf.l_margin)
        self.pdf.multi_cell(0, 6, _safe_text(text), align="L")

    def _sentiment_color(self, label: str) -> Tuple[int, int, int]:
        lbl = (label or "").strip().lower()
        if lbl == "positive":
            return self.color_pos
        if lbl == "negative":
            return self.color_neg
        return self.color_neu

    def _progress_bar(self, fraction: float, height: float = 4.0, color: Tuple[int, int, int] | None = None) -> None:
        color = color or self.theme_primary
        left = self.pdf.l_margin
        right = self.pdf.w - self.pdf.r_margin
        full_width = right - left
        width = max(0.0, min(1.0, float(fraction))) * full_width
        y = self.pdf.get_y() + 1.0
        self.pdf.set_fill_color(230, 230, 230)
        self.pdf.rect(left, y, full_width, height, style="F")
        self.pdf.set_fill_color(*color)
        self.pdf.rect(left, y, width, height, style="F")
        self.pdf.ln(height + 2)

    def _meta_line(self, parts: list[str]) -> None:
        self.pdf.set_font("Helvetica", "", 10)
        self.pdf.set_text_color(*self.color_muted)
        self._body_text(" | ".join(_safe_text(p) for p in parts))
        self.pdf.set_text_color(*self.color_text)

    def _divider(self) -> None:
        left = self.pdf.l_margin
        right = self.pdf.w - self.pdf.r_margin
        y = self.pdf.get_y() + 1
        self.pdf.set_draw_color(230, 230, 230)
        self.pdf.set_line_width(0.2)
        self.pdf.line(left, y, right, y)
        self.pdf.ln(2)

    def add_summary(self, df: pd.DataFrame, kind: str) -> None:
        self.pdf.add_page()
        self._header()
        self._section_title(f"Resumo - {kind}")
        total = len(df)
        pos = (df["sentiment_label"] == "positive").sum() if "sentiment_label" in df.columns else 0
        neg = (df["sentiment_label"] == "negative").sum() if "sentiment_label" in df.columns else 0
        neu = (df["sentiment_label"] == "neutral").sum() if "sentiment_label" in df.columns else 0
        # KPI line
        self._meta_line([
            f"Total: {total}",
            f"Positivas: {pos}",
            f"Negativas: {neg}",
            f"Neutras: {neu}",
        ])
        # Distribution bar
        if total > 0:
            self._body_text("Distribuição de sentimentos")
            # stacked bar
            left = self.pdf.l_margin
            right = self.pdf.w - self.pdf.r_margin
            full_width = right - left
            y = self.pdf.get_y() + 1.0
            # background
            self.pdf.set_fill_color(230, 230, 230)
            self.pdf.rect(left, y, full_width, 6, style="F")
            # segments
            acc = 0.0
            for value, color in (
                (neg, self.color_neg),
                (neu, self.color_neu),
                (pos, self.color_pos),
            ):
                if value <= 0:
                    continue
                w = full_width * (float(value) / float(total))
                self.pdf.set_fill_color(*color)
                self.pdf.rect(left + acc, y, w, 6, style="F")
                acc += w
            self.pdf.ln(10)
        self._divider()

    def add_items(self, df: pd.DataFrame, title_col: str, text_col: str, meta_cols: Optional[list[str]] = None, limit: int = 20) -> None:
        meta_cols = meta_cols or []
        self.pdf.add_page()
        self._section_title("Itens (amostra)")
        sample = df.head(limit)
        for idx, row in sample.iterrows():
            title = str(row.get(title_col, ""))
            # Title
            self._section_title(f"- {title[:120]}")
            # Meta line
            meta_parts = []
            for col in meta_cols:
                val = row.get(col)
                if pd.notna(val):
                    meta_parts.append(f"{col}: {val}")
            # sentiment colored hint
            sent_label = str(row.get("sentiment_label", "")).strip()
            if sent_label:
                color = self._sentiment_color(sent_label)
                meta_parts.append(f"sentiment: {sent_label}")
            if meta_parts:
                if sent_label:
                    self.pdf.set_text_color(*self._sentiment_color(sent_label))
                    self._meta_line(meta_parts)
                    self.pdf.set_text_color(*self.color_text)
                else:
                    self._meta_line(meta_parts)
            text = str(row.get(text_col, ""))
            self._body_text(text[:2000])
            # Divider between items
            self._divider()

    def output(self, path: str) -> None:
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        self.pdf.output(path)
