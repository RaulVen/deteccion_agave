from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "reportes" / "Reporte_optimizadores_lr_aumentacion_agave.docx"
RESULTS = ROOT / "docs" / "results"

BLUE = RGBColor(46, 116, 181)
DARK_BLUE = RGBColor(31, 77, 120)
INK = RGBColor(34, 34, 34)
MUTED = RGBColor(90, 90, 90)
FILL = "F2F4F7"
CALLOUT = "E8EEF5"


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def margins(cell) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for name, value in {"top": 80, "bottom": 80, "start": 120, "end": 120}.items():
        node = tc_mar.find(qn(f"w:{name}"))
        if node is None:
            node = OxmlElement(f"w:{name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def style_table(table, widths: list[float], header=True) -> None:
    table.style = "Table Grid"
    table.autofit = False
    for row in table.rows:
        for i, width in enumerate(widths):
            row.cells[i].width = Inches(width)
            row.cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            margins(row.cells[i])
    if header:
        tr_pr = table.rows[0]._tr.get_or_add_trPr()
        tbl_header = OxmlElement("w:tblHeader")
        tbl_header.set(qn("w:val"), "true")
        tr_pr.append(tbl_header)
        for cell in table.rows[0].cells:
            shade(cell, FILL)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.bold = True
                    r.font.size = Pt(9)
    for row in table.rows[1:]:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)


def configure(doc: Document) -> None:
    section = doc.sections[0]
    section.orientation = WD_ORIENT.PORTRAIT
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.1
    for name, size, color in [("Heading 1", 16, BLUE), ("Heading 2", 13, BLUE), ("Heading 3", 12, DARK_BLUE)]:
        st = doc.styles[name]
        st.font.name = "Calibri"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = color


