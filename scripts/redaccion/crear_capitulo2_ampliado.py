from pathlib import Path
from _common import DOCUMENTS, TEMP, check_destination, export_options, pdftoppm_executable, register_fonts

options = export_options('Exporta el capítulo 2 ampliado desde su Markdown y figuras actuales.', figures=True)
import re, subprocess, json
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, PageBreak, Table, TableStyle, KeepTogether, Spacer, Image
from reportlab.graphics.shapes import Drawing, Rect, Line, Polygon, String
from reportlab.graphics import renderPDF
from pypdf import PdfReader

OUT=DOCUMENTS
TMP=TEMP
ASSETS=OUT/'figuras_capitulo2'
SOURCE=OUT/'Capitulo_2_Marco_teorico_ampliado.md'
PDF=SOURCE.with_suffix('.pdf')
check_destination(PDF, options.overwrite)
register_fonts('Thesis')
TMP.mkdir(parents=True, exist_ok=True)
BLUE=colors.HexColor('#234C6B')
ORANGE=colors.HexColor('#AB5E25')
GREEN=colors.HexColor('#D8E7DC')
INK=colors.HexColor('#20252A')

def label(d,x,y,text,size=10,bold=False,color=INK,anchor='middle'):
    d.add(String(x,y,text,fontName='Thesis-Bold' if bold else 'Thesis',fontSize=size,fillColor=color,textAnchor=anchor))

def arrow(d,x1,y,x2):
    d.add(Line(x1,y,x2-4,y,strokeColor=BLUE,strokeWidth=1.2))
    d.add(Polygon([x2,y,x2-5,y+3,x2-5,y-3],fillColor=BLUE,strokeColor=BLUE))

def yolo_figure():
    d=Drawing(475,150)
    stages=[(0,95,'Entrada',['Imagen RGB','y ajuste de tamaño']),
            (110,105,'Backbone',['Extracción de','características']),
            (230,105,'Neck',['Combinación de','varias escalas']),
            (350,125,'Head',['Coordenadas y','puntuaciones'])]
    for x,w,title,lines in stages:
        d.add(Rect(x,65,w,65,rx=3,ry=3,strokeColor=BLUE,strokeWidth=1,fillColor=colors.HexColor('#F1F5F8')))
        label(d,x+w/2,112,title,11,True,BLUE)
        for i,t in enumerate(lines): label(d,x+w/2,94-i*13,t,10)
    for a,b in zip(stages,stages[1:]):arrow(d,a[0]+a[1]+3,97,b[0]-3)
    label(d,237.5,40,'Ejemplo de entrada cuadrada: 640 × 640 píxeles',10)
    label(d,237.5,22,'Mapas recibidos por la cabeza: 80 × 80, 40 × 40 y 20 × 20 posiciones',10)
    return d

def iou_figure():
    d=Drawing(475,208)
    label(d,237.5,192,'Caja de referencia: 1000 px²   |   Caja predicha: 1200 px²',10)
    for panel,x0 in [('Intersección',39),('Unión',286)]:
        label(d,x0+67.2,168,panel,11,True,BLUE)
        scale=2.8; x=x0; y=56; dx=8*scale; rw=40*scale; rh=25*scale; ph=30*scale
        if panel=='Intersección':
            d.add(Rect(x+dx,y,rw-dx,rh,fillColor=GREEN,strokeColor=None))
        else:
            d.add(Polygon([x,y,x+dx+rw,y,x+dx+rw,y+ph,x+dx,y+ph,x+dx,y+rh,x,y+rh],fillColor=GREEN,strokeColor=None))
        d.add(Rect(x,y,rw,rh,fillColor=None,strokeColor=BLUE,strokeWidth=1.6))
        d.add(Rect(x+dx,y,rw,ph,fillColor=None,strokeColor=ORANGE,strokeWidth=1.6,strokeDashArray=[4,2]))
        label(d,x+67.2,38,'Área: 800 px²' if panel=='Intersección' else 'Área: 1400 px²',10)
    d.add(Line(70,13,88,13,strokeColor=BLUE,strokeWidth=1.6));label(d,93,10,'Referencia',9,anchor='start')
    d.add(Line(185,13,203,13,strokeColor=ORANGE,strokeWidth=1.6,strokeDashArray=[4,2]));label(d,208,10,'Predicción',9,anchor='start')
    d.add(Rect(310,8,14,9,fillColor=GREEN,strokeColor=None));label(d,330,10,'Área considerada',9,anchor='start')
    return d

FIGURES={'estructura_yolo':yolo_figure,'interseccion_union':iou_figure}
if options.regenerate_figures:
    poppler = pdftoppm_executable()
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name,build in FIGURES.items():
        intermediate=TMP/(name+'.pdf')
        renderPDF.drawToFile(build(),str(intermediate))
        subprocess.run([poppler,'-r','220','-png','-singlefile',str(intermediate),str(ASSETS/name)],check=True,capture_output=True)

