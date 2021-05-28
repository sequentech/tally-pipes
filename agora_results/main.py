# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2014-2021  Agora Voting SL <agora@agoravoting.com>

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
import copy
import signal
import json
import tempfile
import shutil
import tarfile
import codecs
import uuid


VERSION = "1.0"

DEFAULT_PIPELINE = dict(
    version=VERSION,
    pipes=[
        dict(
            type='agora_results.pipes.pdf.configure_pdf',
            params=dict(
                languages=['en']
            )
        ),
        dict(
            type='agora_results.pipes.results.do_tallies',
            params={}
        ),
        dict(
            type="agora_results.pipes.sort.sort_non_iterative",
            params={}
        )
    ]
)

# By default we only allow the most used pipes to reduce default attack surface
# NOTE: keep the list sorted
DEFAULT_PIPES_WHITELIST = [
    #"agora_results.pipes.desborda.podemos_desborda",
    #"agora_results.pipes.desborda2.podemos_desborda2",
    #"agora_results.pipes.desborda3.podemos_desborda3",
    #"agora_results.pipes.desborda4.podemos_desborda4",
    #"agora_results.pipes.duplicate_questions.duplicate_questions",
    "agora_results.pipes.modifications.apply_modifications",
    #"agora_results.pipes.multipart.make_multipart",
    #"agora_results.pipes.multipart.election_max_size_corrections",
    #"agora_results.pipes.multipart.question_totals_with_corrections",
    #"agora_results.pipes.multipart.reduce_answers_with_corrections",
    #"agora_results.pipes.multipart.multipart_tally_plaintexts_append_joiner",
    #"agora_results.pipes.multipart.data_list_reverse",
    #"agora_results.pipes.multipart.multipart_tally_plaintexts_joiner",
    #"agora_results.pipes.multipart.append_ballots",
    "agora_results.pipes.parity.proportion_rounded",
    "agora_results.pipes.parity.parity_zip_non_iterative",
    "agora_results.pipes.parity.reorder_winners",
    "agora_results.pipes.parity.podemos_parity_loreg_zip_non_iterative",
    "agora_results.pipes.parity.podemos_parity2_loreg_zip_non_iterative",
    #"agora_results.pipes.podemos.podemos_proportion_rounded_and_duplicates",
    #"agora_results.pipes.pretty_print.pretty_print_stv_winners",
    "agora_results.pipes.pretty_print.pretty_print_not_iterative",
    "agora_results.pipes.results.do_tallies",
    #"agora_results.pipes.results.to_files",
    #"agora_results.pipes.results.apply_removals",
    "agora_results.pipes.sort.sort_non_iterative",
    #"agora_results.pipes.stv_tiebreak.stv_first_round_tiebreak",
    "agora_results.pipes.pdf.configure_pdf",
    "agora_results.pipes.withdraw_candidates.withdraw_candidates",
    #"agora_results.pipes.ballot_boxes.count_tally_sheets"
]


def extract_tally(fpath):
    '''
    extracts the tally and loads the results into a file for convenience
    '''
    extract_dir = tempfile.mkdtemp()
    tar = tarfile.open(fpath)
    tar.extractall(extract_dir)
    tar.close()
    return extract_dir

def print_csv(data, separator, output_func=print):
    counts = data['results']['questions']
    for question, i in zip(counts, range(len(counts))):
        if question['tally_type'] not in ["plurality-at-large", "desborda", "desborda2", "desborda3", "borda", "borda-nauru", "cumulative"] or\
           question.get('no-tally', False):
            continue

        output_func(separator.join(["Question"]))
        output_func(separator.join(["Number", "Title"]))
        output_func(separator.join([str(i + 1), question['title']]))
        output_func(separator*2)

        output_func(separator.join(["Totals"]))

        question_total = (question['totals']['null_votes']
            + question['totals']['blank_votes']
            + question['totals']['valid_votes'])

        output_func(separator.join(["Total votes", str(question_total)]))
        output_func(separator.join(["Blank votes", str(question['totals']['blank_votes'])]))
        output_func(separator.join(["Null votes", str(question['totals']['null_votes'])]))
        output_func(separator.join(["Valid votes", str(question['totals']['valid_votes'])]))
        output_func(separator*2)

        output_func(separator.join(["Answers"]))
        output_func(separator.join(["Id", "Text", "Category", "Total votes", "Winner position"]))
        for answer in question['answers']:
            output_func(separator.join([
                str(answer['id']),
                answer['text'],
                answer['category'],
                str(answer['total_count']),
                str(answer['winner_position'])]))

