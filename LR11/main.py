"""Лабораторная работа №11. 
Вариант 17.
"""
import math
import tkinter as tk
from tkinter import ttk

def hexahedron():
    """Куб: 8 вершин (±1, ±1, ±1); ребро - пара вершин, различающихся одной координатой."""
    v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    e = [(i, j) for i in range(8) for j in range(i + 1, 8)
         if sum(a != b for a, b in zip(v[i], v[j])) == 1]
    f = [[i for i in range(8) if v[i][a] == sg] for a in range(3) for sg in (-1, 1)]
    return v, e, f


def octahedron():
    """Октаэдр: 6 вершин на осях; рёбра соединяют все вершины, кроме противоположных."""
    v = [(1.4, 0, 0), (-1.4, 0, 0), (0, 1.4, 0), (0, -1.4, 0), (0, 0, 1.4), (0, 0, -1.4)]
    e = [(i, j) for i in range(6) for j in range(i + 1, 6) if not (i // 2 == j // 2)]
    f = [[a, b, c] for a in (0, 1) for b in (2, 3) for c in (4, 5)]
    return v, e, f


SOLIDS = {"Гексаэдр": hexahedron, "Октаэдр": octahedron}

def rot_x(p, a):
    x, y, z = p
    return (x, y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a))


def rot_y(p, a):
    x, y, z = p
    return (x * math.cos(a) + z * math.sin(a), y, -x * math.sin(a) + z * math.cos(a))


def rot_z(p, a):
    x, y, z = p
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z)


def observer(rho, phi, theta):
    """Точка наблюдения E в сферических координатах (ρ, φ, θ)."""
    return (rho * math.sin(phi) * math.cos(theta),
            rho * math.sin(phi) * math.sin(theta),
            rho * math.cos(phi))


def view_transform(p, E):
    """Видовое преобразование: перенос начала в E и поворот осей так, чтобы
    ось z_e была направлена от E к началу координат O (система наблюдателя)."""
    n = math.sqrt(sum(c * c for c in E))
    ez = tuple(-c / n for c in E)
    ex = (-ez[1], ez[0], 0.0)
    k = math.hypot(ex[0], ex[1]) or 1.0
    ex = (ex[0] / k, ex[1] / k, 0.0)
    ey = (ez[1] * ex[2] - ez[2] * ex[1], ez[2] * ex[0] - ez[0] * ex[2], ez[0] * ex[1] - ez[1] * ex[0])
    q = tuple(p[i] - E[i] for i in range(3))
    return (sum(q[i] * ex[i] for i in range(3)),
            sum(q[i] * ey[i] for i in range(3)),
            sum(q[i] * ez[i] for i in range(3)))


def project(pe, kind, d):
    """pe - видовые координаты. Центральная: x_p = d*x/z, y_p = d*y/z.
    Ортогональная: проекционная плоскость z=0, координата z отбрасывается."""
    x, y, z = pe
    if kind == "central":
        return (d * x / z, d * y / z)
    return (x, y)


def wireframe(name, ang, rho, phi, theta, kind, d):
    """Возвращает (2D-точки, рёбра (i, j, видимо)).
    Грань выпуклого тела видима, если её внешняя нормаль направлена к наблюдателю;
    ребро видимо, если видима хотя бы одна смежная грань."""
    verts, edges, faces = SOLIDS[name]()
    E = observer(rho, phi, theta)
    world = [rot_z(rot_y(rot_x(p, ang[0]), ang[1]), ang[2]) for p in verts]
    pts = [project(view_transform(p, E), kind, d) for p in world]
    vis = set()
    for f in faces:
        c = tuple(sum(world[i][k] for i in f) / len(f) for k in range(3))
        to_eye = E if kind == "ortho" else tuple(E[k] - c[k] for k in range(3))
        if sum(c[k] * to_eye[k] for k in range(3)) > 0:
            vis.update((min(i, j), max(i, j)) for i in f for j in f if i != j)
    return pts, [(i, j, (i, j) in vis) for i, j in edges]

