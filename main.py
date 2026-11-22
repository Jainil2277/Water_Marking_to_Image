import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ============= Color Palette (Light Theme) =============
BG_COLOR = "#f8fafc"
CARD_BG = "#ffffff"
BORDER_COLOR = "#cbd5e1"
TEXT_COLOR = "#1e293b"
MUTED_TEXT = "#64748b"
PRIMARY_BLUE = "#2563eb"
SUCCESS_GREEN = "#16a34a"
SECONDARY_BTN = "#e2e8f0"

PREVIEW_W = 640
PREVIEW_H = 480

# ============= App State initially =============
original_img = None
base_preview = None
display_photo = None
canvas_img_id = None
canvas_placeholder_id = None


# ============= Image Processing Helper =============
def get_font(font_size: int):
    font_candidates = [
        "arial.ttf",
        "DejaVuSans-Bold.ttf",
        "LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in font_candidates:
        try:
            return ImageFont.truetype(path, font_size)
        except OSError:
            continue
    return ImageFont.load_default()


def apply_watermark(
    source_img: Image.Image,
    text: str,
    x_percent: float,
    y_percent: float,
    opacity: int,
    font_scale_percent: int,
    color_mode: str,
    is_preview: bool = False,
) -> Image.Image:
    """Draws watermark text onto a copy of source_img using percentage coordinates."""
    working_copy = source_img.copy().convert("RGBA")
    txt_layer = Image.new("RGBA", working_copy.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    scale_factor = font_scale_percent / 100.0
    base_min = 14 if is_preview else 24
    font_size = max(base_min, int(working_copy.height * 0.05 * scale_factor))
    font = get_font(font_size)

    x = int(working_copy.width * (x_percent / 100.0))
    y = int(working_copy.height * (y_percent / 100.0))

    rgb = (255, 255, 255) if color_mode == "White" else (20, 20, 20)
    fill_color = (*rgb, int(opacity))

    draw.text((x, y), text, fill=fill_color, font=font)
    composited = Image.alpha_composite(working_copy, txt_layer)

    return composited if is_preview else composited.convert("RGB")


# ============= UI Callbacks =============
def update_preview(*args):
    global base_preview, display_photo, canvas_img_id, canvas_placeholder_id
    if base_preview is None:
        return

    text = text_entry.get().strip() or "Watermark Preview"

    watermarked_preview = apply_watermark(
        source_img=base_preview,
        text=text,
        x_percent=slider_x.get(),
        y_percent=slider_y.get(),
        opacity=slider_opacity.get(),
        font_scale_percent=slider_size.get(),
        color_mode=color_var.get(),
        is_preview=True,
    )

    display_photo = ImageTk.PhotoImage(watermarked_preview)

    if canvas_placeholder_id is not None:
        preview_canvas.delete(canvas_placeholder_id)
        canvas_placeholder_id = None


    cx = PREVIEW_W // 2
    cy = PREVIEW_H // 2
    if canvas_img_id is None:
        canvas_img_id = preview_canvas.create_image(cx, cy, image=display_photo, anchor="center")
    else:
        preview_canvas.itemconfig(canvas_img_id, image=display_photo)

    preview_canvas.image = display_photo


def load_image():
    global original_img, base_preview
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")],
    )
    if not file_path:
        return

    try:
        loaded = Image.open(file_path)
    except OSError as exc:
        messagebox.showerror("Error", f"Could not open image:\n{exc}")
        return

    original_img = loaded.convert("RGBA")

    preview = original_img.copy()
    preview.thumbnail((PREVIEW_W - 24, PREVIEW_H - 24))
    base_preview = preview.convert("RGBA")

    update_preview()


def save_image():
    if original_img is None:
        messagebox.showwarning("Warning", "Please select an image first!")
        return

    text = text_entry.get().strip()
    if not text:
        messagebox.showwarning("Warning", "Please enter watermark text!")
        return

    final_img = apply_watermark(
        source_img=original_img,
        text=text,
        x_percent=slider_x.get(),
        y_percent=slider_y.get(),
        opacity=slider_opacity.get(),
        font_scale_percent=slider_size.get(),
        color_mode=color_var.get(),
        is_preview=False,
    )

    save_path = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", "*.png")],
    )
    if save_path:
        final_img.save(save_path)
        messagebox.showinfo("Success", "Watermarked image saved successfully!")


