from pathlib import Path
from _common import DOCUMENTS, check_destination, export_options, register_fonts

options = export_options('Exporta el borrador histórico del capítulo 2 del 27 de octubre.')
import re
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle
from pypdf import PdfReader

source = DOCUMENTS/'Capitulo_2_Marco_teorico_2026-10-27.md'
out = source.with_suffix('.pdf')
check_destination(out, options.overwrite)
register_fonts('Thesis')
styles = {
    'body': ParagraphStyle('body',fontName='Thesis',fontSize=12,leading=17,alignment=TA_JUSTIFY,spaceAfter=9,allowWidows=0,allowOrphans=0),
    'chapter': ParagraphStyle('chapter',fontName='Thesis-Bold',fontSize=18,leading=23,spaceAfter=20,keepWithNext=True),
    'section': ParagraphStyle('section',fontName='Thesis-Bold',fontSize=13,leading=17,spaceBefore=12,spaceAfter=10,keepWithNext=True),
    'ref': ParagraphStyle('ref',fontName='Thesis',fontSize=10.5,leading=13.5,spaceAfter=6,alignment=TA_LEFT,allowWidows=0,allowOrphans=0),
    'equation': ParagraphStyle('equation',fontName='Thesis',fontSize=12,leading=17,alignment=TA_CENTER,spaceAfter=0),
}
class ThesisPDF(BaseDocTemplate):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        f=Frame(self.leftMargin,self.bottomMargin,self.width,self.height,id='main',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='normal',frames=f,onPage=self.page_marks))
        self.heading_id=0
    def page_marks(self,c,doc):
        c.saveState()
        c.setFillColor(colors.HexColor('#666666'))
        c.setFont('Thesis',9)
        c.drawString(self.leftMargin,letter[1]-36,'Detección de agave para apoyar el deshierbe autónomo')
        c.drawRightString(letter[0]-self.rightMargin,letter[1]-36,'Borrador · 27 octubre 2026')
        c.setStrokeColor(colors.HexColor('#CCCCCC'))
        c.line(self.leftMargin,letter[1]-44,letter[0]-self.rightMargin,letter[1]-44)
        c.setFont('Thesis',10)
        c.drawCentredString(letter[0]/2,34,str(doc.page))
        c.restoreState()
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and f.style.name in ['chapter','section']:
            self.heading_id+=1
            key='heading'+str(self.heading_id)
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f.getPlainText(),key,0 if f.style.name=='chapter' else 1,False)

def rich(text):
    text=escape(text)
    text=re.sub(r'\[([^\]]+)\]\((https://[^)]+)\)',lambda m:'<link href="'+m.group(2)+'" color="#254B6F">'+m.group(1)+'</link>',text)
    for sub,number in [('₁','1'),('₂','2')]:
        text=text.replace(sub,'<sub>'+number+'</sub>')
    text=text.replace('ᶜ','<sub>c</sub>')
    return text

doc=ThesisPDF(str(out),pagesize=letter,leftMargin=72,rightMargin=65,topMargin=64,bottomMargin=59,
              title='Capítulo 2. Marco teórico: detección de agave',author='Raúl Eduardo Venegas Reyes',
              subject='Borrador para revisión, corte documental 27 de octubre de 2026')
story=[]
reference_mode=False
for raw in source.read_text(encoding='utf-8').split('\n\n'):
    p=raw.strip()
    if not p: continue
    if p.startswith('# '):
        if story: story.append(PageBreak())
        reference_mode='Referencias' in p
        story.append(Paragraph(rich(p[2:]),styles['chapter']))
    elif p.startswith('## '):
        story.append(Paragraph(rich(p[3:]),styles['section']))
    elif reference_mode:
        story.append(Paragraph(rich(p),styles['ref']))
    elif re.search(r'\(2\.\d\)$',p):
        eq,num=re.split(r'\s+(?=\(2\.\d\)$)',p.strip(),maxsplit=1)
        eq=re.sub(r' {3,}','       ',eq)
        t=Table([[Paragraph(rich(eq),styles['equation']),Paragraph(rich(num),styles['equation'])]],colWidths=[doc.width-44,44])
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),12)]))
        story.append(t)
    else:
        story.append(Paragraph(rich(p),styles['body']))
doc.build(story)
reader=PdfReader(out)
print(f'PDF: {out}')
print(f'Pages: {len(reader.pages)}')
print(f'Words in source: {len(source.read_text(encoding="utf-8").split())}')
for i,p in enumerate(reader.pages,1):
    text=p.extract_text()
    print(f'Page {i}: {len(text)} chars; final: {text[-125:].replace(chr(10)," ")}')
