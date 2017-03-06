"""
This script computes and displays stats for the evt files in data/raw.
"""

import os
import glob

import xmltodict
import pandas as pd


def get_filelist(import_path, extension):
  """
  Returns list of file paths from import_path with specified extension.
  """
  filelist = []
  for root, dirs, files in os.walk(import_path):
      filelist += glob.glob(os.path.join(root, '*.' + extension))
      return filelist


def get_event_file(filepath, include_clean_segs=True):
    events = {}
    xmlevents = xmltodict.parse(open(filepath).read())
    xmlevents = xmlevents['EMSE_Event_List']['Event']
    n = 0
    for i in range(len(xmlevents)):
        if include_clean_segs == True and xmlevents[i]['Name'] in ['C', 'O']:
            # First, add front of clean segment
            events[n] = {'type': '', 'latency': 0, 'urevent': 0}
            events[n]['type'] = xmlevents[i]['Name'] + '1'
            events[n]['latency'] = int(xmlevents[i]['Start'])
            events[n]['urevent'] = n

            # Then add the end of the clean segment
            n += 1
            events[n] = {'type': '', 'latency': 0, 'urevent': 0}
            events[n]['type'] = xmlevents[i]['Name'] + '2'
            events[n]['latency'] = int(xmlevents[i]['Stop'])
            events[n]['urevent'] = n
            n += 1
        if len(xmlevents[i]['Name']) == 3 and xmlevents[i]['Name'] not in ['255', '222', '223', '252']:
            events[n] = {'type': '', 'latency': 0, 'urevent': 0}
            events[n]['type'] = xmlevents[i]['Name']
            events[n]['latency'] = int(xmlevents[i]['Start'])
            events[n]['urevent'] = n
            n += 1
    return events


def print_events(files, include_clean_segs=False):
    for file in files:
        evts = get_event_file(file, include_clean_segs)
        print(file.split('/')[-1])
        for i in range(len(evts)):
            print(evts[i]['type'])


def get_num_extractable_windows(events, print_info=True):
    """
    Helper function that returns the total number of windows and seconds
    able to be extracted from a specified resting state recording.
    Arguments
        events:     List of event codes, each event in the format: [port_code, time_point],
                    such as ['C1', 10249]
        port_code:  String specifying the events to extract. For example, 'C1' or 'O1'
                    for eyes-closed and eyes-open resting state data, respectively.
        print_info: Boolean specifying whether to print info to the terminal.

    get_num_extractable_windows assumes that we're looking for windows of 2-second lengths,
    with 50% overlap. Thus, 3 seconds of extractable data provides us with 2 windows.
    """
    total_wins = 0
    total_secs = 0
    for event in events:
        # If we can extract at least two seconds...
        if (event[1] - event[0]) >= 1024:
            points = event[1] - event[0]
            secs   = (event[1] - event[0])//512
            nwin   = (event[1] - event[0])//512 - 1 # Assuming 50% window overlap.
            total_wins += nwin
            total_secs += secs
            if print_info == True:
                print('Event {}:\t{} points, {} seconds, {} windows'.format(event, points, secs, nwin))
    if print_info == True:
        print('Total windows able to be extracted: ', total_wins)
        print('Total seconds able to be extracted: ', total_secs)
    total_secs = total_wins + 1
    return total_wins, total_secs


def print_evt_information(filepath, include_clean_segs=False, print_in_secs=True):
    """
    Prints general information about a specified .evt file.
    Inputs:
        filepath: String, specifies full path to a .evt file.
        print_clean_segs: Boolean, specifies whether to print information regarding
                          the segments that have been marked as being clean.
        print_in_secs: Boolean, specifies whether to print .evt information in seconds,
                       as opposed to timepoints. Assumes 512 sampling rate.
    """
    trials = get_event_file(filepath, include_clean_segs)
    # clean_segs = get_event_file(filepath, clean_segs_only=True)
    eyesc_trials = 0
    eyeso_trials = 0
    eyesc_trial_length = 0
    eyeso_trial_length = 0
    for i in range(len(trials)-1):
        # Eyes-closed trial
        if trials[i]['type'][0:2] == '10' and trials[i+1]['type'][0:2] == '20':
            eyesc_trials += 1
            eyesc_trial_length += trials[i+1]['latency'] - trials[i]['latency']
        # Eyes-open trial
        elif trials[i]['type'][0:2] == '11' and trials[i+1]['type'][0:2] == '21':
            eyeso_trials += 1
            eyeso_trial_length += trials[i+1]['latency'] - trials[i]['latency']
    eyesc_trial_length /= eyesc_trials
    eyeso_trial_length /= eyeso_trials
    if print_in_secs:
        eyesc_trial_length /= 512;
        eyeso_trial_length /= 512;
    if eyesc_trials != 4 or eyeso_trials != 4:
        print('\t{0} | eyesc_trials: {1} | eyeso_trials: {2} | eyesc_trial_length: {3} | eyeso_trial_length: {4}'.format(\
            filepath.split('/')[-1], eyesc_trials, eyeso_trials, eyesc_trial_length, eyeso_trial_length))
    else:
        print('{0} | eyesc_trials: {1} | eyeso_trials: {2} | eyesc_trial_length: {3} | eyeso_trial_length: {4}'.format(\
            filepath.split('/')[-1], eyesc_trials, eyeso_trials, eyesc_trial_length, eyeso_trial_length))


files = get_filelist('data/raw/', 'evt')
for f in files:
    clean_segs = []
    events = get_event_file(f, include_clean_segs=True)
    for i in range(len(events)):
        if events[i]['type'] in ['C1', 'O1', 'C2', 'O2']:
            clean_segs.append([events[i]['type'], int(events[i]['latency'])])
    eyesc_segs = []
    eyeso_segs = []
    for i in range(len(clean_segs)-1):
        if clean_segs[i][0] == 'C1':
            eyesc_segs.append([clean_segs[i][1], clean_segs[i+1][1]])
        if clean_segs[i][0] == 'O1':
            eyeso_segs.append([clean_segs[i][1], clean_segs[i+1][1]])

    # print(clean_segs)
    nwins_eyesc, nsecs_eyesc = get_num_extractable_windows(eyesc_segs, print_info=False)
    nwins_eyeso, nsecs_eyeso = get_num_extractable_windows(eyeso_segs, print_info=False)

    print_evt_information(f)
    print('\tN Extractable EyesC Wins: {} | N Extractable EyesC Secs: {}'.format(nwins_eyesc, nsecs_eyesc))
    print('\tN Extractable EyesO Wins: {} | N Extractable EyesO Secs: {}'.format(nwins_eyeso, nsecs_eyeso))
