"""Rutas y opciones compartidas por las exportaciones de la tesis."""

import argparse
import os
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS = ROOT / "docs" / "tesis"
TEMP = ROOT / "tmp" / "redaccion"


def export_options(description, figures=False):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Permite reemplazar el PDF existente; nunca modifica el Markdown.",
    )
    if figures:
        parser.add_argument(
            "--regenerate-figures", action="store_true",
            help="Reemplaza las dos figuras PNG con los diagramas definidos en este script.",
        )
    return parser.parse_args()


def check_destination(path, overwrite):
    if path.exists() and not overwrite:
        raise SystemExit(f"Ya existe {path}. Para actualizar el PDF, usa --overwrite.")


def register_fonts(family):
    """Encuentra Times New Roman o una familia serif libre sin ruta de usuario fija."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_sets = [
        ("times.ttf", "timesbd.ttf", "timesi.ttf"),
        ("Times New Roman.ttf", "Times New Roman Bold.ttf", "Times New Roman Italic.ttf"),
        ("LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf", "LiberationSerif-Italic.ttf"),
        ("DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf", "DejaVuSerif-Italic.ttf"),
    ]
    configured = os.environ.get("THESIS_FONT_DIR")
    directories = [Path(configured)] if configured else [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
        Path("/Library/Fonts"),
        Path("/System/Library/Fonts/Supplemental"),
        Path("/usr/share/fonts/truetype/liberation2"),
        Path("/usr/share/fonts/truetype/liberation"),
        Path("/usr/share/fonts/truetype/dejavu"),
    ]
    for directory in directories:
        for filenames in font_sets:
            if all((directory / filename).is_file() for filename in filenames):
                for suffix, filename in zip(("", "-Bold", "-Italic"), filenames):
                    pdfmetrics.registerFont(TTFont(family + suffix, str(directory / filename)))
                pdfmetrics.registerFontFamily(
                    family, normal=family, bold=family + "-Bold",
                    italic=family + "-Italic", boldItalic=family + "-Bold",
                )
                return
    raise SystemExit("No se encontraron fuentes serif compatibles. Define THESIS_FONT_DIR; consulta docs/tesis/README.md.")


def pdftoppm_executable():
    configured = os.environ.get("PDFTOPPM")
    executable = shutil.which(configured or "pdftoppm")
    if not executable:
        raise SystemExit("Para regenerar figuras instala Poppler y añade pdftoppm a PATH, o define PDFTOPPM.")
    return executable
