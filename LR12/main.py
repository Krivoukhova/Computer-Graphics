# -*- coding: utf-8 -*-
"""Лабораторная работа №12. 
Вариант 1.
"""
import math
import random
import tkinter as tk
from tkinter import ttk


def binom(n, i):
    return math.factorial(n) // (math.factorial(i) * math.factorial(n - i))


def bernstein(n, i, u):
    return binom(n, i) * (u ** i) * ((1 - u) ** (n - i))


def bezier_point(grid, u, v):
    n, m = len(grid) - 1, len(grid[0]) - 1
    x = y = z = 0.0
    for i in range(n + 1):
        bu = bernstein(n, i, u)
        for j in range(m + 1):
            w = bu * bernstein(m, j, v)
            px, py, pz = grid[i][j]
            x += w * px; y += w * py; z += w * pz
    return (x, y, z)


def bezier_surface(grid, res):
    return [[bezier_point(grid, a / res, b / res) for b in range(res + 1)]
            for a in range(res + 1)]


def make_grid(n, m, step=1.0, amp=1.2):
    return [[((j - (m - 1) / 2) * step, (i - (n - 1) / 2) * step, random.uniform(-amp, amp))
             for j in range(m)] for i in range(n)]


def project(p, ax, az, scale, cx, cy):
    x, y, z = p
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    f = 12.0 / (12.0 + y * 0.5)
    return (cx + x * scale * f, cy - z * scale * f), y


