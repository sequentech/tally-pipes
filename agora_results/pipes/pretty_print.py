# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2014-2016  Agora Voting SL <agora@agoravoting.com>

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
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER

def pretty_print_stv_winners(data_list, output_func=print):
    data = data_list[0]
    counts = data['results']['questions']
    output_func("Total votes: %d\n", data['results']['total_votes'])
    for question, i in zip(counts, range(len(counts))):
        if "stv" not in question['tally_type']:
            continue

        output_func("Q: %s\n" % question['title'])
        winners = [answer for answer in question['answers']
            if answer['winner_position'] != None]
        question['answers'].sort(key=itemgetter('winner_position'))

        i = 0
        for answer in question['answers']:
            if answer['winner_position'] != None:
                output_func("%d. %s" % (i+1, winner))
                i += 1

def __pretty_print_base(data, mark_winners, show_percent, filter_names, output_func=print):
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

    counts = data['results']['questions']
    for question, i in zip(counts, range(len(counts))):
        if question['tally_type'] not in filter_names or question.get('no-tally', False):
            continue
        output_func("\n\nQ: %s\n" % question['title'])

        blank_votes = question['totals']['blank_votes']
        null_votes = question['totals']['null_votes']
        valid_votes = question['totals']['valid_votes']

        total_votes = blank_votes + null_votes + valid_votes

        percent_base = question['answer_total_votes_percentage']
        if percent_base == "over-total-votes":
          base_num = total_votes
        elif percent_base == "over-total-valid-votes":
          base_num = question['totals']['valid_votes']


        output_func("Total votes: %d" % total_votes)
        output_func("Blank votes: %d (%0.2f%%)" % (
            blank_votes,
            get_percentage(blank_votes, total_votes)))

        output_func("Null votes: %d (%0.2f%%)" % (
            null_votes,
            get_percentage(null_votes, total_votes)))

        output_func("Total valid votes (votes to options): %d (%0.2f%%)" % (
            valid_votes,
            get_percentage(valid_votes, total_votes)))
        output_func("\nOptions (percentages over %s, %d winners):" % (percent_base, question['num_winners']))

        if mark_winners:
            i = 1
            winners = [answer for answer in question['answers']
                if answer['winner_position'] != None]
            for answer in winners:
                if not show_percent:
                    output_func("%d. %s (%0.2f votes)" % (
                        i,
                        answer['text'],
                        answer['total_count']))
                else:
                    output_func("%d. %s (%0.2f votes, %0.2f%%)" % (
                        i,
                        answer['text'],
                        answer['total_count'],
                        get_percentage(answer['total_count'], base_num)))
                i += 1

            losers = sorted([answer for answer in question['answers']
                if answer['winner_position'] == None],
                key=lambda a: float(a['total_count']), reverse=True)

            for loser in losers:
                if not show_percent:
                    output_func("N. %s (%0.2f votes)" % (
                        loser['text'],
                        loser['total_count']))
                else:
                    output_func("N. %s (%0.2f votes, %0.2f%%)" % (
                        loser['text'],
                        loser['total_count'],
                        get_percentage(loser['total_count'], base_num)))
        else:
            answers = sorted([a for a in question['answers']],
                key=lambda a: float(a['total_count']), reverse=True)

            for i, answer in zip(range(len(answers)), answers):
                if not show_percent:
                    output_func("%d. %s (%0.2f votes)" % (
                        i + 1, answer['text'],
                        answer['total_count']))
                else:
                    output_func("%d. %s (%0.2f votes, %0.2f%%)" % (
                        i + 1, answer['text'],
                        answer['total_count'],
                        get_percentage(answer['total_count'], base_num)))
    output_func("")

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

