# Background information on the experimental design

# Each session (trial?) will be about 10 minutes per horse, 20 horses, x 1 session a day, x probably 7 days total.
# So 20 horses x 10 minutes x 7 days = 1400 minutes = 23.3 hours of data.

# We will want to collect correct responses and the latency between the correct responses.
# Am thinking we will need a "go" signal-probably a noise, then measure the time between that and a correct response.
# Then a set period of time out, then go signal again and commencement of trial.
# So recording the latency between go signal and beginning of time out period, or between go signals.

# Will you also want to record the time between the go signal and the correct response?

# I expect it will be that once the touch sensor is triggered, that will start a time out period where
# no further presses would be registered.
# Then after the time period has elapsed, the next touch would be registered and so on

# There  will be 20 subjects.  All subjects will do the same training.
# We are not sure yet whether we go with a fixed number of trials or trials to criteria.

# Questions:
# 1. How many trials per session? (confirm 1 i.e. session == trial) - may need to change this
# 2. How many sessions per day? (confirm 1)
# 3. How many days do the trials run for? (confirm 7)
# 4. How many subjects? (confirm 20)
# 5. How many sensors? (confirm 1 - touch sensor)
# 6. How many trials per subject? (confirm one per day * # days)
# 7. How many trials in total? (confirm 20 * 7)
# 8. How many observations per trial? (confirm 0 or 1 within the maximum allowed time of 10 minutes)
# 9. Each observation is a touch sensor event (confirm)?
# 10. What is the maximum time allowed for a trial? (confirm 10 minutes)
# 11. So an observation/measurement is either "null" or a time in seconds (i.e. the latency - correct definition)?
# 12. Do you want to record other details of the experiment e.g. temperature, humidity, etc.? time dependent?
# 13. What constitutes a "correct" response? (confirm touch sensor event)
# 14. What constitutes an "missed" response? (confirm no touch sensor event within the maximum allowed time of 10 minutes)
# 15. There will be a noise to signal the start of the trial.  Will this be initiated by the computer or the experimenter?
# 16. Looks like the experiment will "reset" after the time out period and then re-run for the same subject?


from dataclasses import dataclass
from pprint import pprint

MAX_N_OBSERVATION = 30
MAX_TIME_TRIAL_SECONDS = 2 * 60.0


@dataclass
class Subject:
    name: str
    description: str
    id: int
    age: float
    breed: str
    type: str = "horse"

    def __str__(self):
        return f"{self.name} (Id: {self.id})"

    def __repr__(self):
        return f"{self.name} (Id: {self.id})"




@dataclass
class Sensor:
    name: str
    description: str
    status: bool
    serial_number: str
    hardware_daq_info: str  # details about the hardware DAQ e.g. Raspberry Pi

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    def __repr__(self):
        return f"{self.name} ({self.serial_number})"


@dataclass
class DaqHardware:
    name: str
    description: str
    serial_number: str
    sensors: list  # list of sensors connected to the DAQ hardware

    def __str__(self):
        return f"{self.name} ({self.serial_number}) \nSensors:\n{self.sensors}"

    def __repr__(self):
        return f"{self.name} ({self.serial_number}) \nSensors:\n{self.sensors}"


# Experiment is the top level class consisting of a number of trials

@dataclass
class Experiment:
    name: str
    description: str
    n_trial: int
    start_date: str
    end_date: str
    status: str
    # uuid: str (just internally generated - not needed for now)
    daq_hardware: DaqHardware
    data_file_prefix: str
    # max_time_experiment_seconds: float = MAX_TIME_EXPERIMENT_SECONDS (to - probably MAX_TIME_TRIAL_SECONDS)
    max_n_observation: int = MAX_N_OBSERVATION

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"


@dataclass
class Trial:
    name: str
    description: str
    start_datetime: str
    end_datetime: str
    experiment: Experiment
    run_id: str
    subject: Subject
    max_time_trial_seconds: float = MAX_TIME_TRIAL_SECONDS
    max_n_observation: int = MAX_N_OBSERVATION

    def __str__(self):
        return f"{self.name} : Subject {self.subject})"

    def __repr__(self):
        return f"{self.name} : Subject {self.subject})"