class App:
    S = 120

    def __init__(self, root):
        self.ang = [math.radians(25), math.radians(35), 0.0]
        self.fig = tk.StringVar(value="Гексаэдр")
        self.kind = tk.StringVar(value="central")
        self.rho = tk.DoubleVar(value=7.0)
        self.phi = tk.DoubleVar(value=70.0)
        self.theta = tk.DoubleVar(value=40.0)
        self.d = tk.DoubleVar(value=7.0)
        self.hidden = tk.BooleanVar(value=True)

        left = ttk.Frame(root, padding=6); left.pack(side="left", fill="y")
        ttk.Label(left, text="Платоновы тела", font=("Arial", 12, "bold")).pack(pady=4)
        f = ttk.LabelFrame(left, text="Фигура", padding=6); f.pack(fill="x", pady=3)
        for n in SOLIDS:
            ttk.Radiobutton(f, text=n, value=n, variable=self.fig, command=self.redraw).pack(anchor="w")
        f = ttk.LabelFrame(left, text="Проекция", padding=6); f.pack(fill="x", pady=3)
        ttk.Radiobutton(f, text="Ортогональная", value="ortho", variable=self.kind, command=self.redraw).pack(anchor="w")
        ttk.Radiobutton(f, text="Центральная", value="central", variable=self.kind, command=self.redraw).pack(anchor="w")
        f = ttk.LabelFrame(left, text="Точка наблюдения E (ρ, φ°, θ°) и d", padding=6); f.pack(fill="x", pady=3)
        for text, var, a, b in (("ρ", self.rho, 3, 15), ("φ", self.phi, 5, 175), ("θ", self.theta, 0, 360), ("d", self.d, 1, 15)):
            tk.Scale(f, from_=a, to=b, resolution=0.5, orient="horizontal", label=text, variable=var,
                     command=lambda e: self.redraw()).pack(fill="x")
        f = ttk.LabelFrame(left, text="Вращение фигуры", padding=6); f.pack(fill="x", pady=3)
        for k, ax in enumerate("XYZ"):
            r = ttk.Frame(f); r.pack()
            ttk.Button(r, text=f"{ax} −", width=6, command=lambda k=k: self.rot(k, -1)).pack(side="left", padx=2)
            ttk.Button(r, text=f"{ax} +", width=6, command=lambda k=k: self.rot(k, 1)).pack(side="left", padx=2)
        ttk.Checkbutton(left, text="Невидимые рёбра пунктиром", variable=self.hidden,
                        command=self.redraw).pack(anchor="w", pady=2)
        ttk.Button(left, text="Сбросить поворот", command=self.reset).pack(fill="x", pady=4)

        self.cv = tk.Canvas(root, width=760, height=620, bg="white", highlightthickness=0)
        self.cv.pack(side="left", fill="both", expand=True)
        self.cv.bind("<Configure>", lambda e: self.redraw())
        self.redraw()

    def rot(self, k, s):
        self.ang[k] += s * math.radians(10)
        self.redraw()

    def reset(self):
        self.ang = [math.radians(25), math.radians(35), 0.0]
        self.redraw()

    def redraw(self):
        self.cv.delete("all")
        cx, cy = self.cv.winfo_width() / 2, self.cv.winfo_height() / 2
        try:
            pts, edges = wireframe(self.fig.get(), self.ang, self.rho.get(), math.radians(self.phi.get()),
                                   math.radians(self.theta.get()), self.kind.get(), self.d.get())
        except ZeroDivisionError:
            return
        for i, j, visible in edges:
            if not visible and not self.hidden.get():
                continue
            self.cv.create_line(cx + self.S * pts[i][0], cy - self.S * pts[i][1],
                                cx + self.S * pts[j][0], cy - self.S * pts[j][1], width=2,
                                fill="#1b2430" if visible else "#6b7788", dash=None if visible else (5, 4))
        for x, y in pts:
            self.cv.create_oval(cx + self.S * x - 4, cy - self.S * y - 4, cx + self.S * x + 4, cy - self.S * y + 4,
                                fill="red", outline="red")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()