def pretty_print(data, output_func=print):
    from agora_results.pipes.pretty_print import pretty_print_not_iterative
    pretty_print_not_iterative([data], output_func=output_func)

def print_results(
    data, output_format,
    output_func=print,
    election_config=None,
    election_id=None
):  
  '''
  print results in the specified output format
  '''
  if "json" == output_format:
    output_func(
        json.dumps(
            data['results'],
            indent=4,
            ensure_ascii=False,
            sort_keys=True,
            separators=(',', ': ')
        )
    )
  elif "csv" == output_format:
      print_csv(data, separator=",", output_func=output_func)
  elif "tsv" == output_format:
      print_csv(data, separator="\t", output_func=output_func)
  elif "pretty" == output_format:
      pretty_print(data, output_func=output_func)
  elif "pdf" == output_format:
      from agora_results.pipes.pdf import pdf_print
      try:
          pdf_print(data, election_config, election_id)
      except Exception:
          pass

def func_path_sanity_checks(func_path, pipes_whitelist):
    '''
    Check that the func path is valid and reasonably secure
    '''
    if pipes_whitelist is not None and func_path not in pipes_whitelist:
        raise Exception("Pipe not in the whitelist: %s" % func_path)

    values = func_path.split(".")
    if " " in func_path or len(values) == 0 or len(values) > 4 or\
        values[0] != "agora_results" or values[1] != "pipes":
        raise Exception()

    for val in values:
        if len(val) == 0 or val.startswith("_"):
            raise Exception()

def execute_pipeline(pipeline_info, data_list, pipes_whitelist=None):
    '''
    Execute a pipeline of options. pipeline_info must be a list of
    pairs. Each pair contains (pipe_func_path, params), where pipe_func_path is
    the path to the module and a function name, and params is either
    None or a dictionary with extra parameters accepted by the function.

    Pipeline functions must accept always at least one parameter, 'data', which
    will initially be the data parameter of this function, but each function is
    allow to modify it as a way to process the data.

    The other parameters of the function will be the "params" specified for
    that function in 'pipeline_info', which can either be None or a dict, and
    the format is of your choice as a developer.
    '''
    # verify format
    if (
        type(pipeline_info) is not dict or
        'version' not in pipeline_info or
        type(pipeline_info['version']) is not str or
        pipeline_info['version'] != VERSION or
        'pipes' not in pipeline_info or
        type(pipeline_info['pipes']) is not list
    ):
        raise Exception('Invalid pipeline')

    # verify each pipe format and sanity
    for pipe in pipeline_info['pipes']:
        if (
            type(pipe) is not dict or
            'type' not in pipe or
            type(pipe['type']) is not str or
            'params' not in pipe or
            type(pipe['params']) is not dict
        ):
            raise Exception('Invalid pipe: %r' % pipe)
        func_path_sanity_checks(pipe['type'], pipes_whitelist)

    # execute the pipes
    for pipe in pipeline_info['pipes']:
        # get access to the function
        func_path = pipe['type']
        kwargs = pipe['params']

        func_name = func_path.split(".")[-1]
        module = __import__(
            ".".join(func_path.split(".")[:-1]), globals(), locals(),
            [func_name], 0)
        fargs = dict(data_list=data_list)
        if kwargs is not None:
            fargs.update(kwargs)
        ret = getattr(module, func_name)(**fargs)

    return data_list

def read_file(path):
    with codecs.open(path, 'r', encoding="utf-8") as f:
        return f.read()

def write_file(path, data):
    with codecs.open(path, 'w', encoding="utf-8") as f:
        f.write(data)

def serialize(data):
    return json.dumps(data,
        indent=4, ensure_ascii=False, sort_keys=True, separators=(',', ': '))

def create_ephemeral_tally(econfig_path):
    '''
    Creates a tally in a temporal directory from an election config
    '''
    tmp_dir = tempfile.mkdtemp()
    econfig_txt = read_file(econfig_path)
    econfig = json.loads(econfig_txt)

    write_file(
        os.path.join(tmp_dir, "questions_json"),
        serialize(econfig["questions"]))

    for i in range(len(econfig["questions"])):
        session_id = "%d-%s" % (i, str(uuid.uuid4()))
        os.mkdir(os.path.join(tmp_dir, session_id))
        write_file(os.path.join(tmp_dir, session_id, "plaintexts_json"), "")

    return tmp_dir