styles={
 'body':ParagraphStyle('body',fontName='Thesis',fontSize=12,leading=17,alignment=TA_JUSTIFY,spaceAfter=9,allowWidows=0,allowOrphans=0),
 'chapter':ParagraphStyle('chapter',fontName='Thesis-Bold',fontSize=18,leading=23,spaceAfter=20,keepWithNext=True),
 'section':ParagraphStyle('section',fontName='Thesis-Bold',fontSize=13,leading=17,spaceBefore=13,spaceAfter=10,keepWithNext=True),
 'sub':ParagraphStyle('sub',fontName='Thesis-Bold',fontSize=12,leading=16,spaceBefore=10,spaceAfter=8,keepWithNext=True),
 'ref':ParagraphStyle('ref',fontName='Thesis',fontSize=10.5,leading=13.5,spaceAfter=7,alignment=TA_LEFT,allowWidows=0,allowOrphans=0),
 'eq':ParagraphStyle('eq',fontName='Thesis',fontSize=12,leading=17,alignment=TA_CENTER),
 'caption':ParagraphStyle('caption',fontName='Thesis-Italic',fontSize=10,leading=13,alignment=TA_LEFT,spaceBefore=5,spaceAfter=12),
 'cell':ParagraphStyle('cell',fontName='Thesis',fontSize=10.5,leading=13,alignment=TA_LEFT),
 'cellhead':ParagraphStyle('cellhead',fontName='Thesis-Bold',fontSize=10.5,leading=13,alignment=TA_LEFT),
}

class ChapterPDF(BaseDocTemplate):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.heading_id=0
        f=Frame(self.leftMargin,self.bottomMargin,self.width,self.height,id='main',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='main',frames=f,onPage=self.page_marks))
    def page_marks(self,c,doc):
        c.saveState(); c.setFont('Thesis',9); c.setFillColor(colors.HexColor('#666666'))
        c.drawString(self.leftMargin,letter[1]-36,'Detección de agave para apoyar el deshierbe autónomo')
        c.drawRightString(letter[0]-self.rightMargin,letter[1]-36,'Borrador revisado · 28 octubre 2026')
        c.setStrokeColor(colors.HexColor('#CCCCCC'))
        c.line(self.leftMargin,letter[1]-44,letter[0]-self.rightMargin,letter[1]-44)
        c.setFont('Thesis',10);c.drawCentredString(letter[0]/2,34,str(doc.page));c.restoreState()
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and f.style.name in ['chapter','section','sub']:
            self.heading_id+=1;key='head'+str(self.heading_id)
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f.getPlainText(),key,{'chapter':0,'section':1,'sub':2}[f.style.name],False)

def rich(s):
    s=s.replace('–','-').replace('—','-').replace('\u2011','-')
    s=escape(s)
    s=re.sub(r'\[([^\]]+)\]\((https://[^)]+)\)',lambda m:f'<link href="{m.group(2)}" color="#254B6F">{m.group(1)}</link>',s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
    for digit,num in [('₁','1'),('₂','2')]:s=s.replace(digit,'<sub>'+num+'</sub>')
    s=re.sub(r'\b(x|y|A|AP)_([cpriK])\b',r'\1<sub>\2</sub>',s)
    return s

doc=ChapterPDF(str(PDF),pagesize=letter,leftMargin=72,rightMargin=65,topMargin=64,bottomMargin=59,
 title='Capítulo 2. Marco teórico: versión ampliada',author='Raúl Eduardo Venegas Reyes',
 subject='Estructura YOLO, aumento de datos y evaluación de detección de agave')
story=[];references=False
for raw in SOURCE.read_text(encoding='utf-8').split('\n\n'):
    p=raw.strip()
    if not p:continue
    if p.startswith('# '):
        if story:story.append(PageBreak())
        references='Referencias' in p
        story.append(Paragraph(rich(p[2:]),styles['chapter']))
    elif p.startswith('## '):story.append(Paragraph(rich(p[3:]),styles['section']))
    elif p.startswith('### '):story.append(Paragraph(rich(p[4:]),styles['sub']))
    elif references:story.append(Paragraph(rich(p),styles['ref']))
    elif p.startswith('!['):
        m=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',p)
        if not m:raise ValueError('Bad image syntax')
        figure_path = SOURCE.parent / m[2].strip('<>')
        figure = Image(str(figure_path))
        scale = min(1, doc.width / figure.imageWidth)
        figure.drawWidth = figure.imageWidth * scale
        figure.drawHeight = figure.imageHeight * scale
        story.append(KeepTogether([Spacer(1,3),figure,Paragraph(rich(m[1]),styles['caption'])]))
    elif p.startswith('|'):
        rows=[]
        for line in p.splitlines():
            cells=[s.strip() for s in line.strip().strip('|').split('|')]
            if all(re.fullmatch(r'[:\- ]+',c) for c in cells):continue
            rows.append(cells)
        widths=[doc.width*.25,doc.width*.37,doc.width*.38]
        if 'Predicción / referencia' in rows[0][0]:widths=[doc.width*.44,doc.width*.28,doc.width*.28]
        data=[[Paragraph(rich(s),styles['cellhead' if i==0 else 'cell']) for s in row] for i,row in enumerate(rows)]
        table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EDF2F5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.8,BLUE),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#C9D1D7')),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]))
        story.extend([Spacer(1,4),table,Spacer(1,13)])
    elif re.search(r'\(2\.\d+\)$',p):
        eq,num=re.split(r'\s+(?=\(2\.\d+\)$)',p,maxsplit=1)
        table=Table([[Paragraph(rich(eq),styles['eq']),Paragraph(num,styles['eq'])]],colWidths=[doc.width-44,44])
        table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),11)]))
        story.append(table)
    else:story.append(Paragraph(rich(p),styles['body']))
doc.build(story)
r=PdfReader(PDF)
alltext='\n'.join(p.extract_text() for p in r.pages)
report={'pdf':str(PDF),'pages':len(r.pages),'words':len(SOURCE.read_text(encoding='utf-8').split()),
 'references_complete':all(f'[{i}]' in alltext for i in range(1,26)),
 'equations_complete':all(f'(2.{i})' in alltext for i in range(1,10)),
 'missing_unicode':alltext.count('\ufffd'),'page_chars':[len(p.extract_text()) for p in r.pages]}
(TMP/'verificacion_capitulo2_ampliado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True))