def set_preset(x_val: int, y_val: int):
    slider_x.set(x_val)
    slider_y.set(y_val)
    update_preview()


def reset_controls():
    text_entry.delete(0, tk.END)
    text_entry.insert(0, "Confidential")
    slider_x.set(60)
    slider_y.set(85)
    slider_opacity.set(170)
    slider_size.set(100)
    color_var.set("White")
    update_preview()


# ============= Window Setup UI =============
window = tk.Tk()
window.title("Image Watermarker")
window.config(padx=24, pady=24, bg=BG_COLOR)
window.resizable(False, False)


image_frame = tk.Frame(
    window,
    bg=CARD_BG,
    highlightbackground=BORDER_COLOR,
    highlightthickness=1,
)
image_frame.grid(row=0, column=0, padx=(0, 24), sticky="n")

preview_canvas = tk.Canvas(
    image_frame,
    width=PREVIEW_W,
    height=PREVIEW_H,
    bg=CARD_BG,
    highlightthickness=0,
)
preview_canvas.pack(padx=10, pady=10)

canvas_placeholder_id = preview_canvas.create_text(
    PREVIEW_W // 2,
    PREVIEW_H // 2,
    text="No Image Loaded\nClick 'Browse Image' to get started",
    font=("Segoe UI", 12),
    fill=MUTED_TEXT,
    justify="center",
)

# Right Column: Controls Panel
control_frame = tk.Frame(window, bg=BG_COLOR)
control_frame.grid(row=0, column=1, sticky="n")

