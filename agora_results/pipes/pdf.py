# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2016-2021  Agora Voting SL <nvotes@nvotes.com>

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
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.platypus import (
  SimpleDocTemplate, 
  Paragraph, 
  Spacer, 
  Table, 
  TableStyle, 
  Image
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import gettext
import os

def configure_pdf(
    data_list, 
    title=None, 
    first_description_paragraph=None,
    last_description_paragraph=None,
    languages=None
):
    data = data_list[0]
    data['pdf'] = {}
    if title:
        assert(isinstance(title, str))
        data['pdf']['title'] = title
    if first_description_paragraph:
        assert(isinstance(first_description_paragraph, str))
        data['pdf']['first_description_paragraph'] = first_description_paragraph
    if last_description_paragraph:
        assert(isinstance(last_description_paragraph, str))
        data['pdf']['last_description_paragraph'] = last_description_paragraph
    if languages:
        assert(isinstance(languages, list))
        for language in languages:
            assert(isinstance(language, str))
        data['pdf']['languages'] = languages

def gen_text(
    text,
    size=None, 
    bold=False, 
    align=None, 
    color='black', 
    fontName=None
):
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

    try:
        r = requests.get(url, headers=headers, timeout=5)
    except requests.exceptions.Timeout:
        raise Exception(
            'Timeout when requesting election_id = %s' % election_id
        )

    if r.status_code != 200:
        print(r.status_code, r.text)
        raise Exception(
            'Invalid status code: %d for election_id = %s' % (
                r.status_code,
                election_id
            )
        )

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
    header = Image(
        '/home/agoraelections/agora-results/img/nvotes_logo.jpg',
        height=20,
        width=80
    )
    header.hAlign = 'RIGHT'
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(
        canvas, 
        doc.width - w + doc.rightMargin, 
        doc.height + h + doc.bottomMargin - doc.topMargin
    )

    # Release the canvas
    canvas.restoreState()

def pdf_print(election_results, config_folder, election_id):

    localedir = os.path.join(
      os.path.abspath(os.path.dirname(__file__)), 
      'locale'
    )
    translate = gettext.translation(
      'pipes', 
      localedir, 
      languages=election_results.get('pdf', dict()).get('languages', None), 
      fallback=True
    )
    _ = translate.gettext
    try:
        jsonconfig = get_election_cfg(election_id)
        election_title = jsonconfig['payload']['configuration']['title']
    except:
        election_title = ""

    tx_description = _(
        'Detailed and question by question results of the election ' +
        '{election_id} titled <u>"{election_title}"</u>.'
    ).format(
        election_id=election_id,
        election_title=election_title
    )
    tx_title = _(
        'Results of the election tally {election_id} - {election_title}'
    ).format(
        election_id=election_id,
        election_title=election_title
    )
    pdf_path = os.path.join(config_folder, "%s.results.pdf" % election_id)
    styleSheet = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        pdf_path, 
        rightMargin=50,
        leftMargin=50,
        topMargin=35,
        bottomMargin=80
    )
    elements = []
    the_title = tx_title
    if 'pdf' in election_results and 'title' in election_results['pdf']:
        the_title = election_results['pdf']['title']
    elements.append(Spacer(0, 15))
    elements.append(gen_text(the_title, size=20, bold=True, align = TA_LEFT))
    elements.append(Spacer(0, 15))
    if (
        'pdf' in election_results and 
        'first_description_paragraph' in election_results['pdf']
    ):
        elements.append(
            gen_text(
                election_results['pdf']['first_description_paragraph'], 
                size=12, 
                align=TA_LEFT
            )
        )
        elements.append(Spacer(0, 15))
    elements.append(gen_text(tx_description, size=12, align = TA_LEFT))
    elements.append(Spacer(0, 15))
    if (
        'pdf' in election_results and 
        'last_description_paragraph' in election_results['pdf']
    ):
        elements.append(
            gen_text(
                election_results['pdf']['last_description_paragraph'],
                size=12, 
                align=TA_LEFT
            )
        )
        elements.append(Spacer(0, 15))
    doc.title = tx_title

    '''
    Returns the percentage points, ensuring it works with base=0
    '''
    def get_percentage(num, base):
      if base == 0:
          return 0
      else:
        return num/base

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
        elif (
            "over-total-valid-points" == percent_base and
            "valid_points" in question['totals']
        ):
          base_num = question['totals']['valid_points']

        elements.append(
            gen_text(
                _('Question {question_index}: {question_title}').format(
                    question_index=i+1,
                    question_title=question['title']
                ),
                size=15,
                bold=True,
                align=TA_LEFT
            )
        )
        elements.append(Spacer(0, 15))
        t = Table([[
            gen_text(
                _('Configuration Data'),
                align=TA_CENTER
            )
        ]])
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(-1,-1),'#b6d7a8'),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey)
            ]
        )
        t.setStyle(table_style)
        elements.append(t)
        tally_type = {
            "plurality-at-large": _(
              "First past the post, Plurality or Plurality at Large"
            ), 
            "cumulative": _("Cumulative voting"),
            "borda-nauru": _("Borda Nauru or Borda Dowdall (1/n)"), 
            "borda": "Borda Count (traditional)", 
            "pairwise-beta": _("Pairwise comparison (beta distribution)"),
            "desborda3": _("Desborda3"),
            "desborda2": _("Desborda2"),
            "desborda":  _("Desborda")
        }
        data = [
          [
              gen_text(
                  _('Tally system'),
                  align=TA_RIGHT
              ),
              gen_text(tally_type[question['tally_type']], align=TA_LEFT)
          ],
          [
              gen_text(
                  _('Minimum number of options a voter can select'),
                  align=TA_RIGHT
              ),
              gen_text(str(question['min']), align=TA_LEFT)
          ],
          [
              gen_text(
                  _('Maximum number of options a voter can select'),
                  align=TA_RIGHT
              ),
              gen_text(str(question['max']), align=TA_LEFT)
          ],
          [
              gen_text(
                  _('Number of winning options'), 
                  align=TA_RIGHT
              ),
              gen_text(str(question['num_winners']), align=TA_LEFT)
          ],
          [
              gen_text(
                  _('Options appear in the voting booth in random order'),
                  align=TA_RIGHT
              ), 
              gen_text(
                  _('Yes') 
                  if (
                      'shuffle_all_options' in question['extra_options'] and 
                      question['extra_options']['shuffle_all_options']
                  )
                  else _('No'), 
                  align=TA_LEFT
              )
          ]
        ]
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(0,-1),'#efefef'),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey)
            ]
        )
        t = Table(data)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(0, 15))

        t = Table(
            [
                [
                    gen_text(
                        _('Participation in question {question_index}').format(
                            question_index=i + 1
                        ),
                        align=TA_CENTER
                    )
                ]
            ]
        )
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(-1,-1),'#b6d7a8'),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey)
            ]
        )
        t.setStyle(table_style)
        elements.append(t)
        data = [
            [
                gen_text(_('Total number of votes cast'), align=TA_RIGHT),
                gen_text(str(total_votes), align=TA_LEFT)
            ],
            [
                gen_text(_('Blank votes'), align=TA_RIGHT),
                gen_text(
                    _(
                        "{blank_votes} ({percentage:.2%} over the total " + 
                        "number of votes)"
                    ).format(
                        blank_votes=blank_votes,
                        percentage=get_percentage(blank_votes, total_votes)
                    ),
                    align=TA_LEFT
                )
            ],
            [
                gen_text(_('Null votes'), align=TA_RIGHT),
                gen_text(
                    _(
                        "{null_votes} ({percentage:.2%} over the total " +
                        "number of votes)"
                    ).format(
                        null_votes=null_votes,
                        percentage=get_percentage(null_votes, total_votes)
                    ),
                    align=TA_LEFT
                )
            ],
            [
                gen_text(
                    _('Total number of votes for options'),
                    align=TA_RIGHT
                ),
                gen_text(
                    _(
                        "{valid_votes} ({percentage:.2%} over the total " +
                        "number of votes)"
                    ).format(
                        valid_votes=valid_votes,
                        percentage=get_percentage(valid_votes, total_votes)
                    ),
                    align=TA_LEFT
                )
            ],
            [
                gen_text(
                    _('Voting period start date'),
                    align=TA_RIGHT
                ),
                gen_text(
                    str(
                        datetime.strptime(
                            jsonconfig['payload']['startDate'],
                            '%Y-%m-%dT%H:%M:%S.%f'
                        )
                    ),
                    align=TA_LEFT
                )
            ],
            [
                gen_text(
                    _('Voting period end date'),
                    align=TA_RIGHT
                ),
                gen_text(
                    str(
                        datetime.strptime(
                            jsonconfig['payload']['endDate'], 
                            '%Y-%m-%dT%H:%M:%S.%f'
                        )
                    ),
                    align=TA_LEFT
                )
            ],
            [
              gen_text(_('Tally end date'), align=TA_RIGHT),
              gen_text(
                  str(
                      datetime.strptime(
                          jsonconfig['date'], 
                          '%Y-%m-%d %H:%M:%S.%f'
                      )
                  ),
                  align=TA_LEFT
              )
            ]
        ]
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(0,-1),'#efefef'),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey)
            ]
        )
        t=Table(data)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(0, 15))

        t = Table([[
            gen_text(
                _('Candidate results'), 
                align=TA_CENTER
            )
        ]])
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(-1,-1),'#b6d7a8'),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey)
            ]
        )
        t.setStyle(table_style)
        elements.append(t)

        winners = sorted(
          [
              answer 
              for answer in question['answers']
              if answer['winner_position'] is not None
          ],
          key=lambda a: a['winner_position']
        )
        losers_by_name = sorted(
            [
                answer for answer in question['answers']
                if answer['winner_position'] is None
            ],
            key=lambda a: a['text']
        )
        losers = sorted(
            losers_by_name,
            key=lambda a: float(a['total_count']),
            reverse=True
        )
        data = [
            [
              gen_text(
                  _('Name'),
                  align=TA_RIGHT
              ),
              gen_text(
                  _('Points'),
                  align=TA_CENTER
              ),
              gen_text(
                  _('Winning position'),
                  align=TA_LEFT
              )
            ]
        ]
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(-1,0),'#cccccc'),
                ('BACKGROUND',(0,1),(0,-1),'#efefef'),
                ('BACKGROUND',(-1,1),(-1,-1),'#efefef'),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey)
            ]
        )
        for answer in winners:
            data.append(
                [
                    gen_text(answer['text'], bold = True, align=TA_RIGHT),
                    gen_text(
                        '%d' % answer['total_count'],
                        bold=True,
                        align=TA_CENTER
                    ),
                    gen_text(
                        '%dº' % (answer['winner_position'] + 1),
                        bold=True,
                        align=TA_LEFT
                    )
                ]
            )
        for answer in losers:
            data.append(
                [
                    gen_text(answer['text'], align=TA_RIGHT),
                    gen_text(
                        '%d' % answer['total_count'],
                        align=TA_CENTER
                    ),
                    gen_text('-', align=TA_LEFT)
                ]
            )
        t = Table(data)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(0, 15))
    doc.build(
        elements, 
        onFirstPage=_header_footer, 
        onLaterPages=_header_footer, 
        canvasmaker=NumberedCanvas
    )
