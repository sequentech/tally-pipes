# -*- coding:utf-8 -*-

# This file is part of tally-pipes.
# Copyright (C) 2014-2016  Sequent Tech Inc <legal@sequentech.io>

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
import subprocess
import json
import requests
from datetime import datetime
import gettext

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

def __pretty_print_base(
    data,
    mark_winners,
    show_percent,
    filter_names,
    output_func=print
):
    localedir = os.path.join(
      os.path.abspath(os.path.dirname(__file__)), 
      'locale'
    )
    translate = gettext.translation(
      'pipes', 
      localedir, 
      languages=data.get('pdf', dict()).get('languages', None), 
      fallback=True
    )
    _ = translate.gettext
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
        tally_map = {
          "plurality-at-large": "plurality-at-large",
          "cumulative": "plurality-at-large",
          "borda-nauru": "borda",
          "borda": "borda",
          "pairwise-beta": "borda",
          "desborda3": "borda",
          "desborda2": "borda",
          "desborda": "borda"
        }
        count_type_map = {
          "borda": "points",
          "plurality-at-large": "votes"
        }
        count_type = count_type_map[tally_map[question['tally_type']]]
        
        blank_votes = question['totals']['blank_votes']
        null_votes = question['totals']['null_votes']
        valid_votes = question['totals']['valid_votes']

        total_votes = blank_votes + null_votes + valid_votes

        percent_base = question['answer_total_votes_percentage']
        if percent_base == "over-total-votes":
          base_num = total_votes
        elif percent_base == "over-total-valid-votes":
          base_num = question['totals']['valid_votes']
        elif "over-total-valid-points" == percent_base:
          base_num = question['totals']['valid_points']


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
            winners = sorted([answer for answer in question['answers']
                if answer['winner_position'] != None],
                key=lambda a: a['winner_position'])
            for answer in winners:
                answer_text = answer['text']
                if dict(title='isWriteInResult', url='true') in answer.get('urls', []):
                    answer_text = _('{candidate_text} (Write-in)').format(
                        candidate_text=answer['text']
                    )
                if not show_percent:
                    output_func("%d. %s (%0.2f %s)" % (
                        i,
                        answer_text,
                        answer['total_count'],
                        count_type))
                else:
                    output_func("%d. %s (%0.2f %s, %0.2f%%)" % (
                        i,
                        answer_text,
                        answer['total_count'],
                        count_type,
                        get_percentage(answer['total_count'], base_num)))
                i += 1

            losers_by_name = sorted([answer for answer in question['answers']
                if answer['winner_position'] == None],
                key=lambda a: a['text'])
            losers = sorted(losers_by_name,
                key=lambda a: float(a['total_count']), reverse=True)

            for loser in losers:
                loser_text = loser['text']
                if dict(title='isWriteInResult', url='true') in loser.get('urls', []):
                    loser_text = _('{candidate_text} (Write-in)').format(
                        candidate_text=loser['text']
                    )
                if not show_percent:
                    output_func("N. %s (%0.2f %s)" % (
                        loser_text,
                        loser['total_count'],
                        count_type))
                else:
                    output_func("N. %s (%0.2f %s, %0.2f%%)" % (
                        loser_text,
                        loser['total_count'],
                        count_type,
                        get_percentage(loser['total_count'], base_num)))
        else:
            answers_by_name = sorted([a for a in question['answers']],
                key=lambda a: a['text'])
            answers = sorted(answers_by_name,
                key=lambda a: float(a['total_count']), reverse=True)

            for i, answer in zip(range(len(answers)), answers):
                answer_text = answer['text']
                if dict(title='isWriteInResult', url='true') in answer.get('urls', []):
                    answer_text = _('{candidate_text} (Write-in)').format(
                        candidate_text=answer['text']
                    )
                if not show_percent:
                    output_func("%d. %s (%0.2f %s)" % (
                        i + 1,
                        answer_text,
                        answer['total_count'],
                        count_type))
                else:
                    output_func("%d. %s (%0.2f %s, %0.2f%%)" % (
                        i + 1, 
                        answer_text,
                        answer['total_count'],
                        count_type,
                        get_percentage(answer['total_count'], base_num)))
    output_func("")


def pretty_print_not_iterative(data_list, mark_winners=True, output_func=print):
    data = data_list[0]
    __pretty_print_base(
        data, 
        mark_winners, 
        show_percent=True,
        filter_names=[
            "cumulative", 
            "plurality-at-large", 
            "borda-nauru", 
            "desborda3", 
            "desborda2", 
            "desborda", 
            "borda",
        ],
        output_func=output_func
    )
