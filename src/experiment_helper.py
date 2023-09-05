from datetime import datetime as dt
from functools import cache
import numpy as np
import simpleaudio as sa
from pathlib import Path
import os


# Define key hardware parameters
TOUCH_SENSITIVITY_LEVEL = 6
SERVO_PIN = 18  # GPIO pin for the servo
SERVO_MIN = 500  # Minimum pulse width for the servo
SERVO_MAX = 2500  # Maximum pulse width for the servo


MAX_N_OBSERVATION = 30
MAX_TIME_TRIAL_SECONDS = 2 * 60.0


def set_data_dir():
    DATA_DIR = Path.cwd() / "data"
    if not DATA_DIR.exists():
        DATA_DIR.mkdir()
    return DATA_DIR


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
        event_time = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(Path(data_dir) / log_file, "a") as f:
        f.write(f"{event_time}: {event_name}\n")
    if echo_to_console:
        print(f"Logged - {event_time}: {event_name}\n")
    if log_as_measurement:
        log_measurement(data_dir, measurement_file, event_name, event_time)
    return None


def play_correct_response_tone():
    """Play the correct response tone."""
    log_event("Start playing correct response tone", dt.now())
    play_beep(duration=1)
    log_event("Finished playing correct response tone", dt.now())
    return None


def dispense_feed():
    """Dispense feed."""
    log_event("Dispensing feed", dt.now())
    # code to dispense feed
    return None


def wait_for_period_of_time(event_name, duration_sec):
    """Wait for the specified duration in seconds."""
    log_event(f"{event_name}: Waiting for {duration_sec} seconds", dt.now())
    sleep(duration_sec)
    log_event(f"{event_name}: Finished waiting for {duration_sec} seconds", dt.now())
    return None


def wait_for_start_button_press():
    while True:
        if input("Press [ENTER] to start the trial") == "":
            log_event("Trial ready to start", dt.now())
            break
    return None


def log_trial_parameters(trial_parameters_names, log_file):
    trial_parameters = {key: eval(key) for key in trial_parameters_names}

    """Log the trial parameters to a file."""
    with open(log_file, "a") as f:
        f.write(f"TRIAL PARAMETERS: {trial_parameters}\n")
    print(f"Logged - TRIAL PARAMETERS: {trial_parameters}\n")
    return None
