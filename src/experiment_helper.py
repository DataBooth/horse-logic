from datetime import datetime as dt
from pathlib import Path
import pandas as pd


def set_directory(dir_name):
    """
    Check if a directory with the given name exists.

    Args:
        dir_name (str or Path): The name or path of the directory to be checked.

    Raises:
        TypeError: If dir_name is not a string or a Path object.
        FileNotFoundError: If the directory doesn't exist.

    Example:
        set_directory('my_directory')
        In this example, the function is called with the directory name 'my_directory'.
        If the directory doesn't exist, a FileNotFoundError exception will be raised.
    """
    if not isinstance(dir_name, (str, Path)):
        raise TypeError("dir_name must be a string or a Path object.")
    if not Path(dir_name).exists():
        raise FileNotFoundError(f"The specified directory {dir_name} does not exist.")
    return Path(dir_name)


def create_output_filenames(subject_name, session_number, experiment_type):
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
    file_name = f"{LOGFILE_PREFIX}_{dt.now().isoformat()}_{subject_name}_{session_number}_{experiment_type}"
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


def set_subject_number(N_SUBJECT, N_TRIAL, data_dir):
    """
    Sets the subject number for the experiment and calculates the next session number for the given subject.

    Args:
        N_SUBJECT (int): The total number of subjects.
        N_TRIAL (int): The number of trials.
        data_dir (str): The path to the data directory.

    Returns:
        subject_number (int): The subject number for the experiment.
        session_number (int): The next session number for the given subject.
    """
    subject_name = 0
    print("\nStarting experiment:")
    print("\n  Press Ctrl-C to exit the experiment\n")
    print("  Ensure the subject is settled in the stall:")
    print(f"   - Commencing the experiment with {N_TRIAL} trials...")

    while subject_name == 0:
        try:
            subject_name = input(f"\nEnter subject name: ")
        except ValueError:
            subject_name = 0
        subject_name, next_session_number = get_next_session_number(subject_name, data_dir)
    return subject_name, next_session_number


def get_next_session_number(subject_name, data_dir, tracking_file="experiment_tracking.xlsx"):
    if not (Path(data_dir) / tracking_file).exists():
        raise FileNotFoundError(f"Tracking file {Path(data_dir) / tracking_file} does not exist.")
    # Read in the tracking file
    experiment_tracking_df = pd.read_excel(Path(data_dir) / tracking_file)
    experiment_tracking_df["subject_name_clean"] = experiment_tracking_df["subject_name"].apply(
        lambda x: x.lower().replace(" ", "")
    )
    subject_names = [name.lower() for name in experiment_tracking_df["subject_name"].values.tolist()]
    # Amend to allow for subject names with spaces
    subject_names = [name.replace(" ", "") for name in subject_names]
    if subject_name.replace(" ", "") not in subject_names:
        print(f"Subject {subject_name} not found in tracking file.")
        return 0, 0
    next_session_number = (
        experiment_tracking_df["subject_name_clean"]
        .str.contains(subject_name.lower().replace(" ", ""), case=False)
        .values[0]
        + 1
    )
    # TODO: experiment_tracking_df.loc[experiment_tracking_df["subject_name"] == subject_name, "last_session"] = next_session_number
    # Update the tracking file with the next session number for the given subject (subject_name)
    experiment_tracking_df.to_excel(Path(data_dir) / tracking_file, index=False)
    return subject_name, next_session_number


def confirm_experiment_details(subject_name, session_number, experiment_type, N_TRIAL):
    """
    Confirms the experiment details with the user.

    Args:
        subject_name (str): The name of the subject.
        session_number (int): The session number.
        experiment_type (str): The type of experiment.
        N_TRIAL (int): The number of trials.

    Returns:
        True if the user confirms the experiment details are correct, False otherwise.
    """
    print(f"\nSubject name: {subject_name}")
    print(f"Session number: {session_number}")
    print(f"Experiment type: {experiment_type}")
    print(f"Number of trials: {N_TRIAL}")
    confirm = input("\Are experiment details ok (y - continue / n - exit): ")
    if confirm.lower()[0] != "y":
        return False
    else:
        return True
