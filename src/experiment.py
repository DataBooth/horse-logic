from dataclasses import dataclass

MAX_N_OBSERVATION = 30
MAX_TIME_EXPERIMENT_SECONDS = 2 * 60.0


@dataclass
class Experiment:
    name: str
    description: str
    n_run: int
    start_date: str
    end_date: str
    status: str
    uuid: str
    sensors: list
    data_file_suffix: str
    max_time_experiment_seconds: float = MAX_TIME_EXPERIMENT_SECONDS
    max_n_observation: int = MAX_N_OBSERVATION

    def __str__(self):
        return f"{self.name} ({self.uuid})"

    def __repr__(self):
        return f"{self.name} ({self.uuid})"


MAX_SENSOR_VALUE = 100.0
MAX_TIME_DIFF_SECONDS = 10.0


@dataclass
class Sensor:
    name: str
    description: str
    status: bool
    serial_number: str
    hardware_daq_info: str  # details about the hardware DAQ e.g. Raspberry Pi
    max_sensor_value: float = MAX_SENSOR_VALUE
    max_time_diff_seconds: float = MAX_TIME_DIFF_SECONDS

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    def __repr__(self):
        return f"{self.name} ({self.serial_number})"
