#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = ["AASReader"]

import json
import string
import random
from nltk.corpus import stopwords
from nltk import word_tokenize, sent_tokenize
from collections import defaultdict

stops = stopwords.words("english")


def tokenize(abstract):
    tokens = map(word_tokenize, sent_tokenize(abstract))
    tokens = [w for s in tokens for w in s]
    tokens = map(lambda w: w.strip(string.punctuation).lower(), tokens)
    return filter(lambda w: w not in stops and len(w) > 3, tokens)


def pre_analysis(json_path, txt_path):
    sessions = json.load(open(json_path, "r"))
    abstracts = {}
    for session in sessions.itervalues():
        for pres in session["presentations"].itervalues():
            abstracts[pres["id"]] = tokenize(unicode(pres["abstract"]))
    with open(txt_path, "w") as f:
        for k, a in abstracts.iteritems():
            f.write(("{0} {1}\n".format(k, " ".join(a))).encode("utf-8"))


class AASReader(object):

    def __init__(self, path):
        with open(path, "r") as f:
            lines = f.read().decode("utf-8").splitlines()

        self.abstracts = {}
        for line in lines:
            cols = map(lambda w: w.strip(), line.split())
            if len(cols) > 1:
                self.abstracts[cols[0]] = cols[1:]
        self.compute_vocab()
        self.abstracts = map(self.parse, self.abstracts.values())

        self.validation_set = []

    def compute_vocab(self, N=8000, skip=0):
        self.vocab = defaultdict(int)
        for a in self.abstracts.itervalues():
            for w in a:
                self.vocab[w] += 1
        self.vocab, counts = zip(*sorted(self.vocab.items(),
                                         key=lambda o: o[1], reverse=True))
        self.vocab = self.vocab[skip:skip+N]
        self.vocab = dict(zip(self.vocab, range(len(self.vocab))))

    def parse(self, a):
        return [self.vocab[w] for w in a if w in self.vocab]

    def validation(self, n):
        docs = []
        while len(docs) < n:
            doc = self.abstracts.pop(random.randint(0, len(self.abstracts)-1))
            docs.append(doc)
        return docs

    def __iter__(self):
        while True:
            yield self.abstracts[random.randint(0, len(self.abstracts)-1)]