def main(pargs):
    # load config
    if pargs.config is not None:
      with codecs.open(pargs.config, 'r', encoding="utf-8") as f:
          pipeline_info = json.loads(f.read())
    else:
      pipeline_info = DEFAULT_PIPELINE

    # load allowed pipes: Format of the file should simply be: one pipe per line
    if pargs.pipes_whitelist is not None:
        with codecs.open(pargs.pipes_whitelist, 'r', encoding="utf-8") as f:
            pipes_whitelist = [l.strip() for l in f.readlines()]
    else:
      pipes_whitelist = DEFAULT_PIPES_WHITELIST

    data_list = []

    # remove files on abrupt external exit signal
    def sig_handler(signum, frame):
        if not pargs.stdout:
            print("\nTerminating: deleting temporal files..")
        for data in data_list:
            if os.path.exists(data["extract_dir"]):
                shutil.rmtree(data["extract_dir"])
        exit(1)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    try:
        if len(pargs.tally) == 0 and len(pargs.election_config) == 0:
            print("You need to specify at least one tally or election-config")
            exit(1)

        if len(pargs.tally) > 0 and len(pargs.election_config) > 0:
            print("You can't specify both a tally and an election-config")
            exit(1)

        if len(pargs.election_config) > 0:
            for econfig_path in pargs.election_config:
                tmp_dir = create_ephemeral_tally(econfig_path)
                if not pargs.stdout:
                    print("Ephemeral tally for config %s in %s.." %
                        (econfig_path, tmp_dir))
                data_list.append(dict(extract_dir=tmp_dir))
        else:
            # extract each tally, before starting the pipeline, and put the tally
            # relevant data in a list that is processed by the pipeline
            for tally in pargs.tally:
                extract_dir = extract_tally(tally)
                if not pargs.stdout:
                    print("Extracted tally %s in %s.." % (tally, extract_dir))
                data_list.append(dict(extract_dir=extract_dir))

        # tar tallies generates a tar file containing everything related to
        # the results. It also creates a randomly named subdirectory with
        # all the exportable data.

        priv_results_uuid = None
        priv_results_dirname = None
        priv_results_path = None
        ballots_csv_file = None
        ballots_json_file = None

        if pargs.tar and len(data_list) > 0:
            from glob import glob
            existing_priv_results = glob(os.path.join(pargs.tar, "results-*"))

            # if there's any existing priv_results_path, reuse it if there's
            # only one
            if len(existing_priv_results) != 1:
                # if there were more than 1, remove all and replace them
                for existing_priv_result in existing_priv_results:
                    shutil.rmtree(existing_priv_result)

                # in any case, create a new one
                from uuid import uuid4
                priv_results_uuid = str(uuid4())
                priv_results_dirname = "results-%s" % priv_results_uuid
                priv_results_path = os.path.join(pargs.tar, priv_results_dirname)

                # create the priv results
                os.mkdir(priv_results_path)
                
            # reuse the existing results directory
            else:
                priv_results_path = existing_priv_results[0]
                priv_results_dirname = os.path.basename(priv_results_path)

            ballots_csv_path = os.path.join(priv_results_path, "ballots.csv")
            ballots_csv_file = open(ballots_csv_path, "w")

            ballots_json_path = os.path.join(priv_results_path, "ballots.json")
            ballots_json_file = open(ballots_json_path, "w")
            
            def ballots_printer(vote, question, question_num, exception):
                '''
                Function used by the results.do_tallies pipe to dump the ballots 
                in both CSV an JSON format.
                '''

                # initialize output votes
                vote_str = [str(question_num)]
                vote_json = copy.deepcopy(question)
                vote_json['question_num'] = question_num
                vote_json['ballot_flags'] = dict(
                    blank_vote=False,
                    null_vote=False
                )
                if 'winners' in vote_json:
                    del vote_json['winners']
                if 'totals' in vote_json:
                    del vote_json['totals']

                for vote_answer in vote_json['answers']:
                    # transpose url info into the answer
                    for url in vote_answer.get('urls', []):
                        key = url['title']
                        value = url['url']
                        vote_answer[key] = value
                    # empty urls
                    vote_answer['urls'] = []
                    if 'winner_position' in vote_answer:
                        del vote_answer['winner_position']

                # detect blank and null votes and mark accordingly
                if vote == "BLANK_VOTE":
                    vote_str += ["BLANK_VOTE"]
                    vote_json['ballot_flags']['blank_vote'] = True
                elif vote == "NULL_VOTE":
                    vote_str += ["NULL_VOTE"]
                    vote_json['ballot_flags']['null_vote'] = True
                else:
                    if question['tally_type'] != 'cumulative':
                        sorted_vote = sorted(
                            list(vote),
                            key=lambda choice: choice.points,
                            reverse=True
                        )
                    else:
                        sorted_vote = vote
                    for mark_position, choice in enumerate(sorted_vote):
                        choice_answer = question['answers'][choice.answer_id]
                        answer_index = choice.answer_id
                        if isinstance(choice.key, str):
                            choice_text = choice.key
                            vote_json['answers'][answer_index]['text'] = choice.key
                        else:
                            choice_text = choice_answer['text']

                        if question['tally_type'] == 'cumulative':
                            vote_str += [
                                "\"%d. %s\"" % (
                                    choice.points,
                                    choice_text
                                )
                            ]
                            vote_json['answers'][answer_index]['ballot_marks'] = choice.points
                        else:
                            if question['tally_type'] in ['desborda', 'desborda2', 'desborda3']:
                                vote_str += [
                                    "\"%d. %s\"" % (
                                        choice.points,
                                        choice_text
                                    )
                                ]
                            else:
                                vote_str += [
                                    "\"%d. %s\"" % (
                                        choice_answer['id'],
                                        choice_text
                                    )
                                ]
                                if question['tally_type'] == 'plurality-at-large':
                                    vote_json['answers'][answer_index]['ballot_marks'] = 1
                                else:
                                    vote_json['answers'][answer_index]['ballot_marks'] = mark_position
                            
                
                if question['tally_type'] != 'cumulative':
                    # Remove answers not marked by the voter in non-cumulative
                    vote_json['answers'] = [x for x in vote_json['answers'] if 'ballot_marks' in x]

                ballots_csv_file.write(",".join(vote_str,) + "\n")
                # we sort keys to make it reproducible
                ballots_json_file.write(json.dumps(vote_json, sort_keys=True) + "\n")

            data_list[0]['ballots_printer'] = ballots_printer

        execute_pipeline(
            pipeline_info,
            data_list,
            pipes_whitelist=pipes_whitelist
        )

        config_folder = ''
        if pargs.config is not None:
            config_folder = os.path.dirname(pargs.config)

        # tar tallies generates a tar file containing everything related to
        # the results. It also creates a randomly named subdirectory with
        # all the exportable data.
        if ballots_csv_file:
            ballots_csv_file.close()
        if ballots_json_file:
            ballots_json_file.close()

        if pargs.tar and len(data_list) > 0 and 'results' in data_list[0]:
            data_list[0]['results']['results_dirname'] = priv_results_dirname
            from agora_results.utils.tallies import tar_tallies
            tar_tallies(data_list, pipeline_info, pargs.tally, pargs.tar, pargs.election_id)

            # dump the results in CSV,JSON and PRETTY format in the
            # priv-results dir
            for res_format in ['csv', 'json', 'pretty', 'pdf']:
                fpath = os.path.join(
                    priv_results_path,
                    "%d.results.%s" % (pargs.election_id, res_format)
                )
                with open(fpath, "w") as f:
                    output_func = lambda s: f.write(s + "\n")
                    print_results(
                        data_list[0], 
                        res_format, 
                        output_func, 
                        election_config=priv_results_path, 
                        election_id=pargs.election_id
                    )

        if (
            (
                pargs.stdout or 
                (pargs.output_format and 'pdf' == pargs.output_format)
            ) and 
            len(data_list) > 0 and 
            'results' in data_list[0]
        ):
            print_results(
                data_list[0], 
                pargs.output_format, 
                print, 
                election_config=config_folder, 
                election_id=pargs.election_id
            )

    finally:
        if not pargs.stdout:
            print("Deleting temporal files..")
        for data in data_list:
            if os.path.exists(data["extract_dir"]):
                shutil.rmtree(data["extract_dir"])
