#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json

data = open("abstracts.txt").read()

data = data.replace(" Contributing teams: ", "\rContributing teams: ")
data = data.replace("Õ", "'")
data = data.replace("Ò", "\"")
data = data.replace("Ó", "\"")

# Hack to deal with some stupid PDF reading problems.
data = re.sub(r" (?P<type>[a-zA-Z]+?) Session \xc3\x90 ",
              "\r\g<type> Session \xc3\x90 ",
              data)

data = re.sub(r"(?P<name>[0-9]) 1\. ",
              "\g<name>\r1. ",
              data)

# Split into lines.
lines = re.sub(r"\b[0-9]+? of 818", "\r", data).split("\r")

# Build the needed regular expressions.
session_re = re.compile(r"^([0-9]+?) \xc3\x90 (.*)$")
session_info_re = re.compile(r"^(.*?) \xc3\x90 (.*?) \xc3\x90 (.*)$")
pres_re = re.compile(r"^([0-9]+).([0-9A-Z]+) \xc3\x90 (.*)$")
author_re = re.compile(r"\b(.*?)((?:[0-9]+(?:(?:, )*))+)\b")
affil_re = re.compile(r"([0-9]+)\. (.*?)(?:(?=\s*[0-9]+\.)|$)")

sessions = {}


def parse_session(ind, match):
    sess_id, sess_name = match.groups()
    sess_type, sess_loc, sess_date = \
        session_info_re.match(lines[ind+1]).groups()
    ind += 2
    sess_desc = []
    while (pres_re.match(lines[ind]) is None and
            session_re.match(lines[ind]) is None):
        sess_desc.append(lines[ind])
        ind += 1
    sessions[sess_id] = dict(id=sess_id, title=sess_name, type=sess_type,
                             room=sess_loc, date=sess_date,
                             abstract=" ".join(sess_desc),
                             presentations={})
    return ind


def parse_presentation(ind, match):
    sess_id, pres_id, pres_name = match.groups()

    # Parse the author list until we hit affiliations.
    ind += 1
    i = 1
    while affil_re.match(lines[ind+i-1]) is None:
        authors = author_re.findall(" ".join(lines[ind:ind+i]))
        i += 1
    ind += i-1

    # Coerce the authors in to author affiliation pairs.
    authors = map(lambda (au, affil): (au, map(lambda a: a.strip().strip(","),
                                               affil.split())), authors)

    # Get the full list of necessary affiliation keys.
    all_affils = set([a for au, affils in authors for a in affils])

    flag = False
    i = 1
    while not flag:
        affils = dict(affil_re.findall(" ".join(lines[ind:ind+i])))
        check = [a in affils for a in all_affils]
        l = lines[ind+i-1]
        if len(l) and l.strip()[-1] == "." and all(check):
            break
        i += 1
    ind += i

    # Get the abstract.
    desc = []
    while ind < len(lines) and (pres_re.match(lines[ind]) is None and
                                session_re.match(lines[ind]) is None):
        desc.append(lines[ind])
        ind += 1

    # Save the abstract.
    sessions[sess_id]["presentations"][pres_id] \
        = dict(id="{0}.{1}".format(sess_id, pres_id),
               title=pres_name,
               authors=authors, affiliations=affils,
               abstract=" ".join(desc))

    return ind


i = 0
while i < len(lines):
    line = lines[i]
    sess_match = session_re.match(line)
    if sess_match is not None:
        i = parse_session(i, sess_match)
        continue
    pres_match = pres_re.match(line)
    if pres_match is not None:
        i = parse_presentation(i, pres_match)
        continue
    print("Skipping: ", lines[i])
    i += 1

json.dump(sessions, open("abstracts.json", "w"), sort_keys=True, indent=2,
          separators=(",", ": "))
