from experiment import Experiment
from experiment_helper import load_config, DataManager, SoundManager, Button, Servo, TouchSensor
from config import parse_args, load_config


def main():
    args = parse_args()
    config = load_config(command_line_args=args)
    TESTING_MODE = config.get("TESTING_MODE", True)
    data_manager = DataManager(config["DATA_DIR"])
    sound_manager = SoundManager()
    hardware = {
        "buttons": {
            "green": Button(config["GREEN_BUTTON_PIN"]),
            "blue": Button(config["BLUE_BUTTON_PIN"]),
            "red": Button(config["RED_BUTTON_PIN"]),
        },
        "servo": Servo(config["SERVO_CHANNEL"]),
        "touch_sensor": TouchSensor(config["SENSITIVITY"]),
    }

    experiment = Experiment(config, data_manager, sound_manager, hardware)
    experiment.run()


if __name__ == "__main__":
    main()
