# Image to PDF

A small Flask web app that converts one or more images into a single PDF, with one image per page.

- Drag and drop images, or click to choose them, and see thumbnails before converting
- Each page is sized to match its image
- Download the PDF, then delete the uploaded images and the PDF from the server with one click

Built with Flask, [fpdf2](https://py-pdf.github.io/fpdf2/), Pillow, htmx and Tailwind CSS.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Then open http://127.0.0.1:5000.

> Install `fpdf2`, not the old `fpdf` package. Both are imported as `fpdf`, but the old one doesn't support per-page sizes.

## How it works

Each conversion is saved in its own folder under `uploads/<job id>/`, holding the uploaded images and the generated PDF. The **Delete** button removes that folder. The `uploads/` folder is created automatically and is ignored by git.
