#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import os
import argparse
import numpy as np
import cPickle as pickle

from clda.lda import dirichlet_expectation

parser = argparse.ArgumentParser(description="Show the topics from LDA")
parser.add_argument("model", help="The path to the model pickle")
parser.add_argument("-n", "--nwords", type=int, default=15,
                    help="The number of words to show")

if __name__ == "__main__":
    args = parser.parse_args()
    reader = pickle.load(
        open(os.path.join(os.path.dirname(os.path.abspath(args.model)),
                          "reader.pkl")))
    model = pickle.load(open(args.model))
    lnbeta = dirichlet_expectation(model.lam)
    vocab = [None for i in range(len(reader.vocab))]
    for w, k in reader.vocab.iteritems():
        vocab[k] = w
    for i, topics in enumerate(lnbeta):
        inds = np.argsort(topics)
        print(("Topic {0:3d}: ".format(i) +
               " ".join([vocab[i] for i in inds[-args.nwords:]]))
              .encode("utf-8"))