def title(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Optimizadores, learning rate y aumentacion de datos")
    r.bold = True
    r.font.size = Pt(21)
    r.font.color.rgb = DARK_BLUE
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Experimentos YOLO26 para deteccion de agave")
    r.font.size = Pt(12)
    r.font.color.rgb = MUTED


def callout(doc: Document, label: str, text: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.rows[0].cells[0].text = ""
    style_table(table, [6.3], header=False)
    cell = table.rows[0].cells[0]
    shade(cell, CALLOUT)
    p = cell.paragraphs[0]
    r = p.add_run(label + ": ")
    r.bold = True
    r.font.color.rgb = DARK_BLUE
    p.add_run(text)
    doc.add_paragraph()


def bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(4)
        p.add_run(item)


def kv(doc: Document, rows: list[tuple[str, str]]) -> None:
    table = doc.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Elemento"
    table.rows[0].cells[1].text = "Detalle"
    for key, value in rows:
        cells = table.add_row().cells
        cells[0].text = key
        cells[1].text = value
    style_table(table, [1.75, 4.55])


def concepts(doc: Document, rows: list[tuple[str, str]]) -> None:
    table = doc.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Concepto"
    table.rows[0].cells[1].text = "Explicacion"
    for key, value in rows:
        cells = table.add_row().cells
        cells[0].text = key
        cells[1].text = value
    style_table(table, [1.55, 4.75])


def image(doc: Document, path: Path, caption: str, width=6.1) -> None:
    if not path.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = MUTED


def optimizer_table(doc: Document) -> None:
    rows = [
        ("auto", "Ultralytics selecciona el optimizador internamente.", "Corridas iniciales y de campo.", "Exploracion rapida sin fijar manualmente el algoritmo."),
        ("AdamW", "Optimizador adaptativo con weight decay desacoplado.", "Varias corridas con LR bajo y cambios de loss.", "Aprende rapido y ajusta el paso por parametro; util para explorar estabilidad."),
        ("SGD", "Descenso de gradiente estocastico.", "Modelo ganador yolo26s_sgd_cos_slow_120e.", "Mas simple; puede generalizar bien si se combina con LR adecuado y scheduler."),
    ]
    table = doc.add_table(rows=1, cols=4)
    headers = ["Optimizador", "Que hace", "Donde se uso", "Interpretacion"]
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = value
    style_table(table, [0.9, 1.8, 1.8, 1.8])


def lr_table(doc: Document) -> None:
    rows = [
        ("auto / campo inicial", "0.01", "0.01", "false", "yolo26n/yolo26s field_aug y medium_aug"),
        ("AdamW bajo", "0.001", "0.02", "true", "yolo26s_adamw_cos_low_lr_120e"),
        ("AdamW box focus", "0.0012", "0.02", "true", "yolo26s_adamw_box_focus_120e"),
        ("AdamW balanced", "0.002", "0.05", "true", "yolo26s_coslr_balanced_45e"),
        ("AdamW box/dfl loss", "0.002", "0.01", "false", "yolo26s_loss_box_dfl_45e"),
        ("AdamW precision loss", "0.0015", "0.01", "false", "yolo26s_loss_precision_45e"),
        ("SGD ganador", "0.005", "0.01", "true", "yolo26s_sgd_cos_slow_120e"),
    ]
    table = doc.add_table(rows=1, cols=5)
    headers = ["Grupo", "lr0", "lrf", "cos_lr", "Corridas"]
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = value
    style_table(table, [1.35, 0.65, 0.65, 0.65, 3.0])


def augmentation_table(doc: Document) -> None:
    rows = [
        ("hsv_h=0.02", "Variacion leve de tono/color.", "Ayuda ante cambios de iluminacion o color de escena."),
        ("hsv_s=0.55", "Variacion de saturacion.", "Simula colores mas apagados o intensos."),
        ("hsv_v=0.35", "Variacion de brillo.", "Simula sombra o sol mas fuerte."),
        ("scale=0.35", "Cambia tamano aparente del objeto.", "Simula distancia de camara."),
        ("shear=2", "Deforma levemente la geometria.", "Simula pequenas variaciones de angulo."),
        ("perspective=0.0005", "Cambio minimo de perspectiva.", "Simula inclinacion ligera de camara."),
        ("flipud=0.5", "Volteo vertical con probabilidad 50%.", "Aumenta variabilidad espacial."),
        ("fliplr=0.5", "Volteo horizontal con probabilidad 50%.", "Simula surcos o recorridos en sentido contrario."),
        ("mixup=0.05", "Mezcla dos imagenes.", "Regulariza y reduce dependencia de una sola escena."),
        ("erasing=0.15", "Tapa regiones pequenas.", "Ayuda a robustez ante oclusion parcial."),
        ("mosaic=0.0", "Mosaic desactivado.", "Se evito mezclar escenas agresivamente en el modelo ganador."),
        ("degrees=0", "Rotacion desactivada.", "Se elimino rotacion para no deformar demasiado la escena real."),
        ("translate=0.0", "Traslacion desactivada.", "Se elimino desplazamiento artificial."),
        ("cutmix=0.0", "CutMix desactivado.", "No se uso en el modelo ganador."),
    ]
    table = doc.add_table(rows=1, cols=3)
    headers = ["Parametro", "Que modifica", "Por que importa"]
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = value
    style_table(table, [1.35, 2.25, 2.7])


def build() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    configure(doc)
    title(doc)

    callout(
        doc,
        "Objetivo",
        "Explicar los optimizadores, learning rates, aumentos de datos y conteos exactos de imagenes usados en los experimentos YOLO26 para deteccion de agave.",
    )

    doc.add_heading("1. Modelo ganador y resultado final", level=1)
    kv(
        doc,
        [
            ("Modelo ganador", "yolo26s_sgd_cos_slow_120e"),
            ("Modelo base", "yolo26s.pt"),
            ("Peso final", "runs/detect/agave_experiments/yolo26s_sgd_cos_slow_120e/weights/best.pt"),
            ("Optimizador", "SGD"),
            ("Learning rate inicial", "lr0=0.005"),
            ("Learning rate final relativo", "lrf=0.01"),
            ("Scheduler", "cos_lr=true"),
            ("Epocas corridas", "86"),
            ("Mejor epoca reportada", "56"),
            ("Metricas test", "Precision=0.693, Recall=0.615, mAP50=0.654, mAP50-95=0.213"),
        ],
    )

    doc.add_heading("2. Optimizadores usados", level=1)
    doc.add_paragraph(
        "Un optimizador es el algoritmo que actualiza los pesos de la red neuronal durante el entrenamiento. En cada iteracion, el modelo calcula un error o perdida; el optimizador decide como cambiar los pesos para reducir ese error."
    )
    optimizer_table(doc)
    concepts(
        doc,
        [
            ("SGD", "Actualiza los pesos siguiendo la direccion contraria al gradiente. Es simple y puede generalizar bien, aunque puede requerir mas cuidado en el learning rate."),
            ("AdamW", "Usa estimaciones adaptativas del gradiente y desacopla weight decay. Suele aprender rapido, pero no siempre supera a SGD en datasets pequenos."),
            ("auto", "Permite que Ultralytics seleccione internamente una configuracion de optimizacion; fue util para corridas iniciales."),
        ],
    )

    doc.add_heading("3. Learning rate utilizado", level=1)
    doc.add_paragraph(
        "El learning rate controla el tamano del paso con el que el modelo modifica sus pesos. Si el valor es demasiado alto, el modelo puede volverse inestable. Si es demasiado bajo, puede aprender muy lento o quedarse en una solucion limitada."
    )
    lr_table(doc)
    callout(
        doc,
        "Learning rate del modelo ganador",
        "La corrida ganadora uso SGD con lr0=0.005, lrf=0.01 y cos_lr=true. Esto significa que el aprendizaje inicio con un paso moderado y fue disminuyendo con una curva tipo coseno durante el entrenamiento.",
    )

    doc.add_heading("4. Aumento de datos usado", level=1)
    doc.add_paragraph(
        "El aumento de datos consiste en transformar imagenes durante el entrenamiento para que el modelo observe variaciones sin crear manualmente nuevos archivos. En YOLO estas transformaciones se aplican en linea; por eso no quedan guardadas como imagenes nuevas en el dataset."
    )
    augmentation_table(doc)
    image(
        doc,
        RESULTS / "augmentation_examples_agave.jpg",
        "Figura 1. Ejemplos visuales de aumento de datos sobre una imagen real del dataset de agave.",
        width=6.3,
    )
    callout(
        doc,
        "Aclaracion sobre blur",
        "La imagen incluye blur como referencia visual para explicar robustez ante desenfoque, pero blur no aparece como parametro explicito en la configuracion ganadora. Los aumentos confirmados del modelo ganador fueron HSV, scale, shear, perspective, flipud, fliplr, mixup y erasing.",
    )

    doc.add_heading("5. Conteo exacto de imagenes", level=1)
    doc.add_paragraph(
        "Es importante distinguir entre imagenes fisicas guardadas en disco e imagenes presentadas al modelo durante el entrenamiento. Los aumentos de YOLO se aplican en vivo, por lo que no se generaron archivos adicionales de imagenes aumentadas."
    )
    kv(
        doc,
        [
            ("Imagenes train fisicas", "295"),
            ("Imagenes validation fisicas", "73"),
            ("Imagenes test fisicas", "36"),
            ("Total fisico del dataset", "404"),
            ("Imagenes aumentadas guardadas en disco", "0"),
            ("Epocas del modelo ganador", "86"),
            ("Presentaciones de entrenamiento del ganador", "295 x 86 = 25,370"),
            ("Presentaciones si hubiera completado 120 epocas", "295 x 120 = 35,400"),
            ("Presentaciones acumuladas en todos los experimentos", "173,755"),
        ],
    )
    callout(
        doc,
        "Redaccion recomendada para tesis",
        "El conjunto de entrenamiento estuvo compuesto por 295 imagenes reales. Durante el entrenamiento del modelo ganador, YOLO aplico aumentos de datos en linea, por lo que no se generaron archivos nuevos de imagenes aumentadas. El entrenamiento ejecuto 86 epocas, por lo que el modelo proceso 25,370 presentaciones de imagenes de entrenamiento, cada una con posibilidad de recibir transformaciones como variaciones HSV, flip horizontal, flip vertical, escala, shear, perspectiva, MixUp y Erasing.",
    )

    doc.add_heading("6. Resumen interpretativo", level=1)
    bullets(
        doc,
        [
            "Se probaron optimizadores auto, AdamW y SGD.",
            "El mejor resultado se obtuvo con SGD, learning rate inicial 0.005 y scheduler coseno.",
            "AdamW se uso para explorar learning rates bajos y cambios en pesos de perdida, pero no supero al modelo ganador.",
            "Los aumentos de datos fueron aplicados en linea, no como nuevas imagenes guardadas.",
            "El modelo ganador uso 295 imagenes reales de entrenamiento y las proceso durante 86 epocas.",
            "El dato exacto para reportar con aumentacion en linea es 25,370 presentaciones de entrenamiento.",
        ],
    )

    doc.save(OUT)


if __name__ == "__main__":
    build()
