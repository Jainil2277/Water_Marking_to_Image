# Image Watermarker

A desktop GUI application built with Python, **Tkinter**, and **Pillow (PIL)** to add custom text watermarks to images with a live preview before saving. Built as part of the 100 Days of Code Python course.

## Features

- **Live Preview:** See watermark text, position, opacity, and size updates in real time on a preview canvas.
- **Position Controls:** Adjust horizontal (`X %`) and vertical (`Y %`) placement via sliders or use quick presets (*Top Left*, *Center*, *Bottom Right*).
- **Customization:** Choose watermark text, switch between White and Black text, and adjust opacity and font scale.
- **Full-Resolution Export:** Applies the watermark to the original loaded image and saves it as a `.jpg` or `.png` file.
- **Reset Option:** Quickly restore default settings with one click.

## Project Structure

```text
├── main.py          # Tkinter UI and Pillow watermarking logic
├── .gitignore       # Ignored files and folders (cache, virtual env, IDE files)
└── README.md        # Project documentation
