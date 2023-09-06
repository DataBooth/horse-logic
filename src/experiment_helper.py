from datetime import datetime as dt
from pathlib import Path


# Define key hardware parameters
TOUCH_SENSITIVITY_LEVEL = 6
SERVO_PIN = 18  # GPIO pin for the servo
SERVO_MIN = 500  # Minimum pulse width for the servo
SERVO_MAX = 2500  # Maximum pulse width for the servo


MAX_N_OBSERVATION = 30
MAX_TIME_TRIAL_SECONDS = 2 * 60.0


def set_data_dir():
    DATA_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/data"  # CH: Hard-coded
    if not Path(DATA_DIR).exists():
        Path(DATA_DIR).mkdir()
    return Path(DATA_DIR)


def create_output_filenames(subject_number):
    LOGFILE_PREFIX = "Experiment"
    file_name = f"{LOGFILE_PREFIX}_{dt.now().isoformat()}_Subject_{subject_number}"
    return f"{file_name}.log", f"{file_name}.dat"


def log_event(
    data_dir,
    log_file,
    event_name,
    log_as_measurement=False,
    event_time=None,
    echo_to_console=True,
):
    """Log the event name and time to a file."""
    if event_time is None:
        event_time = dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open(Path(data_dir) / log_file, "a") as f:
        f.write(f"{event_time}: {event_name}\n")
    if echo_to_console:
        print(f"Logged - {event_time}: {event_name}\n")
    if log_as_measurement:
        measurement_file = log_file.replace(".log", ".dat")
        with open(Path(data_dir) / measurement_file, "a") as f:
            f.write(f"{event_time}: {event_name}\n")
    return None




def log_trial_parameters(trial_parameters_names, log_file):
    trial_parameters = {key: eval(key) for key in trial_parameters_names}

    """Log the trial parameters to a file."""
    with open(log_file, "a") as f:
        f.write(f"TRIAL PARAMETERS: {trial_parameters}\n")
    print(f"Logged - TRIAL PARAMETERS: {trial_parameters}\n")
    return None
