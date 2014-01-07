#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import json
import numpy as np
from sklearn.neighbors import NearestNeighbors


if __name__ == "__main__":
    sessions = json.load(open("data/inference.json"))
    X = []
    inds = []
    for sid, session in sessions.iteritems():
        for pid, pres in session["presentations"].iteritems():
            if "lntheta" not in pres:
                continue
            X.append(map(float, pres["lntheta"]))
            inds.append(pid)
    X = np.array(X)
    nn = NearestNeighbors(10, algorithm="ball_tree").fit(X)
    dists, indices = nn.kneighbors(X)

    # print(indices)
    print(dists)
