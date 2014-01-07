#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = []

import os
import sys
import time
import numpy as np
from clda.lda import LDA
import cPickle as pickle
from multiprocessing import Pool
from reader import AASReader, pre_analysis

if __name__ == "__main__":
    if "--parse" in sys.argv:
        pre_analysis("abstracts.json", "parsed.txt")
        sys.exit(0)

    outdir = "results"

    print("Parsing abstracts")
    reader = AASReader("parsed.txt")
    pickle.dump(reader, open(os.path.join(outdir, "reader.pkl"), "w"), -1)

    valid = reader.validation(300)
    nvalid = sum([len(s) for s in valid])

    # Set up the model.
    pool = Pool()
    model = LDA(100, len(reader.vocab), 0.01, 0.01, tau=1024, kappa=0.5)
    p = model.elbo(valid, pool=pool)

    # Run EM.
    fn = os.path.join(outdir, "model.{0:04d}.pkl")
    outfn = os.path.join(outdir, "convergence.txt")
    open(outfn, "w").close()
    tot = 0.0
    nxt = 0.1
    batch = 1024
    ndocs = len(reader.abstracts) + len(valid)
    strt = time.time()
    for i, (n, lam) in enumerate(model.em(reader, ndocs=ndocs, pool=pool,
                                          batch=batch)):
        if np.log10(tot+time.time()-strt) > nxt:
            tot += time.time() - strt
            p = np.exp(-model.elbo(valid, pool=pool, ndocs=ndocs)/nvalid)
            print(i, tot, p)
            open(outfn, "a").write("{0} {1} {2}\n".format(i*batch, tot,
                                                          p))
            pickle.dump(model, open(fn.format(i), "wb"), -1)
            strt = time.time()
            nxt += 0.1
