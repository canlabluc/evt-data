"""
Checks data that has been both df-transformed and had segments
that erroneously marked the entire trial space as clean removed.
"""

import os
import sys
import glob

import numpy as np
import pandas as pd

def get_filelist(import_path, extension):
  """
  Returns list of file paths from import_path with specified extension.
  """
  filelist = []
  for root, dirs, files in os.walk(import_path):
      filelist += glob.glob(os.path.join(root, '*.' + extension))
      return filelist

TYPES_START = ['11', '10']
TYPES_STOP = ['21', '20']
SEGS_START = ['C1', 'O1']
SEGS_STOP = ['C2', 'O2']
files = get_filelist('df-data-clean/', 'evt')
for f in files:
    fname = f.split('/')[-1]
    df = pd.read_csv(f, sep='\t')
    found_bad_segs = False

    for i in range(df.shape[0]):
        if df.iloc[i].Type[0:2] in TYPES_START:
            intertrial = False
        elif df.iloc[i].Type[0:2] in TYPES_STOP:
            intertrial = True

        if df.iloc[i].Type[0:2] in SEGS_START and intertrial == True:
            found_bad_segs = True
            length = df.iloc[i+1].Latency - df.iloc[i].Latency
            print('{} | {} -> {} | {} | Next: '.format(fname, df.iloc[i].Type, df.iloc[i+1].Type, length/512), end='')
            try:
                next_event = df.iloc[i+2].Type
                print(next_event)
            except:
                print('EOF')

    if found_bad_segs == True:
        print()
