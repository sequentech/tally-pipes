# Introduction

Piece of software that processes a tally and given a pipeline it modifies the results. The name is just a joke. This is useful for example to post-process a tally to:
 - resolve tie-breaks (there can be many different algorithms to do that)
 - apply egalitarian criteria for men and women (sometimes this is even legaly mandated)
 - sort the winners of stv (which by default doesn't sort winners, just elect them)
 - other complex post-processing, like using the result of question 1 to select the first winner and then using the results of question 2 to sort the rest of the winners

# Installation

Just execute this (no stable release yet):

    $ pip install git+https://github.com/edulix/agora-tongo.git

# Usage

    $ agora-tongo --tally tally.tar.gz --config agora_tongo.test_config

Or the same shorter:

    $ agora-tongo -t tally.tar.gz -c agora_tongo.test_config

# Configuration file

Configuration file specifies the pipeline of functions to be applied to the results. This is an example configuration file (yes just one variable for the pipeline, at least for now):

    # -*- coding:utf-8 -*-
    RESULT_PIPELINE = (
        ("agora_tongo.pipes.tiebreak_stv", None),
        ("agora_tongo.pipes.zip_women_men", dict(
            questions=[0,1],
            women_names=["Enma Goldstein", "Ada Lovelace"],
            men_names=["Thomas Jefferson", "John Doe"]
            )),
    )

The available algorithms can be listed with:

    $ agora-tongo --list-pipes

And you can see how to use it with:

    $ agora-tongo --help "pipe.tiebreak_stv"

# Development

You can of course take a look at the available pipes in the agora_tongo/pipes/ subdirectory and see how to develop your own pipe. Be careful, you might cook the results in an unexpected way!

This software is in development state, that's why we haven't released any stable version yet. Patches and new pipes are welcome. We will review the pipe so that it does what is expected.

# More

You can see all the available commands with:

    $ agora-tongo --help

You can contact us at agora-ciudadana-devel@googlegroups.com mailing list or at #agoraciudadana freenode.net channel.