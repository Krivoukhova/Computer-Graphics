import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showinfo
import math

class ImageInterpolationApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1400x900")

        self.original_image_data = None
        self.transformed_image_data = None
        self.display_images = {}

        self.create_interface()

    def create_interface(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="Открыть изображение",
                   command=self.open_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сохранить результат",
                   command=self.save_image).pack(side=tk.LEFT, padx=5)

        params_frame = ttk.LabelFrame(main_frame, text="Параметры преобразования")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(params_frame, text="Масштаб:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.scale_var = tk.DoubleVar(value=1.5)
        ttk.Entry(params_frame, textvariable=self.scale_var, width=8).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(params_frame, text="Угол поворота (°):").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        self.rotate_var = tk.DoubleVar(value=30)
        ttk.Entry(params_frame, textvariable=self.rotate_var, width=8).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(params_frame, text="Угол скоса (°):").grid(row=0, column=4, padx=5, pady=2, sticky=tk.W)
        self.skew_var = tk.DoubleVar(value=15)
        ttk.Entry(params_frame, textvariable=self.skew_var, width=8).grid(row=0, column=5, padx=5, pady=2)

        ttk.Label(params_frame, text="Метод интерполяции:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.interpolation_var = tk.StringVar(value="ближайший сосед")
        interpolation_combo = ttk.Combobox(params_frame, textvariable=self.interpolation_var,
                                           values=["ближайший сосед", "билинейная", "бикубическая"], width=15)
        interpolation_combo.grid(row=1, column=1, padx=5, pady=2)

        ttk.Button(params_frame, text="Применить преобразование",
                   command=self.apply_transformation).grid(row=1, column=2, columnspan=2, padx=5, pady=2)

        images_frame = ttk.Frame(main_frame)
        images_frame.pack(fill=tk.BOTH, expand=True)

        original_frame = ttk.LabelFrame(images_frame, text="Исходное изображение")
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.original_container = tk.Frame(original_frame, bg="white")
        self.original_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.original_canvas = tk.Canvas(self.original_container, bg="white",
                                         highlightthickness=1, highlightbackground="#cccccc")
        self.original_canvas.pack(fill=tk.BOTH, expand=True)

        transformed_frame = ttk.LabelFrame(images_frame, text="Преобразованное изображение")
        transformed_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.transformed_container = tk.Frame(transformed_frame, bg="white")
        self.transformed_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.transformed_canvas = tk.Canvas(self.transformed_container, bg="white",
                                            highlightthickness=1, highlightbackground="#cccccc")
        self.transformed_canvas.pack(fill=tk.BOTH, expand=True)

        info_frame = ttk.LabelFrame(main_frame, text="Информация")
        info_frame.pack(fill=tk.X, pady=(10, 0))

    def open_image(self):
        """Загрузка изображения"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("PPM файлы", "*.ppm"), ("Все файлы", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'rb') as f:
                signature = f.readline().strip()
                if signature != b'P6':
                    raise ValueError("Поддерживаются только P6 PPM файлы")

                dimensions = f.readline().split()
                width, height = int(dimensions[0]), int(dimensions[1])

                max_color = f.readline().strip()

                pixel_data = f.read()

            self.original_image_data = {
                'width': width,
                'height': height,
                'pixels': list(pixel_data),
                'max_color': max_color
            }

            self.display_original_image()

        except Exception as e:
            showinfo("Ошибка", f"Не удалось загрузить изображение: {e}")

    def display_original_image(self):
        """Отображение исходного изображения на canvas"""
        if not self.original_image_data:
            return

        image_data = self.create_ppm_data(
            self.original_image_data['width'],
            self.original_image_data['height'],
            self.original_image_data['pixels']
        )

        photo = tk.PhotoImage(data=image_data)
        self.display_images['original'] = photo

        scaled_photo = self.scale_image_to_fit_canvas(photo, self.original_canvas)
        self.display_images['original_scaled'] = scaled_photo

        self.original_canvas.delete("all")

        self.original_canvas.update()
        canvas_width = self.original_canvas.winfo_width()
        canvas_height = self.original_canvas.winfo_height()

        x = canvas_width // 2
        y = canvas_height // 2

        self.original_canvas.create_image(x, y, image=scaled_photo, anchor=tk.CENTER)

    def display_transformed_image(self):
        """Отображение преобразованного изображения"""
        if not self.transformed_image_data:
            return

        image_data = self.create_ppm_data(
            self.transformed_image_data['width'],
            self.transformed_image_data['height'],
            self.transformed_image_data['pixels']
        )

        photo = tk.PhotoImage(data=image_data)
        self.display_images['transformed'] = photo

        scaled_photo = self.scale_image_to_fit_canvas(photo, self.transformed_canvas)
        self.display_images['transformed_scaled'] = scaled_photo

        self.transformed_canvas.delete("all")

        self.transformed_canvas.update()
        canvas_width = self.transformed_canvas.winfo_width()
        canvas_height = self.transformed_canvas.winfo_height()

        x = canvas_width // 2
        y = canvas_height // 2

        self.transformed_canvas.create_image(x, y, image=scaled_photo, anchor=tk.CENTER)

    def scale_image_to_fit_canvas(self, photo, canvas):
        """Масштабирует изображение чтобы полностью поместиться в canvas"""
        canvas.update()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width <= 10:
            canvas_width = 400
        if canvas_height <= 10:
            canvas_height = 400

        image_width = photo.width()
        image_height = photo.height()

        scale_x = canvas_width / image_width
        scale_y = canvas_height / image_height
        scale = min(scale_x, scale_y)

        if scale < 1:
            subsample = int(1 / scale)
            return photo.subsample(subsample)
        else:
            scale = min(scale, 2.0)
            zoom = int(scale)
            return photo.zoom(zoom)

    def apply_transformation(self):
        """Применение аффинного преобразования с выбранным методом интерполяции"""
        if not self.original_image_data:
            showinfo("Ошибка", "Сначала откройте изображение")
            return

        try:
            scale = self.scale_var.get()
            angle = self.rotate_var.get()
            skew_angle = self.skew_var.get()
            method_ru = self.interpolation_var.get()

            method_map = {
                "ближайший сосед": "nearest",
                "билинейная": "bilinear",
                "бикубическая": "bicubic"
            }
            method = method_map.get(method_ru, "bilinear")

            result = self.affine_transform(
                self.original_image_data,
                scale, angle, skew_angle, method
            )

            self.transformed_image_data = result

            self.display_transformed_image()

        except Exception as e:
            showinfo("Ошибка", f"Ошибка при преобразовании: {e}")

    def affine_transform(self, image_data, scale, angle, skew_angle, method):
        """Аффинное преобразование с выбранным методом интерполяции"""
        width, height = image_data['width'], image_data['height']
        pixels = image_data['pixels']

        new_width = int(width * scale)
        new_height = int(height * scale)

        phi = math.radians(angle)
        skew_phi = math.radians(skew_angle)

        center_x_orig = width / 2
        center_y_orig = height / 2
        center_x_new = new_width / 2
        center_y_new = new_height / 2

        bg_r, bg_g, bg_b = 255, 255, 255

        new_pixels = [bg_r, bg_g, bg_b] * (new_width * new_height)

        for y_new in range(new_height):
            for x_new in range(new_width):
                x_rel = x_new - center_x_new
                y_rel = y_new - center_y_new

                x_unskew = x_rel - y_rel * math.tan(skew_phi)
                y_unskew = y_rel

                x_unrot = x_unskew * math.cos(-phi) - y_unskew * math.sin(-phi)
                y_unrot = x_unskew * math.sin(-phi) + y_unskew * math.cos(-phi)

                x_orig = x_unrot + center_x_orig
                y_orig = y_unrot + center_y_orig

                if 0 <= x_orig < width and 0 <= y_orig < height:
                    if method == "nearest":
                        color = self.nearest_neighbor_interpolation(pixels, width, height, x_orig, y_orig)
                    elif method == "bilinear":
                        color = self.bilinear_interpolation(pixels, width, height, x_orig, y_orig)
                    elif method == "bicubic":
                        color = self.bicubic_interpolation(pixels, width, height, x_orig, y_orig)
                    else:
                        color = (bg_r, bg_g, bg_b)

                    idx = (y_new * new_width + x_new) * 3
                    new_pixels[idx] = color[0]
                    new_pixels[idx + 1] = color[1]
                    new_pixels[idx + 2] = color[2]

        return {
            'width': new_width,
            'height': new_height,
            'pixels': new_pixels,
            'max_color': image_data['max_color']
        }

    def nearest_neighbor_interpolation(self, pixels, width, height, x, y):
        """Интерполяция по ближайшему соседу"""
        x_round = min(max(0, round(x)), width - 1)
        y_round = min(max(0, round(y)), height - 1)

        idx = (y_round * width + x_round) * 3
        return (pixels[idx], pixels[idx + 1], pixels[idx + 2])

    def bilinear_interpolation(self, pixels, width, height, x, y):
        """Билинейная интерполяция"""
        x0 = int(math.floor(x))
        y0 = int(math.floor(y))
        x1 = min(x0 + 1, width - 1)
        y1 = min(y0 + 1, height - 1)

        a = x - x0
        b = y - y0

        def get_pixel_color(x_coord, y_coord):
            if 0 <= x_coord < width and 0 <= y_coord < height:
                idx = (y_coord * width + x_coord) * 3
                return (pixels[idx], pixels[idx + 1], pixels[idx + 2])
            else:
                return (255, 255, 255)

        c00 = get_pixel_color(x0, y0)
        c10 = get_pixel_color(x1, y0)
        c01 = get_pixel_color(x0, y1)
        c11 = get_pixel_color(x1, y1)

        top_r = c00[0] * (1 - a) + c10[0] * a
        top_g = c00[1] * (1 - a) + c10[1] * a
        top_b = c00[2] * (1 - a) + c10[2] * a

        bottom_r = c01[0] * (1 - a) + c11[0] * a
        bottom_g = c01[1] * (1 - a) + c11[1] * a
        bottom_b = c01[2] * (1 - a) + c11[2] * a

        final_r = top_r * (1 - b) + bottom_r * b
        final_g = top_g * (1 - b) + bottom_g * b
        final_b = top_b * (1 - b) + bottom_b * b

        return (int(final_r), int(final_g), int(final_b))

    def bicubic_interpolation(self, pixels, width, height, x, y):
        """Бикубическая интерполяция с исправленными коэффициентами"""
        x0 = int(math.floor(x))
        y0 = int(math.floor(y))

        a = x - x0
        b = y - y0

        def get_pixel_color(x_coord, y_coord):
            if 0 <= x_coord < width and 0 <= y_coord < height:
                idx = (y_coord * width + x_coord) * 3
                return (pixels[idx], pixels[idx + 1], pixels[idx + 2])
            else:
                return (255, 255, 255)

        colors = []
        for j in range(-1, 3):
            row = []
            for i in range(-1, 3):
                row.append(get_pixel_color(x0 + i, y0 + j))
            colors.append(row)

        def cubic_interpolate(p0, p1, p2, p3, t):
            """Кубическая интерполяция между 4 точками"""
            return (
                    p1 + 0.5 * t * (
                    p2 - p0 + t * (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3 + t * (3.0 * (p1 - p2) + p3 - p0)))
            )

        interpolated_rows = []
        for j in range(4):
            row_r = [colors[j][i][0] for i in range(4)]
            row_g = [colors[j][i][1] for i in range(4)]
            row_b = [colors[j][i][2] for i in range(4)]

            r_x = cubic_interpolate(row_r[0], row_r[1], row_r[2], row_r[3], a)
            g_x = cubic_interpolate(row_g[0], row_g[1], row_g[2], row_g[3], a)
            b_x = cubic_interpolate(row_b[0], row_b[1], row_b[2], row_b[3], a)

            interpolated_rows.append((r_x, g_x, b_x))

        r_values = [interpolated_rows[j][0] for j in range(4)]
        g_values = [interpolated_rows[j][1] for j in range(4)]
        b_values = [interpolated_rows[j][2] for j in range(4)]

        final_r = cubic_interpolate(r_values[0], r_values[1], r_values[2], r_values[3], b)
        final_g = cubic_interpolate(g_values[0], g_values[1], g_values[2], g_values[3], b)
        final_b = cubic_interpolate(b_values[0], b_values[1], b_values[2], b_values[3], b)

        final_r = max(0, min(255, int(final_r)))
        final_g = max(0, min(255, int(final_g)))
        final_b = max(0, min(255, int(final_b)))

        return (final_r, final_g, final_b)

    def create_ppm_data(self, width, height, pixels):
        """Создание данных PPM формата"""
        header = f"P6\n{width} {height}\n255\n".encode()
        if isinstance(pixels, list):
            pixels = bytes(pixels)
        return header + pixels

    def save_image(self):
        """Сохранение преобразованного изображения"""
        if not self.transformed_image_data:
            showinfo("Ошибка", "Нет преобразованного изображения для сохранения")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".ppm",
            filetypes=[("PPM файлы", "*.ppm"), ("Все файлы", "*.*")],
            title="Сохранить преобразованное изображение"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'wb') as f:
                f.write(self.create_ppm_data(
                    self.transformed_image_data['width'],
                    self.transformed_image_data['height'],
                    self.transformed_image_data['pixels']
                ))
            showinfo("Успех", f"Изображение сохранено: {file_path}")
        except Exception as e:
            showinfo("Ошибка", f"Не удалось сохранить изображение: {e}")


def main():
    root = tk.Tk()
    app = ImageInterpolationApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()