# evt-data cleaning

This repository cleans up the EMSE-exported resting-state .evt files. Some of the files came in with incorrect coding -- for example, port codes marking clean segment start and end times sometimes occurred in the intertrial period. In another common case, codes that likely existed to mark the trial period were being interpreted as clean-segment markers, thus making the pipeline treat that entire trial as clean data.

# steps

Starting with the raw .evt files in `data/`, we perform the following steps:


# files that were manually modified
These files were manually modified after running the steps above.

### 120127148.evt
Contains only 7 full trials. This subject is missing the beginning marker for the first trial, an `O` trial.
