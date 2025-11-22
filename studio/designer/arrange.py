from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from PyQt6.QtCore import QPointF, QRectF


@dataclass
class Node:
    rect: QRectF
    weight: float = 1.0

    def center(self) -> Tuple[float, float]:
        r = self.rect
        return r.center().x(), r.center().y()


def grid_positions(rects: List[QRectF], cols: int, spacing_x: float, spacing_y: float) -> List[QRectF]:
    if not rects:
        return []
    w = max(r.width() for r in rects)
    h = max(r.height() for r in rects)
    out: List[QRectF] = []
    for i, r in enumerate(rects):
        row = i // cols
        col = i % cols
        x = col * (w + spacing_x)
        y = row * (h + spacing_y)
        out.append(QRectF(x, y, r.width(), r.height()))
    return out


def pack_in_rect(rects: List[QRectF], outer: QRectF, spacing: float = 8.0) -> List[QRectF]:
    if not rects:
        return []
    rects = sorted(rects, key=lambda r: (r.height(), r.width()), reverse=True)
    rows: List[List[QRectF]] = []
    current_row: List[QRectF] = []
    current_w = 0.0
    max_h = 0.0
    for r in rects:
        if current_row and current_w + r.width() > outer.width():
            rows.append(current_row)
            current_row = []
            current_w = 0.0
            max_h = 0.0
        current_row.append(r)
        current_w += r.width() + spacing
        max_h = max(max_h, r.height())
    if current_row:
        rows.append(current_row)
    out: List[QRectF] = []
    y = outer.top()
    for row in rows:
        x = outer.left()
        row_h = max(r.height() for r in row) if row else 0
        for r in row:
            out.append(QRectF(x, y, r.width(), r.height()))
            x += r.width() + spacing
        y += row_h + spacing
    return out


def align_to_grid(rects: List[QRectF], grid_w: float, grid_h: float) -> List[QRectF]:
    out: List[QRectF] = []
    for r in rects:
        x = round(r.left() / grid_w) * grid_w
        y = round(r.top() / grid_h) * grid_h
        out.append(QRectF(x, y, r.width(), r.height()))
    return out


def flow_layout(rects: List[QRectF], start: QPointF, max_width: float, gap_x: float, gap_y: float) -> List[QRectF]:
    x = start.x()
    y = start.y()
    row_h = 0.0
    out: List[QRectF] = []
    for r in rects:
        if out and x + r.width() > start.x() + max_width:
            x = start.x()
            y += row_h + gap_y
            row_h = 0.0
        out.append(QRectF(x, y, r.width(), r.height()))
        x += r.width() + gap_x
        row_h = max(row_h, r.height())
    return out


def compute_compact_layout(rects: List[QRectF], start: QPointF, grid_w: float, grid_h: float, max_cols: int) -> List[QRectF]:
    if not rects:
        return []
    # size per cell is grid_w x grid_h. We'll map each rect to new cells of width 2*grid_w by 1.5*grid_h approx.
    widths = [r.width() for r in rects]
    heights = [r.height() for r in rects]
    cell_w = max(grid_w, min(widths) if widths else grid_w)
    cell_h = max(grid_h, min(heights) if heights else grid_h)
    cols = max(1, max_cols)
    out: List[QRectF] = []
    x = start.x()
    y = start.y()
    col = 0
    for r in rects:
        out.append(QRectF(x, y, r.width(), r.height()))
        col += 1
        if col >= cols:
            col = 0
            x = start.x()
            y += cell_h * 2
        else:
            x += cell_w * 2
    return out


def smart_arrange(rects: List[QRectF], strategy: str, grid_w: float, grid_h: float, start: QPointF, area: QRectF) -> List[QRectF]:
    if strategy == "grid":
        cols = max(1, int(area.width() // (grid_w * 2)))
        prelim = grid_positions(rects, cols, grid_w * 0.5, grid_h * 0.5)
        return align_to_grid([QRectF(start.x() + r.x(), start.y() + r.y(), r.width(), r.height()) for r in prelim], grid_w, grid_h)
    if strategy == "pack":
        packed = pack_in_rect(rects, QRectF(start.x(), start.y(), area.width(), area.height()), spacing=grid_w * 0.25)
        return align_to_grid(packed, grid_w, grid_h)
    if strategy == "flow":
        fl = flow_layout(rects, start, area.width(), grid_w * 0.5, grid_h * 0.5)
        return align_to_grid(fl, grid_w, grid_h)
    return compute_compact_layout(rects, start, grid_w, grid_h, max_cols=max(1, int(area.width() // (grid_w * 2))))
