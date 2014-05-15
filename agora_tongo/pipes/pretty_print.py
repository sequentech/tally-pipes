# -*- coding:utf-8 -*-

import os
import subprocess

def pretty_print_stv_winners(data):
    counts = data['result']['counts']
    for question, i in zip(counts, range(len(counts))):
        if "STV" not in question['a']:
            continue

        print("Q: %s\n" % question['question'])
        winners = question['winners']
        for i, winner in zip(range(len(winners)), winners):
            print("%d. %s" % (i+1, winner))

def __num_blank_votes(question, i, data, blank_plus=3):
    dirs = []
    for d in sorted(os.listdir(data['extract_dir'])):
        d = os.path.join(data['extract_dir'], d)
        if os.path.isdir(d):
            dirs.append(d)

    plaintexts = os.path.join(dirs[i], "plaintexts_json")

    # a blank vote is codified as num_answers + blank_plus
    blank_vote_value = str(len(question['answers']) + blank_plus)
    return int(subprocess.getoutput("grep \"%s\" %s | wc -l" % (
        blank_vote_value, plaintexts)))

def __pretty_print_base(data, mark_winners, show_percent, filter_name, blank_plus):
    counts = data['result']['counts']
    for question, i in zip(counts, range(len(counts))):
        if filter_name not in question['a']:
            continue
        print("\n\nQ: %s\n" % question['question'])
        blank_votes = __num_blank_votes(question, i, data, blank_plus)

        print("Total votes: %d" % question['total_votes'])
        print("Blank votes: %d (%0.2f%%)" % (
            blank_votes, blank_votes*100/question['total_votes']))

        if mark_winners:
            i = 1
            for winner in question['winners']:
                answer = [a for a in question['answers'] if a['value'] == winner][0]
                if not show_percent:
                    print("%d. %s (%d votes)" % (
                        i,
                        winner,
                        answer['total_count']))
                else:
                    print("%d. %s (%d votes, %0.2f%%)" % (
                        i,
                        winner,
                        answer['total_count'],
                        answer['total_count']*100/question['total_votes']))
                i += 1

            losers = sorted([a for a in question['answers']
                            if a['value'] not in question['winners']],
                key=lambda a: float(a['total_count']), reverse=True)

            for loser in losers:
                if not show_percent:
                    print("N. %s (%d votes)" % (
                        loser['value'],
                        loser['total_count']))
                else:
                    print("N. %s (%d votes, %0.2f%%)" % (
                        loser['value'],
                        loser['total_count'],
                        loser['total_count']*100/question['total_votes']))
        else:
            answers = sorted([a for a in question['answers']],
                key=lambda a: float(a['total_count']), reverse=True)

            for i, answer in zip(range(len(answers)), answers):
                if not show_percent:
                    print("%d. %s (%d votes)" % (
                        i + 1, answer['value'],
                        answer['total_count']))
                else:
                    print("%d. %s (%d votes, %0.2f%%)" % (
                        i + 1, answer['value'],
                        answer['total_count'],
                        answer['total_count']*100/question['total_votes']))

def pretty_print_approval(data, mark_winners=True):
    __pretty_print_base(data, mark_winners, show_percent=False,
                        filter_name="APPROVAL", blank_plus=3)

def pretty_print_one_choice(data, mark_winners=True):
    __pretty_print_base(data, mark_winners, show_percent=True,
                        filter_name="ONE_CHOICE", blank_plus=2)