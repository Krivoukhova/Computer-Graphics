import tkinter as tk
from tkinter import messagebox
import random
import math

INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


class LineClipper:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x700")

        self.window_xmin = 200
        self.window_ymin = 150
        self.window_xmax = 600
        self.window_ymax = 450
        self.midpoint_precision = 1.0

        self.lines = []
        self.clipped_lines = []
        self.selected_algorithm = "Алгоритм Сазерленда-Коэна"

        self.create_widgets()
        self.create_canvas()
        self.draw_window()

    def create_widgets(self):
        control_frame = tk.Frame(self.root, width=300, padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        algo_frame = tk.LabelFrame(control_frame, text="Выбор алгоритма", padx=10, pady=10)
        algo_frame.pack(fill=tk.X, pady=(0, 10))

        self.algo_var = tk.StringVar(value=self.selected_algorithm)
        algorithms = ["Алгоритм Сазерленда-Коэна", "Простой алгоритм", "Алгоритм средней точки"]
        
        for algo in algorithms:
            tk.Radiobutton(algo_frame, text=algo, variable=self.algo_var,
                           value=algo, command=self.on_algorithm_change).pack(anchor=tk.W)

        self.precision_frame = tk.Frame(algo_frame)
        tk.Label(self.precision_frame, text="Точность:").pack(side=tk.LEFT)
        self.precision_var = tk.DoubleVar(value=self.midpoint_precision)
        tk.Entry(self.precision_frame, textvariable=self.precision_var, width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(self.precision_frame, text="OK", command=self.update_precision).pack(side=tk.LEFT)

        window_frame = tk.LabelFrame(control_frame, text="Параметры окна", padx=10, pady=10)
        window_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(window_frame, text="Xmin:").grid(row=0, column=0, sticky=tk.W)
        self.xmin_var = tk.IntVar(value=self.window_xmin)
        tk.Entry(window_frame, textvariable=self.xmin_var, width=8).grid(row=0, column=1, padx=5)

        tk.Label(window_frame, text="Xmax:").grid(row=0, column=2, sticky=tk.W)
        self.xmax_var = tk.IntVar(value=self.window_xmax)
        tk.Entry(window_frame, textvariable=self.xmax_var, width=8).grid(row=0, column=3, padx=5)

        tk.Label(window_frame, text="Ymin:").grid(row=1, column=0, sticky=tk.W)
        self.ymin_var = tk.IntVar(value=self.window_ymin)
        tk.Entry(window_frame, textvariable=self.ymin_var, width=8).grid(row=1, column=1, padx=5)

        tk.Label(window_frame, text="Ymax:").grid(row=1, column=2, sticky=tk.W)
        self.ymax_var = tk.IntVar(value=self.window_ymax)
        tk.Entry(window_frame, textvariable=self.ymax_var, width=8).grid(row=1, column=3, padx=5)

        tk.Button(window_frame, text="Обновить окно", command=self.update_window).grid(row=2, column=0, columnspan=4, pady=(10, 0))

        line_frame = tk.LabelFrame(control_frame, text="Добавление отрезка", padx=10, pady=10)
        line_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(line_frame, text="X1:").grid(row=0, column=0, sticky=tk.W)
        self.x1_var = tk.IntVar(value=50)
        tk.Entry(line_frame, textvariable=self.x1_var, width=8).grid(row=0, column=1, padx=5)

        tk.Label(line_frame, text="Y1:").grid(row=0, column=2, sticky=tk.W)
        self.y1_var = tk.IntVar(value=50)
        tk.Entry(line_frame, textvariable=self.y1_var, width=8).grid(row=0, column=3, padx=5)

        tk.Label(line_frame, text="X2:").grid(row=1, column=0, sticky=tk.W)
        self.x2_var = tk.IntVar(value=450)
        tk.Entry(line_frame, textvariable=self.x2_var, width=8).grid(row=1, column=1, padx=5)

        tk.Label(line_frame, text="Y2:").grid(row=1, column=2, sticky=tk.W)
        self.y2_var = tk.IntVar(value=450)
        tk.Entry(line_frame, textvariable=self.y2_var, width=8).grid(row=1, column=3, padx=5)

        tk.Button(line_frame, text="Добавить", command=self.add_line).grid(row=2, column=0, columnspan=4, pady=(10, 0))

        button_frame = tk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(button_frame, text="Добавить 5 случайных отрезков", command=self.add_random_lines).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Выполнить отсечение", command=self.clip_lines).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Очистить все", command=self.clear_all).pack(fill=tk.X, pady=2)

        legend_frame = tk.LabelFrame(control_frame, text="Обозначения", padx=10, pady=10)
        legend_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Label(legend_frame, text="■", fg="red", font=("Arial", 14)).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Окно отсечения").pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(legend_frame, text="■", fg="gray", font=("Arial", 14)).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Исходные отрезки").pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(legend_frame, text="■", fg="blue", font=("Arial", 14)).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Видимые части").pack(side=tk.LEFT)

    def create_canvas(self):
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def compute_code(self, x, y):
        code = INSIDE
        if x < self.window_xmin: code |= LEFT
        elif x > self.window_xmax: code |= RIGHT
        if y < self.window_ymin: code |= BOTTOM
        elif y > self.window_ymax: code |= TOP
        return code

    def is_point_inside(self, x, y):
        return (self.window_xmin <= x <= self.window_xmax and self.window_ymin <= y <= self.window_ymax)

    def cohen_sutherland_clip(self, x1, y1, x2, y2):
        code1 = self.compute_code(x1, y1)
        code2 = self.compute_code(x2, y2)
        accept = False

        while True:
            if code1 == 0 and code2 == 0:
                accept = True
                break
            elif code1 & code2 != 0:
                break
            else:
                code_out = code1 if code1 != 0 else code2
                if code_out & TOP:
                    x = x1 + (x2 - x1) * (self.window_ymax - y1) / (y2 - y1) if y2 != y1 else x1
                    y = self.window_ymax
                elif code_out & BOTTOM:
                    x = x1 + (x2 - x1) * (self.window_ymin - y1) / (y2 - y1) if y2 != y1 else x1
                    y = self.window_ymin
                elif code_out & RIGHT:
                    y = y1 + (y2 - y1) * (self.window_xmax - x1) / (x2 - x1) if x2 != x1 else y1
                    x = self.window_xmax
                elif code_out & LEFT:
                    y = y1 + (y2 - y1) * (self.window_xmin - x1) / (x2 - x1) if x2 != x1 else y1
                    x = self.window_xmin

                if code_out == code1:
                    x1, y1 = x, y
                    code1 = self.compute_code(x1, y1)
                else:
                    x2, y2 = x, y
                    code2 = self.compute_code(x2, y2)

        return (x1, y1, x2, y2) if accept else None

    def simple_algorithm_clip(self, x1, y1, x2, y2):
        if (self.is_point_inside(x1, y1) and self.is_point_inside(x2, y2)):
            return (x1, y1, x2, y2)
        if ((x1 < self.window_xmin and x2 < self.window_xmin) or (x1 > self.window_xmax and x2 > self.window_xmax) or
            (y1 < self.window_ymin and y2 < self.window_ymin) or (y1 > self.window_ymax and y2 > self.window_ymax)):
            return None

        intersections = []
        sides = [
            (self.window_xmin, self.window_ymin, self.window_xmax, self.window_ymin),
            (self.window_xmax, self.window_ymin, self.window_xmax, self.window_ymax),
            (self.window_xmax, self.window_ymax, self.window_xmin, self.window_ymax),
            (self.window_xmin, self.window_ymax, self.window_xmin, self.window_ymin)
        ]

        for x3, y3, x4, y4 in sides:
            intersection = self.line_intersection(x1, y1, x2, y2, x3, y3, x4, y4)
            if intersection and self.is_point_on_segment(intersection[0], intersection[1], x1, y1, x2, y2):
                intersections.append(intersection)

        if not intersections: return None
        if len(intersections) == 1:
            if self.is_point_inside(x1, y1): return (x1, y1, intersections[0][0], intersections[0][1])
            else: return (intersections[0][0], intersections[0][1], x2, y2)
        if len(intersections) >= 2:
            dist1 = self.distance(x1, y1, intersections[0][0], intersections[0][1])
            dist2 = self.distance(x1, y1, intersections[-1][0], intersections[-1][1])
            if dist1 < dist2:
                return (intersections[0][0], intersections[0][1], intersections[-1][0], intersections[-1][1])
            else:
                return (intersections[-1][0], intersections[-1][1], intersections[0][0], intersections[0][1])
        return None

    def midpoint_algorithm_clip(self, x1, y1, x2, y2):
        code1 = self.compute_code(x1, y1)
        code2 = self.compute_code(x2, y2)
        if code1 == 0 and code2 == 0: return (x1, y1, x2, y2)
        if code1 & code2 != 0: return None
        return self.midpoint_recursive(x1, y1, x2, y2)

    def midpoint_recursive(self, x1, y1, x2, y2):
        if self.distance(x1, y1, x2, y2) <= self.midpoint_precision:
            if self.is_point_inside(x1, y1) and self.is_point_inside(x2, y2): return (x1, y1, x2, y2)
            elif self.is_point_inside(x1, y1): return (x1, y1, x1, y1)
            elif self.is_point_inside(x2, y2): return (x2, y2, x2, y2)
            return None

        code1 = self.compute_code(x1, y1)
        code2 = self.compute_code(x2, y2)
        if code1 == 0 and code2 == 0: return (x1, y1, x2, y2)
        if code1 & code2 != 0: return None

        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        result1 = self.midpoint_recursive(x1, y1, mid_x, mid_y)
        result2 = self.midpoint_recursive(mid_x, mid_y, x2, y2)

        if result1 and result2:
            return (result1[0], result1[1], result2[2], result2[3])
        return result1 if result1 else result2

    def line_intersection(self, x1, y1, x2, y2, x3, y3, x4, y4):
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0: return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        return None

    def is_point_on_segment(self, px, py, x1, y1, x2, y2):
        epsilon = 1e-6
        if abs((py - y1) * (x2 - x1) - (px - x1) * (y2 - y1)) > epsilon: return False
        dot = (px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)
        if dot < 0: return False
        if dot > (x2 - x1)**2 + (y2 - y1)**2: return False
        return True

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def draw_window(self):
        self.canvas.delete("window")
        self.canvas.create_rectangle(self.window_xmin, self.window_ymin, self.window_xmax, self.window_ymax,
                                     outline="red", width=2, tags="window")

    def update_window(self):
        try:
            xmin, xmax = int(self.xmin_var.get()), int(self.xmax_var.get())
            ymin, ymax = int(self.ymin_var.get()), int(self.ymax_var.get())
            if xmin >= xmax or ymin >= ymax:
                messagebox.showerror("Ошибка", "Неверные координаты окна!")
                return
            self.window_xmin, self.window_xmax = xmin, xmax
            self.window_ymin, self.window_ymax = ymin, ymax
            self.draw_window()
            self.redraw_all_lines()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целые числа!")

    def update_precision(self):
        try:
            val = float(self.precision_var.get())
            if val > 0: self.midpoint_precision = val
        except: pass

    def on_algorithm_change(self):
        self.selected_algorithm = self.algo_var.get()
        if self.selected_algorithm == "Алгоритм средней точки":
            self.precision_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.precision_frame.pack_forget()

    def add_line(self):
        try:
            line = (int(self.x1_var.get()), int(self.y1_var.get()), int(self.x2_var.get()), int(self.y2_var.get()))
            self.lines.append(line)
            self.draw_original_line(*line)
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные координаты!")

    def add_random_lines(self):
        for _ in range(5):
            line = (random.randint(50, 750), random.randint(50, 650), random.randint(50, 750), random.randint(50, 650))
            self.lines.append(line)
            self.draw_original_line(*line)

    def draw_original_line(self, x1, y1, x2, y2):
        self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=1, tags="original")

    def draw_clipped_line(self, x1, y1, x2, y2):
        self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="clipped")

    def clip_lines(self):
        if not self.lines:
            return

        self.canvas.delete("clipped")
        self.clipped_lines.clear()

        for line in self.lines:
            if self.selected_algorithm == "Алгоритм Сазерленда-Коэна":
                clipped = self.cohen_sutherland_clip(*line)
            elif self.selected_algorithm == "Простой алгоритм":
                clipped = self.simple_algorithm_clip(*line)
            else:
                clipped = self.midpoint_algorithm_clip(*line)

            if clipped:
                self.clipped_lines.append(clipped)
                self.draw_clipped_line(*clipped)

    def redraw_all_lines(self):
        self.canvas.delete("original")
        self.canvas.delete("clipped")
        for line in self.lines:
            self.draw_original_line(*line)

    def clear_all(self):
        self.lines.clear()
        self.clipped_lines.clear()
        self.canvas.delete("all")
        self.draw_window()

if __name__ == "__main__":
    root = tk.Tk()
    app = LineClipper(root)
    root.mainloop()