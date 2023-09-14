from datetime import datetime as dt
from pathlib import Path
import pandas as pd
from dataclasses import dataclass


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
    event_name,
    data_dir,
    log_file,
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


def log_trial_parameters(parameters, data_dir, log_file):
    params = {key: eval(key) for key in parameters}
    with open(Path(data_dir) / log_file, "a") as f:
        f.write(f"PARAMETERS: {params}\n")
    print(f"Logged - PARAMETERS: {params}\n")
    return None


def set_subject_number(N_TRIAL, data_dir):
    subject_name = 0
    print("\nStarting experiment:")
    print("\n  Press Ctrl-C to exit the experiment\n")
    print("  Ensure the subject is settled in the stall:")
    print(
        f"   - Commencing the experiment with {N_TRIAL} trials..."
    )  # May be to adjust for various types of experiments

    while subject_name == 0:
        try:
            subject_name = input("\nEnter subject name: ")
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
        lambda name: name.lower().replace(" ", "")
    )
    subject_names = [name.lower() for name in experiment_tracking_df["subject_name"].values.tolist()]
    # Amend to allow for subject names with spaces
    subject_names = [name.replace(" ", "") for name in subject_names]
    if subject_name.lower().replace(" ", "") not in subject_names:
        print(f"Subject {subject_name} not found in tracking file.\nSee {(Path(data_dir) / tracking_file).as_posix()}.")
        return 0, 0
    next_session_number = (
        experiment_tracking_df["subject_name_clean"]
        .str.contains(subject_name.lower().replace(" ", ""), case=False)
        .values[0]
        + 1
    )
    experiment_tracking_df.loc[
        experiment_tracking_df["subject_name_clean"].str.contains(subject_name.lower().replace(" ", ""), case=False),
        "last_session_number",
    ] = next_session_number
    # Update the tracking file with the next session number for the given subject (subject_name)
    experiment_tracking_df.to_excel(Path(data_dir) / tracking_file, index=False)
    return subject_name, next_session_number


def choose_experiment_type():
    # Allow the user to choose the experiment type by entering the number corresponding to the experiment type
    experiment_types = ["RPE-A", "RPE-B", "Experiment 3"]
    experiment_number = 0
    print("\nChoose experiment type:")
    for i, experiment_type in enumerate(experiment_types):
        print(f"{i+1} - {experiment_type}")
    while experiment_number < 1 or experiment_number > len(experiment_types):
        try:
            experiment_number = int(input("\nEnter experiment type: "))
        except ValueError:
            experiment_number = 0
    experiment_type = experiment_types[experiment_number - 1]
    return experiment_type


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


@dataclass
class Parameter:
    name: str
    val: float
    unit: str
    minimum_value: float
    maximum_value: float
    description: str


def parse_text_for_na(value):
    if pd.isna(value):
        return ""
    else:
        return value


def get_parameter(name, experimental_parameters_df):
    row = experimental_parameters_df.loc[experimental_parameters_df["name"] == name]
    if row.drop(columns=["name"]).isnull().values.all():
        return None
    return Parameter(
        name=name,
        val=row["value"].values[0],
        minimum_value=row["minimum_value"].values[0],
        maximum_value=row["maximum_value"].values[0],
        unit=parse_text_for_na(row["unit"].values[0]),
        description=parse_text_for_na(row["description"].values[0]),
    )


def load_validate_experimental_parameters(data_dir, parameters_xlsx="experimental_parameters.xlsx"):
    if not Path(data_dir / parameters_xlsx).exists():
        raise FileNotFoundError(f"{parameters_xlsx} does not exist")
    experimental_parameters_df = pd.read_excel(Path(data_dir / parameters_xlsx))
    par = {}
    for name in experimental_parameters_df["name"]:
        parameter = get_parameter(name, experimental_parameters_df)
        if parameter is not None:
            if parameter.val < parameter.minimum_value or parameter.val > parameter.maximum_value:
                print(f"{parameter.name} is out of range: {parameter.val} {parameter.unit}")
            print(f"{parameter.name}: {parameter.val} {parameter.unit} - Validated")
            par[name] = parameter.val
    return par
