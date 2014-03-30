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

def __num_blank_votes(question, i, data):
    dirs = []
    for d in sorted(os.listdir(data['extract_dir'])):
        d = os.path.join(data['extract_dir'], d)
        if os.path.isdir(d):
            dirs.append(d)

    plaintexts = os.path.join(dirs[i], "plaintexts_json")

    # a blank vote is codified as num_answers + 3
    blank_vote_value = str(len(question['answers']) + 3)
    return int(subprocess.getoutput("grep \"%s\" %s | wc -l" % (
        blank_vote_value, plaintexts)))

def pretty_print_approval(data, mark_winners=True):
    counts = data['result']['counts']
    for question, i in zip(counts, range(len(counts))):
        if 'APPROVAL' not in question['a']:
            continue
        print("Q: %s\n" % question['question'])
        blank_votes = __num_blank_votes(question, i, data)

        print("Total votes: %d" % question['total_votes'])
        print("Blank votes: %d (%0.2f%%)" % (
            blank_votes, blank_votes*100/question['total_votes']))

        if mark_winners:
            i = 1
            for winner in question['winners']:
                answer = [a for a in question['answers'] if a['value'] == winner][0]
                print("%d. %s (%d votes)" % (
                    i, winner, answer['total_count']))
                i += 1

            losers = sorted([a for a in question['answers']
                            if a['value'] not in question['winners']],
                key=lambda a: float(a['total_count']), reverse=True)

            for loser in losers:
                print("N. %s (%d votes)" % (loser['value'], loser['total_count']))
        else:
            answers = sorted([a for a in question['answers']],
                key=lambda a: float(a['total_count']), reverse=True)

            for i, answer in zip(range(len(answers)), answers):
                print("%d. %s (%d votes)" % (i + 1, answer['value'],
                                             answer['total_count']))