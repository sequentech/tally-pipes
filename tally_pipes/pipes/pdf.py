# -*- coding:utf-8 -*-

# This file is part of tally-pipes.
# Copyright (C) 2016-2021  Sequent Tech Inc <legal@sequentech.io>

# tally-pipes is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# tally-pipes  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with tally-pipes.  If not, see <http://www.gnu.org/licenses/>. 

import os
import re
import gettext
import os
from datetime import datetime

def configure_pdf(
    data_list, 
    title=None, 
    first_description_paragraph=None,
    last_description_paragraph=None,
    languages=None,
    timezone=None,
    date_format=None,
    hide_logo=None,
    hide_dates=None,
    theme_colors=None
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
    if timezone:
        assert(isinstance(timezone, str))
        data['pdf']['timezone'] = timezone
    if date_format:
        assert(isinstance(date_format, str))
        data['pdf']['date_format'] = date_format
    if hide_logo:
        assert(isinstance(hide_logo, bool))
        data['pdf']['hide_logo'] = hide_logo
    if hide_dates:
        assert(isinstance(hide_dates, bool))
        data['pdf']['hide_dates'] = hide_dates
    if theme_colors:
        assert(isinstance(theme_colors, dict))
        for value in theme_colors.values():
            assert(isinstance(value, str))
        data['pdf']['theme_colors'] = theme_colors

def remove_html(text):
    return re.sub(r"<[^>]+>", " ", text)

def parse_date(date_str, input_date_format, timezone_str, output_date_format):
    import pytz
    date = datetime.strptime(date_str, input_date_format)
    timezone = pytz.timezone(timezone_str)
    date_timezoned = date.astimezone(timezone)
    return date_timezoned.strftime(output_date_format)

def gen_text(
    text,
    size=None, 
    bold=False, 
    align=None, 
    color='black', 
    fontName=None
):
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle

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
    import requests
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

def _header_footer(canvas, doc, hide_logo):
    # If logo should not be shown, then do nothine_logog
    if hide_logo:
        return

    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Image

    # Save the state of our canvas so we can draw on it
    canvas.saveState()
    styles = getSampleStyleSheet()

    # Header
    header = Image(
        '/home/ballotbox/tally-pipes/img/sequent_logo.jpg',
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

def custom_i18n(parent, key, langs):
    translation = ''
    key_i18n = key + '_i18n'
    if key_i18n in parent:
        for lang in langs:
            if lang in parent[key_i18n]:
                translation = parent[key_i18n][lang]
                break
    if not translation and key in parent:
        translation = parent[key]
    return translation

def pdf_print(election_results, config_folder, election_id):
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

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

    localedir = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'locale'
    )
    languages = election_results.get('pdf', dict()).get('languages', [])
    translate = gettext.translation(
        'pipes', 
        localedir, 
        languages=election_results.get('pdf', dict()).get('languages', None), 
        fallback=True
    )
    _ = translate.gettext
    try:
        jsonconfig = get_election_cfg(election_id)
        election_title = remove_html(custom_i18n(jsonconfig['payload']['configuration'],'title', languages))
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
    theme_colors = dict(
        Background='white',
        OnBackground='black',
        Primary='#b6d7a8',
        OnPrimary='black',
        OnGrey='black',
        Grey='grey',
        LightGrey='#cccccc',
        DarkGrey='#efefef'
    )
    hide_logo = False
    hide_dates = False
    if 'pdf' in election_results:
        if 'theme_colors' in election_results['pdf']:
            theme_colors = {
                **theme_colors,
                **election_results['pdf']['theme_colors']
            }
        if 'hide_dates' in election_results['pdf']:
            hide_dates = election_results['pdf']['hide_dates']
        if 'hide_logo' in election_results['pdf']:
            hide_logo = election_results['pdf']['hide_logo']
        if 'title' in election_results['pdf']:
            the_title = election_results['pdf']['title']
    elements.append(Spacer(0, 15))
    elements.append(
        gen_text(
            the_title,
            size=20,
            bold=True,
            align=TA_LEFT,
            color=theme_colors['OnBackground']
        )
    )
    elements.append(Spacer(0, 15))
    if (
        'pdf' in election_results and 
        'first_description_paragraph' in election_results['pdf']
    ):
        elements.append(
            gen_text(
                election_results['pdf']['first_description_paragraph'], 
                size=12, 
                align=TA_LEFT,
                color=theme_colors['OnBackground']
            )
        )
        elements.append(Spacer(0, 15))
    elements.append(
        gen_text(
            tx_description,
            size=12,
            align=TA_LEFT,
            color=theme_colors['OnBackground']
        )
    )
    elements.append(Spacer(0, 15))
    if (
        'pdf' in election_results and 
        'last_description_paragraph' in election_results['pdf']
    ):
        elements.append(
            gen_text(
                election_results['pdf']['last_description_paragraph'],
                size=12, 
                align=TA_LEFT,
                color=theme_colors['OnBackground']
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
                    question_title=remove_html(custom_i18n(question, 'title', languages))
                ),
                size=15,
                bold=True,
                align=TA_LEFT,
                color=theme_colors['OnBackground']
            )
        )
        elements.append(Spacer(0, 15))
        t = Table([[
            gen_text(
                _('Configuration Data'),
                align=TA_CENTER,
                color=theme_colors['OnPrimary']
            )
        ]])
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(-1,-1), theme_colors['Primary']),
                ('BOX', (0,0), (-1,-1), 0.5, theme_colors['Grey'])
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
                    align=TA_RIGHT,
                    color=theme_colors['OnGrey']
                ),
                gen_text(
                    tally_type[question['tally_type']],
                    align=TA_LEFT,
                    color=theme_colors['OnBackground']
                )
            ],
            [
                gen_text(
                    _('Minimum number of options a voter can select'),
                    align=TA_RIGHT,
                    color=theme_colors['OnGrey']
                ),
                gen_text(
                    str(question['min']),
                    align=TA_LEFT,
                    color=theme_colors['OnBackground']
                )
            ],
            [
                gen_text(
                    _('Maximum number of options a voter can select'),
                    align=TA_RIGHT,
                    color=theme_colors['OnGrey']
                ),
                gen_text(
                    str(question['max']),
                    align=TA_LEFT,
                    color=theme_colors['OnBackground']
                )
            ],
            [
                gen_text(
                    _('Number of winning options'), 
                    align=TA_RIGHT,
                    color=theme_colors['OnGrey']
                ),
                gen_text(
                    str(question['num_winners']),
                    align=TA_LEFT,
                    color=theme_colors['OnBackground']
                )
            ],
            [
                gen_text(
                    _('Options appear in the voting booth in random order'),
                    align=TA_RIGHT,
                    color=theme_colors['OnGrey']
                ), 
                gen_text(
                    _('Yes') 
                    if (
                        'shuffle_all_options' in question['extra_options'] and 
                        question['extra_options']['shuffle_all_options']
                    )
                    else _('No'), 
                    align=TA_LEFT,
                    color=theme_colors['OnBackground']
                )
            ]
        ]
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(0,-1), theme_colors['DarkGrey']),
                ('INNERGRID', (0,0), (-1,-1), 0.5, theme_colors['Grey']),
                ('BOX', (0,0), (-1,-1), 0.5, theme_colors['Grey'])
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
                        align=TA_CENTER,
                        color=theme_colors['OnPrimary']
                    )
                ]
            ]
        )
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(-1,-1), theme_colors['Primary']),
                ('BOX', (0,0), (-1,-1), 0.5, theme_colors['Grey'])
            ]
        )
        t.setStyle(table_style)
        elements.append(t)
        data = [
            [
                gen_text(
                    _('Total number of votes cast'),
                    align=TA_RIGHT,
                    color=theme_colors['OnGrey']
                ),
                gen_text(
                    str(total_votes),
                    align=TA_LEFT,
                    color=theme_colors['OnBackground']
                )
            ],
            [
                gen_text(
                    _('Blank votes'),
                    align=TA_RIGHT,
                    color=theme_colors['OnGrey']
                ),
                gen_text(
                    _(
                        "{blank_votes} ({percentage:.2%} over the total " + 
                        "number of votes)"
                    ).format(
                        blank_votes=blank_votes,
                        percentage=get_percentage(blank_votes, total_votes)
                    ),
                    align=TA_LEFT,
                    color=theme_colors['OnBackground']
                )
            ],
            [
                gen_text(
                    _('Null votes'),
                    align=TA_RIGHT,
                    color=theme_colors['OnGrey']
                ),
                gen_text(
                    _(
                        "{null_votes} ({percentage:.2%} over the total " +
                        "number of votes)"
                    ).format(
                        null_votes=null_votes,
                        percentage=get_percentage(null_votes, total_votes)
                    ),
                    align=TA_LEFT,
                    color=theme_colors['OnBackground']
                )
            ],
            [
                gen_text(
                    _('Total number of votes for options'),
                    align=TA_RIGHT,
                    color=theme_colors['OnGrey']
                ),
                gen_text(
                    _(
                        "{valid_votes} ({percentage:.2%} over the total " +
                        "number of votes)"
                    ).format(
                        valid_votes=valid_votes,
                        percentage=get_percentage(valid_votes, total_votes)
                    ),
                    align=TA_LEFT,
                    color=theme_colors['OnBackground']
                )
            ]
        ]
        if not hide_dates:
            data += [
                [
                    gen_text(
                        _('Voting period start date'),
                        align=TA_RIGHT,
                        color=theme_colors['OnGrey']
                    ),
                    gen_text(
                        parse_date(
                            date_str=jsonconfig['payload']['startDate'],
                            input_date_format='%Y-%m-%dT%H:%M:%S.%f',
                            timezone_str=election_results\
                                .get('pdf', dict())\
                                .get('timezone', 'UTC'),
                            output_date_format=election_results\
                                .get('pdf', dict())\
                                .get('date_format', '%Y-%m-%d %H:%M:%S %Z')
                        ),
                        align=TA_LEFT,
                        color=theme_colors['OnBackground']
                    )
                ],
                [
                    gen_text(
                        _('Voting period end date'),
                        align=TA_RIGHT,
                        color=theme_colors['OnGrey']
                    ),
                    gen_text(
                        parse_date(
                            date_str=jsonconfig['payload']['endDate'],
                            input_date_format='%Y-%m-%dT%H:%M:%S.%f',
                            timezone_str=election_results\
                                .get('pdf', dict())\
                                .get('timezone', 'UTC'),
                            output_date_format=election_results\
                                .get('pdf', dict())\
                                .get('date_format', '%Y-%m-%d %H:%M:%S %Z')
                        ),
                        align=TA_LEFT,
                        color=theme_colors['OnBackground']
                    )
                ],
                [
                    gen_text(
                        _('Tally end date'),
                        align=TA_RIGHT,
                        color=theme_colors['OnGrey']
                    ),
                    gen_text(
                        parse_date(
                            date_str=jsonconfig['date'],
                            input_date_format='%Y-%m-%d %H:%M:%S.%f',
                            timezone_str=election_results\
                                .get('pdf', dict())\
                                .get('timezone', 'UTC'),
                            output_date_format=election_results\
                                .get('pdf', dict())\
                                .get('date_format', '%Y-%m-%d %H:%M:%S %Z')
                        ),
                        align=TA_LEFT,
                        color=theme_colors['OnBackground']
                    )
                ]
            ]
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(0,-1), theme_colors['DarkGrey']),
                ('INNERGRID', (0,0), (-1,-1), 0.5, theme_colors['Grey']),
                ('BOX', (0,0), (-1,-1), 0.5, theme_colors['Grey'])
            ]
        )
        t=Table(data)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(0, 15))

        t = Table([[
            gen_text(
                _('Candidate results'), 
                align=TA_CENTER,
                color=theme_colors['OnPrimary']
            )
        ]])
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(-1,-1), theme_colors['Primary']),
                ('BOX', (0,0), (-1,-1), 0.5, theme_colors['Grey'])
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
                  align=TA_RIGHT,
                  color=theme_colors['OnGrey']
              ),
              gen_text(
                  _('Points'),
                  align=TA_CENTER,
                  color=theme_colors['OnGrey']
              ),
              gen_text(
                  _('Winning position'),
                  align=TA_LEFT,
                  color=theme_colors['OnGrey']
              )
            ]
        ]
        table_style = TableStyle(
            [
                ('BACKGROUND',(0,0),(-1,0), theme_colors['LightGrey']),
                ('BACKGROUND',(0,1),(0,-1),  theme_colors['DarkGrey']),
                ('BACKGROUND',(-1,1),(-1,-1),  theme_colors['DarkGrey']),
                ('INNERGRID', (0,0), (-1,-1), 0.5, theme_colors['Grey']),
                ('BOX', (0,0), (-1,-1), 0.5, theme_colors['Grey'])
            ]
        )
        for answer in winners:
            answer_text = remove_html(custom_i18n(answer, 'text', languages))
            if dict(title='isWriteInResult', url='true') in answer.get('urls', []):
                answer_text = _('{candidate_text} (Write-in)').format(
                    candidate_text=answer_text
                )
            data.append(
                [
                    gen_text(
                        answer_text,
                        bold=True,
                        align=TA_RIGHT,
                        color=theme_colors['OnGrey']
                    ),
                    gen_text(
                        '%d' % answer['total_count'],
                        bold=True,
                        align=TA_CENTER,
                        color=theme_colors['OnGrey']
                    ),
                    gen_text(
                        '%dº' % (answer['winner_position'] + 1),
                        bold=True,
                        align=TA_LEFT,
                        color=theme_colors['OnGrey']
                    )
                ]
            )
        for loser in losers:
            loser_text = remove_html(custom_i18n(loser, 'text', languages))
            if dict(title='isWriteInResult', url='true') in loser.get('urls', []):
                loser_text = _('{candidate_text} (Write-in)').format(
                    candidate_text=loser_text
                )
            data.append(
                [
                    gen_text(
                        loser_text,
                        align=TA_RIGHT,
                        color=theme_colors['OnBackground']
                    ),
                    gen_text(
                        '%d' % loser['total_count'],
                        align=TA_CENTER,
                        color=theme_colors['OnBackground']
                    ),
                    gen_text(
                        '-',
                        align=TA_LEFT,
                        color=theme_colors['OnBackground']
                    )
                ]
            )
        t = Table(data)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(0, 15))

    def _header_footer_wrapper(canvas, doc):
        '''
        Wrapper around _header_footer, to be able to capture hide_logo variable
        from the current context.
        '''
        return _header_footer(canvas, doc, hide_logo=hide_logo)

    doc.build(
        elements, 
        onFirstPage=_header_footer_wrapper,
        onLaterPages=_header_footer_wrapper,
        canvasmaker=NumberedCanvas
    )
