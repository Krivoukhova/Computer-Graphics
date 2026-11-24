"""Лабораторная работа №10.
Вариант 1.
"""
import tkinter as tk
from tkinter import ttk

def lerp(a, b, t):
    """Точка на отрезке ab в пропорции t."""
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def bezier_quad(p0, p1, p2, t, depth):
    """Геометрическое построение квадратичной кривой Безье.
    Возвращает (вершины уточнённого полигона, промежуточные точки по шагам).
    Промежуточные точки: список по уровням разбиения [(P1(1), P2(1), P1(2)), ...]."""
    levels = [[] for _ in range(depth)]
    out = [p0]

    def rec(a, b, c, d, lvl):
        if d == 0:
            out.append(c)
            return
        p1_, p2_ = lerp(a, b, t), lerp(b, c, t)
        m = lerp(p1_, p2_, t)
        levels[lvl].append((p1_, p2_, m))
        rec(a, p1_, m, d - 1, lvl + 1)
        rec(m, p2_, c, d - 1, lvl + 1)

    rec(p0, p1, p2, depth, 0)
    return out, levels


def bezier_chain(pts, t, depth):
    """Произвольное число вершин: каждые три подряд идущие точки образуют
    сегмент (P0,P1,P2), (P2,P3,P4), ... Хвост из одной точки соединяется отрезком."""
    if len(pts) < 3:
        return list(pts), [[] for _ in range(depth)]
    res, levels = [pts[0]], [[] for _ in range(depth)]
    i = 0
    while i + 2 < len(pts):
        seg, lv = bezier_quad(pts[i], pts[i + 1], pts[i + 2], t, depth)
        res += seg[1:]
        for k in range(depth):
            levels[k] += lv[k]
        i += 2
    if i + 1 < len(pts):
        res.append(pts[i + 1])
    return res, levels


def chaikin(pts, iterations):
    """Угловое отсечение Чайкина: Qi = 3/4 Pi + 1/4 Pi+1, Ri = 1/4 Pi + 3/4 Pi+1."""
    cur = list(pts)
    for _ in range(iterations):
        nxt = []
        for i in range(len(cur) - 1):
            nxt.append(lerp(cur[i], cur[i + 1], 0.25))
            nxt.append(lerp(cur[i], cur[i + 1], 0.75))
        cur = nxt
    return cur