tk.Label(
    control_frame,
    text="Watermark Controls",
    font=("Segoe UI", 16, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR,
).pack(anchor="w", pady=(0, 12))

# Watermark Text
tk.Label(
    control_frame,
    text="Watermark Text",
    font=("Segoe UI", 10, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR,
).pack(anchor="w")

text_entry = tk.Entry(
    control_frame,
    font=("Segoe UI", 11),
    width=28,
    bg=CARD_BG,
    fg=TEXT_COLOR,
    highlightbackground=BORDER_COLOR,
    highlightthickness=1,
    relief="flat",
)
text_entry.pack(anchor="w", pady=(4, 12), ipady=5)
text_entry.insert(0, "Confidential")
text_entry.bind("<KeyRelease>", update_preview)

# Text Color Selector
tk.Label(
    control_frame,
    text="Text Color",
    font=("Segoe UI", 9, "bold"),
    bg=BG_COLOR,
    fg=MUTED_TEXT,
).pack(anchor="w")

color_var = tk.StringVar(value="White")
color_menu = tk.OptionMenu(control_frame, color_var, "White", "Black", command=update_preview)
color_menu.config(
    font=("Segoe UI", 10),
    bg=CARD_BG,
    fg=TEXT_COLOR,
    highlightthickness=1,
    highlightbackground=BORDER_COLOR,
    relief="flat",
    width=24,
)
color_menu.pack(anchor="w", pady=(4, 12))

# Position X Slider
tk.Label(
    control_frame,
    text="Horizontal Position X (%)",
    font=("Segoe UI", 9, "bold"),
    bg=BG_COLOR,
    fg=MUTED_TEXT,
).pack(anchor="w")

slider_x = tk.Scale(
    control_frame,
    from_=0,
    to=100,
    orient="horizontal",
    command=update_preview,
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    highlightthickness=0,
    troughcolor="#e2e8f0",
    length=260,
)
slider_x.set(60)
slider_x.pack(anchor="w", pady=(0, 8))

# Position Y Slider
tk.Label(
    control_frame,
    text="Vertical Position Y (%)",
    font=("Segoe UI", 9, "bold"),
    bg=BG_COLOR,
    fg=MUTED_TEXT,
).pack(anchor="w")

slider_y = tk.Scale(
    control_frame,
    from_=0,
    to=100,
    orient="horizontal",
    command=update_preview,
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    highlightthickness=0,
    troughcolor="#e2e8f0",
    length=260,
)
slider_y.set(85)
slider_y.pack(anchor="w", pady=(0, 8))

# Opacity Slider
tk.Label(
    control_frame,
    text="Opacity (0 - 255)",
    font=("Segoe UI", 9, "bold"),
    bg=BG_COLOR,
    fg=MUTED_TEXT,
).pack(anchor="w")

slider_opacity = tk.Scale(
    control_frame,
    from_=20,
    to=255,
    orient="horizontal",
    command=update_preview,
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    highlightthickness=0,
    troughcolor="#e2e8f0",
    length=260,
)
slider_opacity.set(170)
slider_opacity.pack(anchor="w", pady=(0, 8))

# Font Scale Slider
tk.Label(
    control_frame,
    text="Font Scale (%)",
    font=("Segoe UI", 9, "bold"),
    bg=BG_COLOR,
    fg=MUTED_TEXT,
).pack(anchor="w")

slider_size = tk.Scale(
    control_frame,
    from_=40,
    to=250,
    orient="horizontal",
    command=update_preview,
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    highlightthickness=0,
    troughcolor="#e2e8f0",
    length=260,
)
slider_size.set(100)
slider_size.pack(anchor="w", pady=(0, 12))

# Quick Position Presets
preset_frame = tk.Frame(control_frame, bg=BG_COLOR)
preset_frame.pack(anchor="w", pady=(0, 14))

tk.Button(
    preset_frame,
    text="Top Left",
    font=("Segoe UI", 8, "bold"),
    command=lambda: set_preset(5, 5),
    bg=SECONDARY_BTN,
    fg=TEXT_COLOR,
    relief="flat",
    cursor="hand2",
    padx=8,
    pady=4,
).pack(side="left", padx=(0, 6))

tk.Button(
    preset_frame,
    text="Center",
    font=("Segoe UI", 8, "bold"),
    command=lambda: set_preset(40, 48),
    bg=SECONDARY_BTN,
    fg=TEXT_COLOR,
    relief="flat",
    cursor="hand2",
    padx=8,
    pady=4,
).pack(side="left", padx=(0, 6))

tk.Button(
    preset_frame,
    text="Bottom Right",
    font=("Segoe UI", 8, "bold"),
    command=lambda: set_preset(60, 85),
    bg=SECONDARY_BTN,
    fg=TEXT_COLOR,
    relief="flat",
    cursor="hand2",
    padx=8,
    pady=4,
).pack(side="left")

# Action Buttons
tk.Button(
    control_frame,
    text="📁 Browse Image",
    font=("Segoe UI", 10, "bold"),
    command=load_image,
    bg=PRIMARY_BLUE,
    fg="white",
    activebackground="#1d4ed8",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    width=26,
    pady=7,
).pack(pady=(0, 8))

tk.Button(
    control_frame,
    text="💾 Save Watermarked Image",
    font=("Segoe UI", 10, "bold"),
    command=save_image,
    bg=SUCCESS_GREEN,
    fg="white",
    activebackground="#15803d",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    width=26,
    pady=7,
).pack(pady=(0, 8))

tk.Button(
    control_frame,
    text="↺ Reset Settings",
    font=("Segoe UI", 9, "bold"),
    command=reset_controls,
    bg=SECONDARY_BTN,
    fg=TEXT_COLOR,
    relief="flat",
    cursor="hand2",
    width=28,
    pady=5,
).pack()

window.mainloop()