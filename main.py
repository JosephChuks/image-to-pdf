from flask import Flask, abort, render_template, request, send_from_directory
from fpdf import FPDF
from werkzeug.utils import secure_filename
import os
import shutil
import uuid
from PIL import Image

app = Flask(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def convert_images_to_pdf(image_paths, output_pdf):

    if image_paths:
        with Image.open(image_paths[0]) as image:
            pdf = FPDF(unit="pt", format=image.size)
    else:
        pdf = FPDF()

    for image_path in image_paths:
        with Image.open(image_path) as image:
            width, height = image.size
        pdf.add_page(format=(width, height))
        pdf.image(image_path, x=0, y=0, w=width, h=height)
    pdf.output(output_pdf)


def job_dir(job_id):
    # Job ids are uuid4 hex strings; reject anything else so the id can't escape UPLOAD_DIR
    try:
        uuid.UUID(hex=job_id)
    except ValueError:
        abort(404)
    path = os.path.join(UPLOAD_DIR, job_id)
    if not os.path.isdir(path):
        abort(404)
    return path


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/convert")
def convert():
    images = [image for image in request.files.getlist("images") if image.filename]
    if not images:
        return render_template("_result.html", error="Please choose at least one image.")

    job_id = uuid.uuid4().hex
    folder = os.path.join(UPLOAD_DIR, job_id)
    os.makedirs(folder)

    image_paths = []
    for index, image in enumerate(images):
        # Prefix with the index so duplicate filenames don't overwrite each other
        filename = f"{index:03d}_{secure_filename(image.filename) or 'image'}"
        path = os.path.join(folder, filename)
        image.save(path)
        image_paths.append(path)

    stem = os.path.splitext(secure_filename(images[0].filename))[0] or "images"
    pdf_name = f"{stem}.pdf"

    try:
        convert_images_to_pdf(image_paths, os.path.join(folder, pdf_name))
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        return render_template(
            "_result.html", error="Couldn't convert those files. Are they all valid images?"
        )

    return render_template(
        "_result.html", job_id=job_id, pdf_name=pdf_name, page_count=len(image_paths)
    )


@app.get("/download/<job_id>/<pdf_name>")
def download(job_id, pdf_name):
    return send_from_directory(job_dir(job_id), pdf_name, as_attachment=True)


@app.post("/delete/<job_id>")
def delete(job_id):
    shutil.rmtree(job_dir(job_id))
    return render_template("_result.html", deleted=True)


if __name__ == "__main__":
    app.run(debug=True)
