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

def pretty_print_stv_winners(data_list):
    data = data_list[0]
    counts = data['results']['questions']
    print("Total votes: %d\n", data['results']['total_votes'])
    for question, i in zip(counts, range(len(counts))):
        if "stv" not in question['tally_type']:
            continue

        print("Q: %s\n" % question['title'])
        winners = [answer for answer in question['answers']
            if answer['winner_position'] != None]
        question['answers'].sort(key=itemgetter('winner_position'))

        i = 0
        for answer in question['answers']:
            if answer['winner_position'] != None:
                print("%d. %s" % (i+1, winner))
                i += 1

def __pretty_print_base(data, mark_winners, show_percent, filter_names):
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
        print("\n\nQ: %s\n" % question['title'])

        blank_votes = question['totals']['blank_votes']
        null_votes = question['totals']['null_votes']
        valid_votes = question['totals']['valid_votes']

        total_votes = blank_votes + null_votes + valid_votes

        percent_base = question['answer_total_votes_percentage']
        if percent_base == "over-total-votes":
          base_num = total_votes
        elif percent_base == "over-total-valid-votes":
          base_num = question['totals']['valid_votes']


        print("Total votes: %d" % total_votes)
        print("Blank votes: %d (%0.2f%%)" % (
            blank_votes,
            get_percentage(blank_votes, total_votes)))

        print("Null votes: %d (%0.2f%%)" % (
            null_votes,
            get_percentage(null_votes, total_votes)))

        print("Total valid votes (votes to options): %d (%0.2f%%)" % (
            valid_votes,
            get_percentage(valid_votes, total_votes)))
        print("\nOptions (percentages over %s, %d winners):" % (percent_base, question['num_winners']))

        if mark_winners:
            i = 1
            winners = [answer for answer in question['answers']
                if answer['winner_position'] != None]
            for answer in winners:
                if not show_percent:
                    print("%d. %s (%0.2f votes)" % (
                        i,
                        answer['text'],
                        answer['total_count']))
                else:
                    print("%d. %s (%0.2f votes, %0.2f%%)" % (
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
                    print("N. %s (%0.2f votes)" % (
                        loser['text'],
                        loser['total_count']))
                else:
                    print("N. %s (%0.2f votes, %0.2f%%)" % (
                        loser['text'],
                        loser['total_count'],
                        get_percentage(loser['total_count'], base_num)))
        else:
            answers = sorted([a for a in question['answers']],
                key=lambda a: float(a['total_count']), reverse=True)

            for i, answer in zip(range(len(answers)), answers):
                if not show_percent:
                    print("%d. %s (%0.2f votes)" % (
                        i + 1, answer['text'],
                        answer['total_count']))
                else:
                    print("%d. %s (%0.2f votes, %0.2f%%)" % (
                        i + 1, answer['text'],
                        answer['total_count'],
                        get_percentage(answer['total_count'], base_num)))
    print("")

def pretty_print_not_iterative(data_list, mark_winners=True):
    data = data_list[0]
    __pretty_print_base(data, mark_winners, show_percent=True,
        filter_names=["plurality-at-large", "borda-nauru", "borda", "pairwise-beta", "cup"])