def pdf_print(election_results, config_folder, election_id):
    def read_jsonfile(filepath):
        with open(filepath, mode='r', encoding="utf-8", errors='strict') as f:
            return json.loads(f.read())

    config_path = os.path.join(config_folder, "%s.config.json" % election_id)
    jsonconfig = read_jsonfile(config_path)

    pdf_path = os.path.join(config_folder, "%s.results.pdf" % election_id)
    styleSheet = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
    elements = []
    tx_title = 'Resultados del escrutinio de la votación %d'
    tx_description = 'A continunación se detallan, pregunta por pregunta, los resultados de la votación %d titulada <u>"%s"</u> realizada con <font color="blue"><u><a href ="https://www.nvotes.com">nVotes</a></u></font>, que una vez publicados podrán ser verificados en su <font color="blue"><u><a href ="%s">página pública de votación</a></u></font>.'
    tx_question_title = 'Pregunta %d: %s'
    elements.append(gen_text("nVotes", size=16, bold=True, color = "#374859", align = TA_RIGHT))
    elements.append(Spacer(0, 15))
    elements.append(gen_text(tx_title % election_id, size=15, bold=True, align = TA_LEFT))
    elements.append(Spacer(0, 15))
    elements.append(gen_text(tx_description % (election_id, jsonconfig['payload']['configuration']['title'], 'https://url/publica'), size=12, align = TA_LEFT))
    elements.append(Spacer(0, 15))

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

    counts = data['results']['questions']
    for question, i in zip(counts, range(len(counts))):
    #for question in jsonconfig['payload']['configuration']['questions']:

        blank_votes = question['totals']['blank_votes']
        null_votes = question['totals']['null_votes']
        valid_votes = question['totals']['valid_votes']

        total_votes = blank_votes + null_votes + valid_votes

        percent_base = question['answer_total_votes_percentage']
        if percent_base == "over-total-votes":
          base_num = total_votes
        elif percent_base == "over-total-valid-votes":
          base_num = question['totals']['valid_votes']

        elements.append(gen_text(tx_question_title % (i+1, question['title']), size = 15, bold = True, align = TA_LEFT))
        t = Table([[gen_text('Datos de configuración', align=TA_CENTER)]])
        table_style = TableStyle([('BACKGROUND',(0,0),(-1,-1),'#b6d7a8'),
                                  ('BOX', (0,0), (-1,-1), 0.5, colors.grey)])
        t.setStyle(table_style)
        elements.append(t)
        tally_type = {
          "plurality-at-large": "Voto en bloque o Escrutinio Mayoritario Plurinominal", 
          "borda-nauru": "Borda de Nauru o Borda Dowdall (1/n)", 
          "borda": "Borda Count (tradicional)", 
          "pairwise-beta": "Comparación de pares (distribución beta)"
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
            gen_text('Número mínimo de opciones que puede seleccionar un votante', align = TA_RIGHT),
            gen_text(str(question['max']), align = TA_LEFT)
          ],
          [
            gen_text('Número de opciones ganadoras', align = TA_RIGHT),
            gen_text(str(question['num_winners']), align = TA_LEFT)
          ],
          [
            gen_text('Las opciones aparecen en la cabina de votación en orden aleatorio', align = TA_RIGHT), 
            gen_text('Sí' if 'shuffle_all_options' in question['extra_options'] and question['extra_options']['shuffle_all_options'] else 'No', align = TA_LEFT)
          ],
          [
            gen_text('Configuración adicional del recuento', align = TA_RIGHT),
            gen_text('', align = TA_LEFT)
          ]
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
            'Fecha de inicio del período de recuento',
            str(datetime.strptime(jsonconfig['payload']['configuration']['start_date'], '%Y-%m-%dT%H:%M:%S.%f')
          ],
          [
            'Fecha de fin del período de recuento',
            str(datetime.strptime(jsonconfig['payload']['configuration']['end_date'], '%Y-%m-%dT%H:%M:%S.%f')
          ],
          [
            'Fecha de finalización del escrutinio',
            str(datetime.strptime(jsonconfig['date'], '%Y-%d-%m %H:%M:%S.%f')
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

        winners = [answer for answer in question['answers']
            if answer['winner_position'] != None]
        losers = sorted([answer for answer in question['answers']
            if answer['winner_position'] == None],
            key=lambda a: float(a['total_count']), reverse=True)
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
                gen_text(str(answer['winner_position']), bold = True, align = TA_LEFT)
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
    doc.build(elements)

def pretty_print_not_iterative(data_list, mark_winners=True, output_func=print):
    data = data_list[0]
    __pretty_print_base(data, mark_winners, show_percent=True,
        filter_names=["plurality-at-large", "borda-nauru", "borda", "pairwise-beta", "cup"],
        output_func=output_func)
