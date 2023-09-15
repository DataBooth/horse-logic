## Setup and running of experiment code

The code is designed to be run on a Raspberry Pi using Python.
The code should be run from the command line using the following command:

```bash
python Final_RPE.py
```

The code should be run for each subject (horse) for each session number of specified session type:
- RP-A: acquisition,
- RP-H: habit formation,
- RP-E: extinction,
- RP-R: reinstatement.

### Python code

The two code files are:
- `Final_RPE.py`
- `experiment_helper.py`
- `experiment_sounds.py`

The `experiment_helper.py` file contains the helper functions for the experiment code to hide the details of the
experiment code from the main code. `experiment_sounds.py` contains the paths for each of the sounds for the experiment.

### Data files

- `data/experiment_subjects.xlsx`
- `data/experiment_parameters.xlsx`

The first workbook is used to specify the names of the subjects (horses) in the experiments
It assumes that the horses have unique names (and no sub-string matches - this can be tweaked if needed) and that the names
are in the first column of the first sheet of the workbook. The workbook also tracks the number of the last session for each
subject (horse). The subject name and session number are included in the name of the data and log file for each session.

### Session types

#### RP-A - acquisition of response

- trialLimit = 20 per session, multiple sessions until acquisition criterion
- unlimited time between start tone and touch (or button)
- criterion = n touches in a row that occur under 20 sec from start tone
- no responseTimeout

#### RP-H - habit formation

- trialLimit = 20 fixed trials per session, 3 sessions
- responseTimeout 45s

#### RP-E - extinction of response

- trialLimit = 20, multiple session until extinction criterion
- number of responses in a row
- criterion_seconds = 20s

#### RP-R - reinstatement of response

- trialLimit = 20 per session, multiple sessions until acquisition criterion
- no responseTimeout

### Log files and data files

Naming convention for log files and data files is:

 `Experiment_{SESSION_START_TIMESTAMP}_{SUBJECT_NAME}_{SESSION_NUMBER}_{SESSION_TYPE}`

with a `.log` (log file) or `.dat` (measurement file) extension. The measurement file is a work in progress to work out
if it is convenient to have a separate file for the measurements or to include them in the log file.
