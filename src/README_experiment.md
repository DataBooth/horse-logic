## Setup and running of experiment code

The code is designed to be run on a Raspberry Pi using Python.
The code should be run from the command line using the following command:

```bash
python main.py [TODO: Fix name]
```

The code should be run for each subject (horse) for each session number of specified session type (RP-A (acquisition), RP-E (extinction), TODO add others).


### Code files

The two code files are:
- main.py (TODO: put in actual name)
- experiment_helper.py

The `experiment_helper.py` file contains the helper functions for the experiment code to hide the details of the experiment code from the main code.

### Data files

- experiment_subjects.xlsx
- experiment_parameters.xlsx

The first workbook is used to specify the names of the subjects (horses) in the experiments
It assumes that the horses have unique names and that the names are in the first column of the first sheet of the workbook. The workbook also tracks the number of the last session for each
subject (horse). The subject name and session number are included in the name of the data and log file for each session.


### Log files and data files

Naming convention for log files and data files is:

`Experiment_{SESSION_START_TIMESTAMP}_{SUBJECT_NAME}_{SESSION_NUMBER}_{SESSION_TYPE}`

with a `.log` (log file) or `.dat` (measurement file) extension.
