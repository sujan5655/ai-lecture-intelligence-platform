import subprocess
from pathlib import Path

import pymupdf


def convert_pptx_to_pdf(pptx_path: str, output_directory: str) -> str:
    pptx = Path(pptx_path)
    output_dir = Path(output_directory)

    if not pptx.exists():
        raise FileNotFoundError(
            f"PPTX file not found: {pptx}"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(pptx),
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "PPTX to PDF conversion failed:\n"
            f"{result.stderr}"
        )

    pdf_path = output_dir / f"{pptx.stem}.pdf"

    if not pdf_path.exists():
        raise RuntimeError(
            "LibreOffice completed but PDF was not created."
        )

    return str(pdf_path)


def pdf_to_slide_images(
    pdf_path: str,
    output_directory: str,
):
    pdf = Path(pdf_path)
    output_dir = Path(output_directory)

    if not pdf.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf}"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = pymupdf.open(str(pdf))


    slides = []

    try:
        for page_number, page in enumerate(document):
            image_path = (
                output_dir
                / f"slide_{page_number + 1:04d}.png"
            )

            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False,
            )

            pixmap.save(str(image_path))

            slides.append(
                {
                    "slide_number": page_number + 1,
                    "path": str(image_path),
                    "width": pixmap.width,
                    "height": pixmap.height,
                }
            )
    finally:
        document.close()

    if not slides:
        raise RuntimeError(
            "No slides were generated from the PDF."
        )

    return slides



from pathlib import Path

from django.core.files import File

from lectures.models import Lecture, Slide


def process_lecture_slides(lecture: Lecture):
    if not lecture.slides_source:
        raise ValueError(
            "Lecture does not have a slide deck."
        )

    source_path = Path(
        lecture.slides_source.path
    )

    extension = source_path.suffix.lower()

    if extension not in [".pdf", ".pptx"]:
        raise ValueError(
            "Only PDF and PPTX files are supported."
        )

    output_directory = (
        Path("media")
        / "lectures"
        / "slides"
        / str(lecture.id)
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    pdf_path = source_path

    if extension == ".pptx":
        pdf_path = Path(
            convert_pptx_to_pdf(
                str(source_path),
                str(output_directory),
            )
        )

    slide_data = pdf_to_slide_images(
        str(pdf_path),
        str(output_directory),
    )

    Slide.objects.filter(
        lecture=lecture
    ).delete()

    created_slides = []

    for slide in slide_data:
        slide_number = slide["slide_number"]
        image_path = Path(slide["path"])

        slide_object = Slide(
            lecture=lecture,
            slide_number=slide_number,
            width=slide["width"],
            height=slide["height"],
        )

        with open(image_path, "rb") as image_file:
            slide_object.image.save(
                image_path.name,
                File(image_file),
                save=True,
            )

        created_slides.append(slide_object)

    return created_slides