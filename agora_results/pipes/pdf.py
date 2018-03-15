# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2016  Agora Voting SL <nvotes@nvotes.com>

# agora-results is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# agora-results  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with agora-results.  If not, see <http://www.gnu.org/licenses/>. 

import os
import subprocess
import json
import requests
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def configure_pdf(data_list, title = None, first_description_paragraph = None, last_description_paragraph = None):
    data = data_list[0]
    data['pdf'] = {}
    if title:
        data['pdf']['title'] = title
    if first_description_paragraph:
        data['pdf']['first_description_paragraph'] = first_description_paragraph
    if last_description_paragraph:
        data['pdf']['last_description_paragraph'] = last_description_paragraph

def gen_text(text, size=None, bold=False, align=None, color='black', fontName=None):
    if not isinstance(text, str):
        text = text.__str__()
    p = ParagraphStyle('test')
    if fontName:
        p.fontName = fontName
    if size:
        p.fontSize = size
        p.leading = size * 1.2
    if bold:
        text = '<b>%s</b>' % text
    p.textColor = color
    if align:
        p.alignment = align
    return Paragraph(text, p)

def get_election_cfg(election_id):
    headers = {'content-type': 'application/json'}
    base_url = 'http://localhost:9000/api'

    url = '%s/election/%d' % (base_url, election_id)
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(r.status_code, r.text)
        raise Exception('Invalid status code: %d for election_id = %s' % (r.status_code, election_id))

    return r.json()

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 7)
        self.drawRightString(200*mm, 20*mm,
            "Page %d of %d" % (self._pageNumber, page_count))


def _header_footer(canvas, doc):
    # Save the state of our canvas so we can draw on it
    canvas.saveState()
    styles = getSampleStyleSheet()

    # Header
    #header = Paragraph('This is a multi-line header.  It goes on every page.   ' * 5, styles['Normal'])
    header = Image('/home/agoraelections/agora-results/img/nvotes_logo.jpg', height = 20, width = 80)
    header.hAlign = 'RIGHT'
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.width - w + doc.rightMargin, doc.height + h + doc.bottomMargin - doc.topMargin)

    # Footer
    #footer = Paragraph('This is a multi-line footer.  It goes on every page.' * 5, styles['Normal'])
    #w, h = footer.wrap(doc.width, doc.bottomMargin)
    #footer.drawOn(canvas, doc.leftMargin, h)

    # Release the canvas
    canvas.restoreState()

