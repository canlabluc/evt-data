# evt-data cleaning

This repository cleans up the EMSE-exported resting-state .evt files. Some of the files came in with incorrect coding -- for example, port codes marking clean segment start and end times sometimes occurred in the intertrial period. In another common case, codes that likely existed to mark the trial period were being interpreted as clean-segment markers, thus making the pipeline treat that entire trial as clean data.

# steps

Starting with the raw .evt files in `data/raw/`, we perform the following steps:

Remove irrelevant xml tags from the raw data and save modified data to `data/clean/`.
```bash
$ python rm_irrelevant_xml.py
```

Transform data to a pandas dictionary, for easier modifying and readability.
```bash
$ python transform_data_to_df.py
```

Remove markers which exist to mark the trial period but were interpreted as clean-segment markers.
```bash
$ python rm_entire_trial_segs.py
```

Finally, remove clean segments which sit entirely in the intertrial period and trim segments which sit partially in the intertrial period.
```bash
$ python rm_intertrial_segs.py
```

# files that were manually modified

### data/raw/120127148.evt
Contains only 7 full trials. This subject is missing the beginning marker for the first trial, an `O` trial. It the beginning marker was added at timepoint 0.
