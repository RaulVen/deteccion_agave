from pathlib import Path
from _common import DOCUMENTS, check_destination, export_options, register_fonts

options = export_options('Exporta el capítulo 1 y su marco teórico desde el Markdown conservado.')
import re
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents

source = DOCUMENTS/'Capitulo_1_y_marco_teorico_agave.md'
out = source.with_suffix('.pdf')
check_destination(out, options.overwrite)
register_fonts('TimesCustom')

styles = {
 'body': ParagraphStyle('body', fontName='TimesCustom',fontSize=12,leading=17,alignment=TA_JUSTIFY,spaceAfter=8,allowWidows=0,allowOrphans=0),
 'title': ParagraphStyle('title',fontName='TimesCustom-Bold',fontSize=19,leading=25,alignment=TA_CENTER,spaceAfter=28),
 'cover': ParagraphStyle('cover',fontName='TimesCustom',fontSize=13,leading=19,alignment=TA_CENTER,spaceAfter=14),
 'chapter': ParagraphStyle('chapter',fontName='TimesCustom-Bold',fontSize=17,leading=22,spaceAfter=18,keepWithNext=True),
 'section': ParagraphStyle('section',fontName='TimesCustom-Bold',fontSize=13,leading=17,spaceBefore=12,spaceAfter=9,keepWithNext=True),
 'sub': ParagraphStyle('sub',fontName='TimesCustom-Bold',fontSize=12,leading=16,spaceBefore=9,spaceAfter=7,keepWithNext=True),
 'ref': ParagraphStyle('ref',fontName='TimesCustom',fontSize=10.5,leading=14,spaceAfter=11,alignment=TA_LEFT,allowWidows=0,allowOrphans=0),
}

class ThesisPDF(BaseDocTemplate):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        f=Frame(self.leftMargin,self.bottomMargin,self.width,self.height,id='main',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='normal',frames=f,onPage=self.page_footer))
    def page_footer(self,c,doc):
        if doc.page>1:
            c.setFont('TimesCustom',10)
            c.setFillColor(colors.HexColor('#444444'))
            c.drawCentredString(letter[0]/2,35,str(doc.page-1))
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and (f.style.name in ['chapter','section'] or (f.style.name=='sub' and f.getPlainText().startswith('1.3.'))):
            name=f.getPlainText()
            key='h'+str(self.seq.nextf('headings'))
            self.canv.bookmarkPage(key)
            level={'chapter':0,'section':1,'sub':2}[f.style.name]
            self.canv.addOutlineEntry(name,key,level,False)
            self.notify('TOCEntry',(level,name,self.page-1,key))

def rich(s):
    s=escape(s)
    s=re.sub(r'(https://[^\s]+)',r'<link href="\1" color="#222222">\1</link>',s)
    return s

doc=ThesisPDF(str(out),pagesize=letter,leftMargin=76,rightMargin=65,topMargin=61,bottomMargin=59,title='Detección de agave para apoyar el deshierbe selectivo',author='Raúl Eduardo Venegas Reyes')
paras=source.read_text(encoding='utf-8').split('\n\n')
story=[Spacer(1,75)]
start=next(i for i,p in enumerate(paras) if p.startswith('## Capítulo 1'))
story.append(Paragraph(rich(paras[0][2:]),styles['title']))
for p in paras[1:start]:story.append(Paragraph(rich(p.strip()),styles['cover']))
story += [Spacer(1,34),Paragraph('Capítulo 1 y desarrollo del marco teórico',styles['cover']),PageBreak(),Paragraph('Contenido',styles['chapter'])]
# TOC heading is ordinary text to avoid self-entry.
story[-1].style=ParagraphStyle('toc_title',parent=styles['chapter'])
toc=TableOfContents()
toc.levelStyles=[ParagraphStyle('toc0',fontName='TimesCustom-Bold',fontSize=12,leading=17,spaceBefore=9,leftIndent=0,firstLineIndent=0),ParagraphStyle('toc1',fontName='TimesCustom',fontSize=11,leading=16,leftIndent=12,firstLineIndent=0),ParagraphStyle('toc2',fontName='TimesCustom',fontSize=10.5,leading=15,leftIndent=24,firstLineIndent=0)]
story.extend([toc,PageBreak()])
first=True
for p in paras[start:]:
    p=p.strip()
    if not p:continue
    if p.startswith('## '):
        if not first:story.append(PageBreak())
        first=False
        story.append(Paragraph(rich(p[3:]),styles['chapter']))
    elif p.startswith('### '):story.append(Paragraph(rich(p[4:]),styles['section']))
    elif p.startswith('#### '):story.append(Paragraph(rich(p[5:]),styles['sub']))
    elif re.match(r'^\[\d+\]',p):story.append(Paragraph(rich(p),styles['ref']))
    else:story.append(Paragraph(rich(p),styles['body']))
doc.multiBuild(story)
print(out)
