# -*- coding:utf-8 -*-

import json
from itertools import groupby, chain
import sys

def podemos_proportion_rounded_and_duplicates(data_list, women_names, proportions, withdrawed_candidates=[]):
    '''
    Given a list of woman names, returns a list of winners where the proportions
    of each sex is between the number provided.

    It also checks that the winners in the first question cannot win in the
    second.

    NOTE: it assumes the list of answers is already sorted.
    '''
    data = data_list[0]
    total = sum(proportions)
    proportions.sort()
    questions = data['results']['questions']
    first_question_winners = []
    first_question_winner_is_woman = None
    for question, question_index in zip(questions, range(len(questions))):
        num_winners = question['num_winners']
        max_samesex = int(num_winners*(proportions[1]/total))
        q_withdrawed = [a['id'] for a in withdrawed_candidates if a['question_num'] == question_index]

        if question['tally_type'] not in ["plurality-at-large"] or len(question['answers']) < 2 or question['num_winners'] < 2:
            last_winner = None
            num_won = 0
            for answer, i in zip(question['answers'], range(len(question['answers']))):
                if num_won < question['num_winners'] and answer['id'] not in q_withdrawed:
                    answer['winner_position'] = i
                    num_won += 1
                    last_winner = answer
                elif num_won == question['num_winners']:
                    answer['winner_position'] = None
                    if answer['total_count'] == last_winner['total_count'] and answer['id'] not in q_withdrawed:
                        print("it seems there is a tie in question '%s' with total_count = %d, '%s' vs '%s'" % (
                            question['title'], last_winner['total_count'], last_winner['text'], answer['text']), file=sys.stderr)
                else:
                    answer['winner_position'] = None

            # check if there's any removed winner that could have won and show
            # a warning if so
            last_winner_count = last_winner['total_count']
            removed_candidates = [
                '\'%s\'' % a['text']
                for a in question['answers']
                if a['text'] in first_question_winners and a['total_count'] >= last_winner_count]
            if len(removed_candidates) > 0:
                print("removed candidates that could have won: [%s]" % ", ".join(removed_candidates), file=sys.stderr)

            if question_index == 0:
                first_question_winners = [a['text'] for a in question['answers'] if a['winner_position'] is not None]
                first_question_winner_is_woman = first_question_winners[0] in women_names
            continue

        for answer, i in zip(question['answers'], range(len(question['answers']))):
            answer['winner_position'] = None

        def filter_women(l, women_names, question_index):
          return [
            a
            for a in l
            if a['text'] in women_names and a['text'] not in first_question_winners and\
            a['id'] not in q_withdrawed]
        def filter_men(l, women_names, question_index):
          return [
              a
              for a in l
              if a['text'] not in women_names and a['text'] not in first_question_winners and\
                a['id'] not in q_withdrawed]

        # remove withdrawed candidates
        running_candidates = [a for a in question['answers'] if a['text'] not in first_question_winners and\
                a['id'] not in q_withdrawed]
        women = filter_women(running_candidates, women_names, question_index)
        men = filter_men(running_candidates, women_names, question_index)
        num_winners = question['num_winners']

        base_winners = running_candidates[:num_winners]
        base_women_winners = filter_women(base_winners, women_names, question_index)
        base_men_winners = filter_men(base_winners, women_names, question_index)

        winners = base_women_winners + base_men_winners
        if len(base_women_winners) > max_samesex:
            n_diff =len(base_women_winners) - max_samesex
            winners = base_women_winners[:max_samesex] + men[:num_winners - max_samesex]
            print("too many women, len(base_women_winners)(%d) > max_samesex(%d)" % (len(base_women_winners), max_samesex), file=sys.stderr)
        elif len(base_men_winners) > max_samesex:
            n_diff =len(base_men_winners) - max_samesex
            winners = base_men_winners[:max_samesex] + women[:num_winners - max_samesex]
            print("too many men, len(base_men_winners)(%d) > max_samesex(%d)" % (len(base_men_winners), max_samesex), file=sys.stderr)

        winners = sorted(winners, reverse=True, key=lambda a: a['total_count'])

        # check for ties, filtering if there are other non winners with the same
        # total count of votes
        tie_val = winners[-1]['total_count']
        last_winner_name = winners[-1]['text']
        ties = [
            a for a in question['answers']
            if a['total_count'] == tie_val and a not in winners and answer['id'] not in q_withdrawed]
        if len(ties) > 0:
            tie_names = ", ".join(['\'%s\'' % tie['text'] for tie in ties])
            print("it seems there is a tie in question '%s' with total_count = %d, '%s' vs [%s]" % (
                question['title'], tie_val, last_winner_name, tie_names), file=sys.stderr)

        for answer, i in zip(winners, range(len(winners))):
            answer['winner_position'] = i

        # check if there's any removed winner that could have won and show
        # a warning if so
        removed_candidates = [
            '\'%s\'' % a['text']
            for a in question['answers']
            if a['text'] in first_question_winners and a['total_count'] >= tie_val]
        if len(removed_candidates) > 0:
            print("removed candidates that could have won: [%s]" % ", ".join(removed_candidates), file=sys.stderr)

        if question_index == 0:
          first_question_winners = [a['text'] for a in winners]
          first_question_winner_is_woman = first_question_winners[0] in women_names