def pdf_print(election_results, config_folder, election_id):
    jsonconfig = get_election_cfg(election_id)

    pdf_path = os.path.join(config_folder, "%s.results.pdf" % election_id)
    styleSheet = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, rightMargin=50,leftMargin=50, topMargin=35,bottomMargin=80)
    elements = []
    tx_title = 'Resultados del escrutinio de la votación %d - %s'
    tx_description = 'A continuación se detallan, pregunta por pregunta, los resultados de la votación %d titulada <u>"%s"</u> realizada con <font color="blue"><u><a href ="https://www.nvotes.com">nVotes</a></u></font>, que una vez publicados podrán ser verificados en su página pública de votación.'
    tx_question_title = 'Pregunta %d: %s'
    the_title = tx_title % (election_id, jsonconfig['payload']['configuration']['title'])
    if 'pdf' in election_results and 'title' in election_results['pdf']:
        the_title = election_results['pdf']['title']
    elements.append(Spacer(0, 15))
    elements.append(gen_text(the_title, size=20, bold=True, align = TA_LEFT))
    elements.append(Spacer(0, 15))
    if 'pdf' in election_results and 'first_description_paragraph' in election_results['pdf']:
        elements.append(gen_text(election_results['pdf']['first_description_paragraph'], size=12, align = TA_LEFT))
        elements.append(Spacer(0, 15))
    elements.append(gen_text(tx_description % (election_id, jsonconfig['payload']['configuration']['title']), size=12, align = TA_LEFT))
    elements.append(Spacer(0, 15))
    if 'pdf' in election_results and 'last_description_paragraph' in election_results['pdf']:
        elements.append(gen_text(election_results['pdf']['last_description_paragraph'], size=12, align = TA_LEFT))
        elements.append(Spacer(0, 15))
    doc.title = tx_title % (election_id, jsonconfig['payload']['configuration']['title'])

    '''
    percent_base:
      "total" total of the votes, the default
      "valid options" votes to options
    '''
    def get_percentage(num, base):
      if base == 0:
          return 0
      else:
        return num*100.0/base

    counts = election_results['results']['questions']
    for question, i in zip(counts, range(len(counts))):
        blank_votes = question['totals']['blank_votes']
        null_votes = question['totals']['null_votes']
        valid_votes = question['totals']['valid_votes']

        total_votes = blank_votes + null_votes + valid_votes

        percent_base = question['answer_total_votes_percentage']
        if percent_base == "over-total-votes":
          base_num = total_votes
        elif percent_base == "over-total-valid-votes":
          base_num = question['totals']['valid_votes']
        elif "over-total-valid-points" == percent_base \
          and "valid_points" in question['totals']:
          base_num = question['totals']['valid_points']

        elements.append(gen_text(tx_question_title % (i+1, question['title']), size = 15, bold = True, align = TA_LEFT))
        elements.append(Spacer(0, 15))
        t = Table([[gen_text('Datos de configuración', align=TA_CENTER)]])
        table_style = TableStyle([('BACKGROUND',(0,0),(-1,-1),'#b6d7a8'),
                                  ('BOX', (0,0), (-1,-1), 0.5, colors.grey)])
        t.setStyle(table_style)
        elements.append(t)
        tally_type = {
          "plurality-at-large": "Voto en bloque o Escrutinio Mayoritario Plurinominal", 
          "borda-nauru": "Borda de Nauru o Borda Dowdall (1/n)", 
          "borda": "Borda Count (tradicional)", 
          "pairwise-beta": "Comparación de pares (distribución beta)",
          "desborda3": "Desborda3",
          "desborda2": "Desborda2",
          "desborda": "Desborda"
        }
        data = [
          [
            gen_text('Sistema de recuento', align = TA_RIGHT),
            gen_text(tally_type[question['tally_type']], align = TA_LEFT)
          ],
          [
            gen_text('Número mínimo de opciones que puede seleccionar un votante', align = TA_RIGHT),
            gen_text(str(question['min']), align = TA_LEFT)
          ],
          [
            gen_text('Número máximo de opciones que puede seleccionar un votante', align = TA_RIGHT),
            gen_text(str(question['max']), align = TA_LEFT)
          ],
          [
            gen_text('Número de opciones ganadoras', align = TA_RIGHT),
            gen_text(str(question['num_winners']), align = TA_LEFT)
          ],
          [
            gen_text('Las opciones aparecen en la cabina de votación en orden aleatorio', align = TA_RIGHT), 
            gen_text('Sí' if 'shuffle_all_options' in question['extra_options'] and question['extra_options']['shuffle_all_options'] else 'No', align = TA_LEFT)
          ]#,
          #[
            #gen_text('Configuración adicional del recuento', align = TA_RIGHT),
            #gen_text('', align = TA_LEFT)
          #]
        ]
        table_style = TableStyle([('BACKGROUND',(0,0),(0,-1),'#efefef'),
                                  ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
                                  ('BOX', (0,0), (-1,-1), 0.5, colors.grey)])
        t = Table(data)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(0, 15))

        t = Table([[gen_text('Participación en pregunta %d' % (i + 1), align=TA_CENTER)]])
        table_style = TableStyle([('BACKGROUND',(0,0),(-1,-1),'#b6d7a8'),
                                  ('BOX', (0,0), (-1,-1), 0.5, colors.grey)])
        t.setStyle(table_style)
        elements.append(t)
        data = [
          #[
            #gen_text('Número total de electores', align = TA_RIGHT),
            #''
          #],
          [
            gen_text('Número total de votos emitidos', align = TA_RIGHT),
            gen_text(str(total_votes), align = TA_LEFT)
          ],
          [
            gen_text('Votos en blanco', align = TA_RIGHT),
            gen_text("%d (%0.2f%% sobre el número total de votos)" % (blank_votes, get_percentage(blank_votes, total_votes)), align = TA_LEFT)
          ],
          [
            gen_text('Votos nulos', align = TA_RIGHT),
            gen_text("%d (%0.2f%% sobre el número total de votos)" % (null_votes, get_percentage(null_votes, total_votes)), align = TA_LEFT)
          ],
          [
            gen_text('Número total de votos válidos (a opciones)', align = TA_RIGHT),
            gen_text("%d (%0.2f%% sobre el número total de votos)" % (valid_votes, get_percentage(valid_votes, total_votes)), align = TA_LEFT)
          ],
          [
            gen_text('Fecha de inicio del período de voto', align = TA_RIGHT),
            gen_text(str(datetime.strptime(jsonconfig['payload']['startDate'], '%Y-%m-%dT%H:%M:%S.%f')), align = TA_LEFT)
          ],
          [
            gen_text('Fecha de fin del período de voto', align = TA_RIGHT),
            gen_text(str(datetime.strptime(jsonconfig['payload']['endDate'], '%Y-%m-%dT%H:%M:%S.%f')), align = TA_LEFT)
          ],
          [
            gen_text('Fecha de finalización del escrutinio', align = TA_RIGHT),
            gen_text(str(datetime.strptime(jsonconfig['date'], '%Y-%m-%d %H:%M:%S.%f')), align = TA_LEFT)
          ]
        ]
        table_style = TableStyle([('BACKGROUND',(0,0),(0,-1),'#efefef'),
                                  ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
                                  ('BOX', (0,0), (-1,-1), 0.5, colors.grey)])
        t=Table(data)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(0, 15))

        t = Table([[gen_text('Resultados de las candidaturas', align=TA_CENTER)]])
        table_style = TableStyle([('BACKGROUND',(0,0),(-1,-1),'#b6d7a8'),
                                  ('BOX', (0,0), (-1,-1), 0.5, colors.grey)])
        t.setStyle(table_style)
        elements.append(t)

        winners = sorted([answer for answer in question['answers']
            if answer['winner_position'] is not None],
            key=lambda a: a['winner_position'])
        losers_by_name = sorted([answer for answer in question['answers']
            if answer['winner_position'] is None],
            key=lambda a: a['text'])
        losers = sorted(losers_by_name,
            key=lambda a: float(a['total_count']),
            reverse=True)
        data = [
          [
            gen_text('Nombre', align = TA_RIGHT),
            gen_text('Número de puntos', align = TA_CENTER),
            gen_text('¿Posición ganadora?', align = TA_LEFT)
          ]
        ]
        table_style = TableStyle([('BACKGROUND',(0,0),(-1,0),'#cccccc'),
                                  ('BACKGROUND',(0,1),(0,-1),'#efefef'),
                                  ('BACKGROUND',(-1,1),(-1,-1),'#efefef'),
                                  ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
                                  ('BOX', (0,0), (-1,-1), 0.5, colors.grey)])
        for answer in winners:
            data.append(
              [
                gen_text(answer['text'], bold = True, align = TA_RIGHT),
                gen_text('%d (%0.2f%%)' % (answer['total_count'], get_percentage(answer['total_count'], base_num)), bold = True, align = TA_CENTER),
                gen_text('%dº' % ( answer['winner_position'] + 1 ), bold = True, align = TA_LEFT)
              ]
            )
        for answer in losers:
            data.append(
              [
                gen_text(answer['text'], align = TA_RIGHT),
                gen_text('%d (%0.2f%%)' % (answer['total_count'], get_percentage(answer['total_count'], base_num)), align = TA_CENTER),
                gen_text('No', align = TA_LEFT)
              ]
            )
        t=Table(data)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(0, 15))
    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer, canvasmaker = NumberedCanvas)
