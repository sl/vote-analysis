import pandas
import os
from io import StringIO
import numpy as np
import re

VOTES_FOLDER = 'data/votes'

print('loading constituent ideology data')
ideology_raw = pandas.read_csv('data/ideology.csv', sep=',').as_matrix()

ideology = {}

for row in ideology_raw:
    ideology[row[0]] = row[1]

print(ideology)

print('\nloading vote data...\n')

vote_data_strings = []


def lookup(file):
    return os.path.getctime(VOTES_FOLDER + '/' + file)

files = sorted(os.listdir(VOTES_FOLDER), key=lookup)

for file_name in files:
    # check to make sure it's not a bogus operating system file
    if file_name.endswith('.csv'):
        data = None

        with open(VOTES_FOLDER + '/' + file_name, 'r') as file:
            data = file.read()

        if data != None:
            [name, data] = data.split('\n', 1)
            print('loading: ' + name + '\n')
            vote_data_strings.append((name, data))

print('loaded ' + str(len(vote_data_strings)) + ' voting records')

print('processing voting records...\n')

vote_results = []

def format(value):
    if isinstance(value, str) and value.startswith('Sen. '):
        cleaned = value[5:] # remove "Sen. " from the front of the string
        cleaned = re.sub('\\[(.*?)\\]', '', cleaned).strip()
        return cleaned
    return value

v_format = np.vectorize(format)

# boolean to a vote string
def bts(b):
    if b:
        return "Yea"
    else:
        return "Nay"

# if a vote is valid
def vvalid(vote):
    return vote == "Yea" or vote == "Nay"

for (vote_name, raw) in vote_data_strings:
    vote_data = pandas.read_csv(StringIO(raw), sep=',')
    vote_data = vote_data.drop(columns=['person', 'state', 'district'])
    repubs_raw = vote_data[vote_data['party'].str.contains("Republican")]
    dems_raw = vote_data[vote_data['party'].str.contains("Democrat")]

    vote_data = v_format(vote_data)

    repubs = v_format(repubs_raw)
    dems = v_format(dems_raw)

    demyes = 0
    demno = 0

    for [vote, name, party] in dems:
        if vote == "Yea":
            demyes = demyes + 1
        elif vote == "Nay":
            demno = demno + 1

    repubyes = 0
    repubno = 0

    for [vote, name, party] in repubs:
        if vote == "Yea":
            repubyes = repubyes + 1
        elif vote == "Nay":
            repubno = repubno + 1

    dem_vote = demyes > demno
    repub_vote = repubyes > repubno

    total_votes = demyes + demno + repubyes + repubno

    dem_against = []
    dem_with = []
    for [vote, name, party] in dems:
        if bts(dem_vote) != vote and vvalid(vote):
            dem_against.append(name)
        elif vvalid(vote):
            dem_with.append(name)

    repub_against = []
    repub_with = []
    for [vote, name, party] in repubs:
        if bts(repub_vote) != vote and vvalid(vote):
            repub_against.append(name)
        elif vvalid(vote):
            repub_with.append(name)

    print('democrats against:')
    print(dem_against)
    print('republicans against:')
    print(repub_against)

    against = dem_against + repub_against

    print()

    # lookup how many of those have differing constituent ideology

    dci = 0
    for name in against:
        if not name in ideology:
            print('WARNING: Found no ideology lookup for "' + name + '"')
            continue
        dci = dci + ideology[name]

    with_party = dem_with + repub_with

    dci_with = 0
    for name in with_party:
        if not name in ideology:
            print('WARNING: Found no ideology lookup for "' + name + '"')
            continue
        dci_with = dci_with + ideology[name]

    along = total_votes - len(against)

    vote_results.append((vote_name, len(against), dci, along, dci_with))

print('\n')
print('============================ RESULTS ============================')
print()

for (name, against, dci_against, along, dci_with) in vote_results:
    print('Vote: ' + str(name))
    print('Against Party Lines: ' + str(against))
    print('With DCI: ' + str(dci_against))
    print('Along party lines: ' + str(along))
    print('With DCI: ' + str(dci_with))
    print()
