# -*- coding:utf-8 -*-

import os
import copy
import json
import subprocess
import agora_tally.tally
from itertools import groupby, chain
from agora_results.pipes.base import Pipe
from agora_results.pipes import PipeReturnvalue
from jsonschema import validate

class stv_first_round_tiebreak(Pipe):
    @staticmethod
    def check_config(config):
        '''
        Implement this method to check that the input data is valid. It should
        be as strict as possible. By default, config is checked to be empty.
        '''

        '''
        TO DO: Aqui usar 'json_scheme' para comprobar que la configuración de config.json para este pipe es correcta.
        Los propiedades que puede recibir son:

        En caso contrario lanzar una excepción.
        '''
        #schema = {"type":"object","properties":{"question_indexes":{"type":"array"},"withdrawals":{"type":"array"},"ties_sorting":{"type":"array"}},"required":["question_indexes"]};
        #TENER EN CUENTA QUE SOLO SE PASA POR PARÁMETROS UN DATA_LIST, Y NO SE PRUEBA, POR LO QUE NO TIENE SENTIDO AÑADIR UN CHECK_CONFIG
        #validate(config, schema);
        
        if len(config) == 0:
            raise Exception("Pipe stv_first_round_tiebreak is not correctly configured.")
        
        return True 
    
    @staticmethod
    def execute(data, config):
        '''
        Executes the pipe. Should return a PipeReturnValue. "data" is the value
        that one pipe passes to the other, and config is the specific config of
        a pipe.
        '''
        stv_first_round_tiebreak.stv_first_round_tiebreak(data_list=data, **config)
        
        return PipeReturnvalue.CONTINUE
    @staticmethod
    def stv_first_round_tiebreak(data_list):
        '''
        Tie break algorithm for stv sorting of the winners.
    
        When in the first round some of the winners have the same number of
        votes for the first option in ballots, it tries to solve the tie comparing
        the number of second, third, etc option in ballots for each candidate.
    
        NOTE: it only works to resolve ties in the first round!
        '''
        data = data_list[0]
        # get the log to get the rounds
        tallies = []
        result = agora_tally.tally.do_tally(data['extract_dir'],
                                            data['result']['counts'],
                                            tallies)
    
        for tally in tallies:
            log = tally.get_log()
            question = data['result']['counts'][tally.question_num]
            if "STV" not in question['a']:
                continue
    
            q_winners = []
            choices = stv_first_round_tiebreak.__get_choices(data['extract_dir'], tally, question)
            for iteration, i in zip(log['iterations'], range(len(log['iterations']))):
                it_winners = [cand for cand in iteration['candidates']
                    if cand['status'] == 'won']
    
                it_winners = sorted(it_winners, key=lambda winner: float(winner['count']),
                                    reverse=True)
    
                # check if there are repeated counts
                len_set = len(set([i['count'] for i in it_winners]))
                if len_set != len(it_winners) and i == 0:
                    it_winners = stv_first_round_tiebreak.__stv_first_iteration_tie_break(
                        it_winners, iteration, i, data['extract_dir'], question,
                        choices, 1)
                for winner in it_winners:
                    q_winners.append(winner['name'])
    
            question['winners'] = q_winners
    @staticmethod
    def get_choices(extract_dir, tally, question):
        question_num = tally.question_num
        dirs = [os.path.join(extract_dir, d)
                for d in sorted(os.listdir(extract_dir))
                    if os.path.isdir(os.path.join(extract_dir, d))]
        votes_file = os.path.join(dirs[question_num], "plaintexts_json")
        choices = []
        with open(votes_file, 'r', encoding="utf-8") as f:
            for line in f.readlines():
                try:
                    # Note line starts with " (1 character) and ends with
                    # "\n (2 characters). It contains the index of the
                    # option selected by the user but starting with 1
                    # because number 0 cannot be encrypted with elgammal
                    # so we trim beginning and end, parse the int and
                    # substract one
                    number = int(line[1:-2]) - 1
                    choices.append(tally.parse_vote(number, question))
                except:
                    print("invalid vote: %s" % line)
        return choices
    @staticmethod
    def __stv_first_iteration_tie_break(
            it_winners, iteration, question_num, extract_dir, question, choices,
            break_position=1):
        '''
        Resolve tie
        '''
        tab_size = len(str(len(question['answers']) + 2))
        ties = [list(g) for k, g in groupby(
            it_winners, key=lambda winner: winner['count'])]
    
        list_opts = [a['value'] for a in question['answers']]
    
        def tie_break(winner):
            '''
            Given a winner, return the number of votes it received as a
            <break_position>
            '''
            n = 0
            for v in choices:
                if len(v) > break_position and\
                        v[break_position] == winner['name']:
                    n += 1
            return n
    
        for tie in ties:
            if len(tie) is 1:
                continue
            tiebroke_winners = []
            for winner in tie:
                winner['tie_break'] = tie_break(winner)
                tiebroke_winners.append(winner)
    
            # check if the tie was unresolved. This happens when the total
            # sum of tie_break nums is zero (i.e. no vote with the
            # break_position)
            total_sum = sum([winner['tie_break'] for winner in tie])
            if total_sum == 0:
                print("no way to break the tie even with break_pos = %d: %s" % (
                    break_position, json.dumps(tie)))
    
            tie = sorted(tiebroke_winners, key=lambda winner: winner['tie_break'],
                         reverse=True)
            # let's check if all ties have been broken
            recursive_ties = [list(g) for k, g in groupby(
                tie, key=lambda winner: winner['tie_break'])]
    
            # if not broken, go crazy recursive!
            if len(recursive_ties) != len(tie):
                for tie2 in recursive_ties:
                    if len(tie2) == 1:
                        continue
                    tie2 = stv_first_round_tiebreak.__stv_first_iteration_tie_break(tie2, iteration,
                                                        question_num, extract_dir,
                                                        question, choices,
                                                        break_position + 1)
    
                tie = list(chain.from_iterable(recursive_ties))
    
        return list(chain.from_iterable(ties))
