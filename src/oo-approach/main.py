# main.py
from experiment import Experiment
from experiment_helper import DataManager, SoundManager, Button, Servo, TouchSensor

def main():
    config = load_config()  # Load or define your configuration
    data_manager = DataManager(config['DATA_DIR'])
    sound_manager = SoundManager()
    hardware = {
        'buttons': {
            'green': Button(config['GREEN_BUTTON_PIN']),
            'blue': Button(config['BLUE_BUTTON_PIN']),
            'red': Button(config['RED_BUTTON_PIN'])
        },
        'servo': Servo(config['SERVO_CHANNEL']),
        'touch_sensor': TouchSensor(config['SENSITIVITY'])
    }

    experiment = Experiment(config, data_manager, sound_manager, hardware)
    experiment.run()

if __name__ == "__main__":
    main()
