from datetime import datetime as dt
from pathlib import Path


MAX_N_OBSERVATION = 30
MAX_TIME_TRIAL_SECONDS = 2 * 60.0


def set_data_dir():
    """
    Sets the path for the data directory.

    If the directory doesn't exist, it creates the directory and returns the path.

    Returns:
        Path: The `Path` object representing the data directory.
    """
    DATA_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/data"  # CH: Hard-coded
    if not Path(DATA_DIR).exists():
        Path(DATA_DIR).mkdir()
    return Path(DATA_DIR)


def create_output_filenames(subject_number):
    """
    Generate output filenames for an experiment log file and a data file.

    Args:
        subject_number (int): The number of the subject for which the filenames are being created.

    Returns:
        tuple: A tuple containing the log filename and the data filename, both based on the current date and time, and the subject number.

    Example:
        filenames = create_output_filenames(10)
        print(filenames)
        # Output: ('Experiment_2022-01-01T12:00:00_Subject_10.log', 'Experiment_2022-01-01T12:00:00_Subject_10.dat')
    """
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
    """
    Log the event name and time to a file.

    Args:
        data_dir (str): The directory where the log/measurement file(s) will be stored.
        log_file (str): The name of the log file. The measurement file will have the same name, but with a .dat extension.
        event_name (str): The name/text of the event to be logged.
        log_as_measurement (bool, optional): If True, the event will also be logged as a measurement in a separate file. Default is False.
        event_time (str, optional): The timestamp of the event. If not provided, the current timestamp will be used.
        echo_to_console (bool, optional): If True, the log will be echoed to the console. Default is True.

    Returns:
        None

    Example:
        log_event("data", "log.txt", "Event 1")
        This example logs "Event 1" with the current timestamp to the file "log.txt" in the "data" directory.
    """

    if not Path(data_dir).exists():
        raise FileNotFoundError(f"Data directory {data_dir} does not exist.")
    if event_time is None:
        event_time = dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open(Path(data_dir) / log_file, "a") as flog:
        flog.write(f"{event_time}: {event_name}\n")
    if echo_to_console:
        print(f"Logged - {event_time}: {event_name}\n")
    if log_as_measurement:
        measurement_file = log_file.replace(".log", ".dat")
        with open(Path(data_dir) / measurement_file, "a") as f:
            f.write(f"{event_time}: {event_name}\n")
    return None


def log_trial_parameters(trial_parameters_names, log_file):
    """
    Log the trial parameters to a file and print them to the console.

    Args:
        trial_parameters_names (list): A list of strings representing the names of the trial parameters.
        log_file (str): The path to the log file where the trial parameters will be logged.

    Returns:
        None

    Example Usage:
        trial_parameters_names = ['param1', 'param2']
        log_file = 'trial_log.txt'
        param1 = 10
        param2 = 'hello'
        log_trial_parameters(trial_parameters_names, log_file)

    This function logs the trial parameters to a file and prints them to the console.
    The trial parameters are obtained by creating a dictionary using a dictionary comprehension,
    where the keys are the elements in `trial_parameters_names` and the values are the values of the corresponding variables.
    The trial parameters are then written to the log file in append mode and printed to the console.
    """
    trial_parameters = {key: eval(key) for key in trial_parameters_names}

    with open(log_file, "a") as f:
        f.write(f"TRIAL PARAMETERS: {trial_parameters}\n")
    print(f"Logged - TRIAL PARAMETERS: {trial_parameters}\n")
    return None
