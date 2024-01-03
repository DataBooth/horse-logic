# experiment.py
import sys
from datetime import datetime
from experiment_helper import DataManager, SoundManager, Button, Servo, TouchSensor

class Experiment:
    def __init__(self, config, data_manager, sound_manager, hardware):
        self.config = config
        self.data_manager = data_manager
        self.sound_manager = sound_manager
        self.hardware = hardware
        self.trial_number = 0
        self.session_active = False
        self.session_type = self.config['SESSION_TYPE']
        # ... other initializations ...

    def run(self):
        try:
            self._start_experiment()
            while self.trial_number < self.config['TRIAL_LIMIT']:
                self._run_trial()
                self.trial_number += 1
            self._end_experiment()
        except KeyboardInterrupt:
            self.data_manager.log_event("Keyboard interrupt - exiting...")
            self.hardware.cleanup()

    def _start_experiment(self):
        self.data_manager.log_event("Experiment started")
        self.session_active = True
        self.trial_number = 0
        # Play a sound to indicate the experiment is starting
        self.sound_manager.play_system_ready()
        # ... additional start experiment logic ...

    def _run_trial(self):
        self.data_manager.log_event(f"Trial {self.trial_number} started")
        # Play the start tone
        self.sound_manager.play_start_tone()
        start_time = datetime.now()

        # Wait for a response or timeout
        response = self._wait_for_response(start_time)

        if response:
            self._handle_response(start_time)
        else:
            self._handle_timeout()

        # ... additional trial logic ...

    def _end_experiment(self):
        self.session_active = False
        self.data_manager.log_event("Experiment ended")
        # Play a sound to indicate the experiment is ending
        self.sound_manager.play_session_terminated()
        # ... additional end experiment logic ...

    def _wait_for_response(self, start_time):
        # Logic to wait for touch sensor or button press
        # This is a placeholder for actual implementation
        # Return True if response is detected, False if timeout occurs
        return True

    def _handle_response(self, start_time):
        response_time = datetime.now()
        latency = (response_time - start_time).total_seconds()
        self.data_manager.log_event(f"Response received in {latency} seconds")
        self.sound_manager.play_correct_tone()
        # Dispense feed if appropriate for session type
        if self.session_type in ['RP-A', 'RP-R']:
            self.hardware['servo'].dispense_feed()
        # ... additional response handling logic ...

    def _handle_timeout(self):
        self.data_manager.log_event("Response timeout")
        if self.session_type == 'RP-H':
            self.sound_manager.play_incorrect_tone()
        # ... additional timeout handling logic ...
