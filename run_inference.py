#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import json
import argparse
import numpy as np
import cPickle as pickle

from clda.lda import dirichlet_expectation
from reader import AASReader

parser = argparse.ArgumentParser(description="Show the topics from LDA")
parser.add_argument("model", help="The path to the model pickle")
parser.add_argument("parsed", help="The path to the parsed abstracts")
parser.add_argument("abstracts", help="The path to the abstracts dump")

if __name__ == "__main__":
    args = parser.parse_args()
    reader = AASReader(args.parsed)
    model = pickle.load(open(args.model))
    sessions = json.load(open(args.abstracts))

    for i, (aid, doc) in enumerate(zip(reader.ids, reader.abstracts)):
        if i % 100 == 0:
            print(i)
        sid, pid = aid.split(".")
        topics = model.infer(doc)
        lntheta = dirichlet_expectation(topics)
        sessions[sid]["presentations"][pid]["lntheta"] = list(lntheta)

    json.dump(sessions, open("data/inference.json", "w"), sort_keys=True,
              indent=2, separators=(",", ": "))