class App:
    def __init__(self, root):
        self.root = root
        self.n, self.m = 4, 4
        self.grid = make_grid(self.n, self.m)
        self.ax, self.az, self.scale = 1.0, 0.6, 70.0
        self.sel = None
        self.last = None

        self.res = tk.IntVar(value=10)
        self.show_ctl = tk.BooleanVar(value=True)
        self.show_ref = tk.BooleanVar(value=True)
        self.sn = tk.IntVar(value=self.n)
        self.sm = tk.IntVar(value=self.m)

        left = ttk.Frame(root, padding=6)
        left.pack(side="left", fill="y")
        ttk.Label(left, text="Поверхность Безье", font=("Arial", 12, "bold")).pack(pady=4)

        f = ttk.LabelFrame(left, text="Контрольная сетка", padding=6)
        f.pack(fill="x", pady=3)
        r = ttk.Frame(f); r.pack(fill="x")
        ttk.Label(r, text="Строк n:").pack(side="left")
        ttk.Spinbox(r, from_=2, to=8, width=4, textvariable=self.sn).pack(side="left", padx=4)
        ttk.Label(r, text="Столбцов m:").pack(side="left")
        ttk.Spinbox(r, from_=2, to=8, width=4, textvariable=self.sm).pack(side="left", padx=4)
        ttk.Button(f, text="Применить размер", command=self.apply_size).pack(fill="x", pady=2)
        ttk.Button(f, text="Случайные высоты", command=self.randomize).pack(fill="x", pady=2)

        f = ttk.LabelFrame(left, text="Параметр разбиения", padding=6)
        f.pack(fill="x", pady=3)
        ttk.Label(f, text="Число разбиений по u и v:").pack(anchor="w")
        tk.Scale(f, from_=2, to=40, orient="horizontal", variable=self.res,
                 command=lambda e: self.redraw()).pack(fill="x")

        f = ttk.LabelFrame(left, text="Редактирование точки", padding=6)
        f.pack(fill="x", pady=3)
        ttk.Label(f, text="Выберите точку кликом, затем:", justify="left").pack(anchor="w")
        g = ttk.Frame(f); g.pack()
        for k, (txt, d) in enumerate((("X-", (-1, 0, 0)), ("X+", (1, 0, 0)), ("Y-", (0, -1, 0)),
                                       ("Y+", (0, 1, 0)), ("Z-", (0, 0, -1)), ("Z+", (0, 0, 1)))):
            ttk.Button(g, text=txt, width=5, command=lambda d=d: self.move_sel(d)).grid(row=k // 2, column=k % 2, padx=2, pady=1)

        f = ttk.LabelFrame(left, text="Вид", padding=6)
        f.pack(fill="x", pady=3)
        ttk.Label(f, text="Мышь: вращение (ЛКМ по пустому месту),\nколесо - масштаб", justify="left").pack(anchor="w")
        r = ttk.Frame(f); r.pack()
        for txt, fn in (("←", lambda: self.rot(0, -.15)), ("→", lambda: self.rot(0, .15)),
                        ("↑", lambda: self.rot(-.15, 0)), ("↓", lambda: self.rot(.15, 0)),
                        ("+", lambda: self.zoom(1.15)), ("-", lambda: self.zoom(1 / 1.15))):
            ttk.Button(r, text=txt, width=3, command=fn).pack(side="left", padx=1)

        f = ttk.LabelFrame(left, text="Настройки отображения", padding=6)
        f.pack(fill="x", pady=3)
        ttk.Checkbutton(f, text="Контрольные точки и сетка", variable=self.show_ctl, command=self.redraw).pack(anchor="w")
        ttk.Checkbutton(f, text="Вершины поверхности", variable=self.show_ref, command=self.redraw).pack(anchor="w")
        self.info = ttk.Label(left, text="", wraplength=240, justify="left")
        self.info.pack(fill="x", pady=6)

        self.cv = tk.Canvas(root, width=860, height=640, bg="white", highlightthickness=0)
        self.cv.pack(side="left", fill="both", expand=True)
        self.cv.bind("<Button-1>", self.on_down)
        self.cv.bind("<B1-Motion>", self.on_move)
        self.cv.bind("<MouseWheel>", lambda e: self.zoom(1.1 if e.delta > 0 else 1 / 1.1))
        self.cv.bind("<Button-4>", lambda e: self.zoom(1.1))
        self.cv.bind("<Button-5>", lambda e: self.zoom(1 / 1.1))
        self.cv.bind("<Configure>", lambda e: self.redraw())
        self.redraw()

    def apply_size(self):
        self.n, self.m = max(2, min(8, self.sn.get())), max(2, min(8, self.sm.get()))
        self.grid, self.sel = make_grid(self.n, self.m), None
        self.redraw()

    def randomize(self):
        self.grid = make_grid(self.n, self.m)
        self.redraw()

    def move_sel(self, d, k=0.25):
        if self.sel:
            i, j = self.sel
            x, y, z = self.grid[i][j]
            self.grid[i][j] = (x + d[0] * k, y + d[1] * k, z + d[2] * k)
            self.redraw()

    def rot(self, dax, daz):
        self.ax += dax; self.az += daz
        self.redraw()

    def zoom(self, k):
        self.scale *= k
        self.redraw()

    def on_down(self, e):
        self.last = (e.x, e.y)
        best, bd = None, 12
        for i in range(self.n):
            for j in range(self.m):
                (px, py), _ = self.pr(self.grid[i][j])
                d = math.hypot(px - e.x, py - e.y)
                if d < bd:
                    best, bd = (i, j), d
        self.sel = best
        self.redraw()

    def on_move(self, e):
        if self.sel is None and self.last:
            self.az += (e.x - self.last[0]) * 0.01
            self.ax = self.ax + (e.y - self.last[1]) * 0.01
            self.last = (e.x, e.y)
            self.redraw()

    def pr(self, p):
        return project(p, self.ax, self.az, self.scale, self.cv.winfo_width() / 2, self.cv.winfo_height() / 2)

    def redraw(self):
        self.cv.delete("all")
        res = self.res.get()
        surf = bezier_surface(self.grid, res)
        P = [[self.pr(p)[0] for p in row] for row in surf]
        for a in range(res + 1):
            for b in range(res + 1):
                if a < res:
                    self.cv.create_line(*P[a][b], *P[a + 1][b], fill="#d9480f")
                if b < res:
                    self.cv.create_line(*P[a][b], *P[a][b + 1], fill="#d9480f")
        if self.show_ref.get():
            for row in P:
                for x, y in row:
                    self.cv.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#7c3aed", outline="#7c3aed")
        if self.show_ctl.get():
            C = [[self.pr(p)[0] for p in row] for row in self.grid]
            for row in C:
                self.cv.create_line(*[c for p in row for c in p], fill="#888", dash=(4, 4))
            for j in range(self.m):
                self.cv.create_line(*[c for i in range(self.n) for c in C[i][j]], fill="#888", dash=(4, 4))
            for i in range(self.n):
                for j in range(self.m):
                    x, y = C[i][j]
                    col = "#1976d2" if self.sel == (i, j) else "red"
                    self.cv.create_oval(x - 5, y - 5, x + 5, y + 5, fill=col, outline=col)
        self.info.config(text=f"Сетка {self.n}x{self.m} (степени {self.n - 1} и {self.m - 1}), "
                              f"разбиений: {res}, вершин поверхности: {(res + 1) ** 2}.")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
