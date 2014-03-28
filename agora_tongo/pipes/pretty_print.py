# -*- coding:utf-8 -*-

def pretty_print(data):
    '''
    Prints the data. We of course asume that the data is already sorted, that's
    what the pipeline is for.
    '''
    for question in data['result']['counts']:
        print("Q: %s\n" % question['question'])

        if "STV" in question['a']:
            stv_answers(question)
        elif "APPROVAL" in question['a']:
            approval_answers(question)

def stv_answers(question):
    answers = question['answers']
    for i, answer in zip(range(len(answers)), answers):
        print("%d. %s (votes)" % (i, answer['value']))

def approval_answers(question):
    print("Total votes: %d" % question['total_votes'])
    answers = question['answers']
    for i, answer in zip(range(len(answers)), answers):
        print("%d. %s (%d votes)" % (
            i, answer['value'], answer['total_count']))