class App:
    R = 5

    def __init__(self, root):
        self.root = root
        root.title("Построение кривых Безье и Чайкина")
        self.pts = []
        self.mode = None
        self.step = 0 
        self.drag = None

        self.kind = tk.StringVar(value="bezier")
        self.t = tk.DoubleVar(value=0.5)
        self.iters = tk.IntVar(value=3)
        self.show_mid = tk.BooleanVar(value=True)
        self.show_ctl = tk.BooleanVar(value=True)
        self.show_ref = tk.BooleanVar(value=True)
        self.max_steps = tk.IntVar(value=5)

        left = ttk.Frame(root, padding=6)
        left.pack(side="left", fill="y")
        ttk.Label(left, text="Построение кривых", font=("Arial", 12, "bold")).pack(pady=4)

        f = ttk.LabelFrame(left, text="Кривая Безье (2-й степени)", padding=6)
        f.pack(fill="x", pady=3)
        ttk.Label(f, text="Параметр разбиения t:").pack(anchor="w")
        tk.Scale(f, from_=0.05, to=0.95, resolution=0.05, orient="horizontal",
                 variable=self.t, command=lambda e: self.redraw()).pack(fill="x")
        ttk.Label(f, text="Максимум шагов разбиения:").pack(anchor="w")
        tk.Scale(f, from_=1, to=8, orient="horizontal", variable=self.max_steps).pack(fill="x")
        row = ttk.Frame(f); row.pack(fill="x", pady=2)
        ttk.Button(row, text="Следующий шаг", command=self.next_step).pack(side="left", padx=2)
        ttk.Button(row, text="Полное построение", command=self.full_bezier).pack(side="left", padx=2)

        f = ttk.LabelFrame(left, text="Кривая Чайкина", padding=6)
        f.pack(fill="x", pady=3)
        ttk.Label(f, text="Число разбиений:").pack(anchor="w")
        tk.Scale(f, from_=0, to=8, orient="horizontal", variable=self.iters,
                 command=lambda e: self.redraw()).pack(fill="x")
        ttk.Button(f, text="Построить Чайкина", command=self.run_chaikin).pack(pady=2)

        f = ttk.LabelFrame(left, text="Управление точками", padding=6)
        f.pack(fill="x", pady=3)
        ttk.Label(f, text="ЛКМ по полю - добавить точку,\nперетаскивание - переместить",
                  justify="left").pack(anchor="w")
        tk.Button(f, text="Удалить последнюю", bg="#ff9a9a", command=self.del_last).pack(fill="x", pady=2)
        tk.Button(f, text="Очистить все точки", bg="#ff6a6a", command=self.clear).pack(fill="x", pady=2)

        f = ttk.LabelFrame(left, text="Настройки отображения", padding=6)
        f.pack(fill="x", pady=3)
        for text, var in (("Показывать контрольные точки", self.show_ctl),
                          ("Показывать промежуточные точки", self.show_mid),
                          ("Показывать вершины уточнённого полигона", self.show_ref)):
            ttk.Checkbutton(f, text=text, variable=var, command=self.redraw).pack(anchor="w")

        self.info = ttk.Label(left, text="", wraplength=240, justify="left")
        self.info.pack(fill="x", pady=6)

        self.cv = tk.Canvas(root, width=860, height=640, bg="white", highlightthickness=0)
        self.cv.pack(side="left", fill="both", expand=True)
        self.cv.bind("<Button-1>", self.on_down)
        self.cv.bind("<B1-Motion>", self.on_move)
        self.cv.bind("<ButtonRelease-1>", lambda e: setattr(self, "drag", None))

    def next_step(self):
        self.mode = "bezier"
        if self.step < self.max_steps.get():
            self.step += 1
        self.redraw()

    def full_bezier(self):
        self.mode, self.step = "bezier", self.max_steps.get()
        self.redraw()

    def run_chaikin(self):
        self.mode = "chaikin"
        self.redraw()

    def del_last(self):
        if self.pts:
            self.pts.pop()
        self.redraw()

    def clear(self):
        self.pts, self.mode, self.step = [], None, 0
        self.redraw()

    def hit(self, x, y):
        for i, p in enumerate(self.pts):
            if abs(p[0] - x) <= 9 and abs(p[1] - y) <= 9:
                return i
        return None

    def on_down(self, e):
        i = self.hit(e.x, e.y)
        if i is None:
            self.pts.append((e.x, e.y))
            self.drag = len(self.pts) - 1
        else:
            self.drag = i
        self.redraw()

    def on_move(self, e):
        if self.drag is not None:
            self.pts[self.drag] = (e.x, e.y)
            self.redraw()

    def dot(self, p, color, r=None):
        r = r or self.R
        self.cv.create_oval(p[0] - r, p[1] - r, p[0] + r, p[1] + r, fill=color, outline=color)

    def line(self, pts, color, w=1, dash=None):
        if len(pts) > 1:
            self.cv.create_line(*[c for p in pts for c in p], fill=color, width=w, dash=dash)

    def redraw(self):
        self.cv.delete("all")
        pts = self.pts
        if self.show_ctl.get():
            self.line(pts, "#888", 1, (4, 4))
        text = f"Контрольных точек: {len(pts)}."
        if self.mode == "bezier" and len(pts) >= 3:
            res, levels = bezier_chain(pts, self.t.get(), self.step)
            for lv in levels:
                for p1, p2, m in lv:
                    if self.show_mid.get():
                        self.line([p1, p2], "#4a90d9", 1)
                        self.dot(p1, "#4a90d9", 3); self.dot(p2, "#4a90d9", 3); self.dot(m, "#2e7d32", 3)
            self.line(res, "#d9480f", 2)
            if self.show_ref.get():
                for p in res:
                    self.dot(p, "#7c3aed", 3)
            text += f" Шаг разбиения: {self.step}, t = {self.t.get():.2f}, вершин в полигоне: {len(res)}."
        elif self.mode == "chaikin" and len(pts) >= 2:
            res = chaikin(pts, self.iters.get())
            self.line(res, "#d9480f", 2)
            if self.show_ref.get():
                for p in res:
                    self.dot(p, "#7c3aed", 2 if len(res) > 200 else 3)
            text += f" Разбиений: {self.iters.get()}, вершин в полигоне: {len(res)}."
        elif self.mode and len(pts) < 3:
            text += " Для построения нужно не менее 3 точек (Чайкина - 2)."
        if self.show_ctl.get():
            for i, p in enumerate(pts):
                self.dot(p, "red")
                self.cv.create_text(p[0] + 4, p[1] - 12, text=f"P{i}", fill="red")
        self.info.config(text=text)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()