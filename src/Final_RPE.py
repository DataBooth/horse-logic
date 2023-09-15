import sys
import time
from datetime import datetime

import experiment_sounds as wav
from experiment_helper import (
    Servo_grain,
    Servo_pellets,
    elapsed_seconds,
    initialise_GPIO_buttons,
    listenForPause,
    log_event,
    pausable_sleep,
    play_WAV,
    setup_experiment,
)

#### Start of experiment ####

(
    subject_name,
    session_number,
    session_type,
    p,
    touchSensor,
    servo,
    data_dir,
    log_file,
    measurement_file,
) = setup_experiment()


# Session settings [these should be defined in the parameters workbook - provided a couple of examples below]
trialLimit = p["TRIAL_LIMIT"]  # all session types
criterionLimit = 3  # check for session type-may differ between session types
criterion_seconds = 20  # max duration in seconds for either a go or no-go response depending on session type
responseTimeout = p["RESPONSE_TIMEOUT"]  # used for RP-H only- maximum time to respond to a start tone
trialSleepTime = p["TRIAL_SLEEP_TIME"]

# Define mode of operation - test or live
mode = p["MODE"]

if mode == "test":
    trialLimit = 5
    criterion_seconds = 10
    trialSleepTime = 5  # sleep time period to allow feed consumption after a dispense
    responseTimeout = 10

# servo mode - change depending on which feed type is used
servo_mode = p["SERVO_MODE"]

# Create instances of Servo objects
feeder_grain = Servo_grain(servo)
feeder_pellets = Servo_pellets(servo)


# Initialise GPIO and create button instances
gpio, green_button, blue_button, red_button = initialise_GPIO_buttons()


# Initialize variables
trial_count = 0
touch_count = 0
last_touch_time = time.time()
is_touch_active = True
green_button_press_count = 0
blue_button_press_count = 0
last_green_press_time = time.time()  #MJB: currently unused
last_blue_press_time = time.time()

start_tone_played = False

if touchSensor is None:  # MJB testing mode
    sys.exit("Exiting test mode - not running on Raspberry Pi\n")

try:
    trial_number = 0

    while True:
        if green_button.is_pressed():
            log_event("Green button pressed", data_dir, log_file)
            green_button_press_count += 1
            if green_button_press_count == 1:
                # pause to avoid button double-press
                log_event(
                    f"System is ready for {subject_name} {session_number} Session type {session_type}",
                    data_dir,
                    log_file,
                )
                play_WAV(wav.systemIsReady, p["SYSTEM_READY_SOUND_DURATION"])

            elif green_button_press_count == 2:
                log_event("Green button pressed 2nd time", data_dir, log_file)
                # pause to avoid button double-press
                criterion_count = 0
                # print(f"Session started for {subject_name} {session_number} Session type {session_type} at: {datetime.now()}")
                log_event(
                    f"Session started for {subject_name} {session_number} Session type {session_type}",
                    data_dir,
                    log_file,
                )
                if session_type == "RP-A":
                    play_WAV(wav.acquisitionSessionStarted, p["SESSION_STARTED_SOUND_DURATION"])
                elif session_type == "RP-H":
                    play_WAV(wav.habitSessionStarted, p["SESSION_STARTED_SOUND_DURATION"])
                elif session_type == "RP-E":
                    play_WAV(wav.extinctionSessionStarted, p["SESSION_STARTED_SOUND_DURATION"])
                elif session_type == "RP-R":
                    play_WAV(wav.reinstatementSessionStarted, p["SESSION_STARTED_SOUND_DURATION"])
                else:
                    play_WAV(wav.sessionTerminated, p["SESSION_TERMINATED_SOUND_DURATION"])
                pausable_sleep(0.5, False)

                while trial_number < trialLimit:
                    if session_type == "RP-E":
                        if criterion_count == criterionLimit:
                            play_WAV(wav.criterionAchieved, 3)
                            # print(f"Criterion reached at: {datetime.now()}")
                            log_event("Criterion reached", data_dir, log_file)
                            sys.exit()

                    # begin next trial
                    trial_number += 1
                    # print(f"Current trial: {trial_number}")
                    log_event(f"Current trial: {trial_number}", data_dir, log_file)
                    play_WAV(wav.startTone, 1)
                    start_tone_played = True
                    start_tone_time = datetime.now()
                    # print(f"Start tone played at: {start_tone_time}")
                    log_event("Start tone played", data_dir, log_file)

                    # waiting for either a touch or the blue button
                    while True:
                        start_tone_time = start_tone_time + listenForPause(red_button, False, blue_button, touchSensor)

                        # elapsed = elapsed_seconds(start_tone_time)
                        # print(f"Session type {session_type} - elapsed {elapsed}")

                        # assess timeout
                        if session_type == "RP-H":
                            if elapsed_seconds(start_tone_time) > responseTimeout:
                                # print(f"Habit formation incorrect response at {datetime.now()}")
                                log_event("Habit formation incorrect response", data_dir, log_file)
                                play_WAV(wav.incorrectTone, 1)
                                start_tone_time = start_tone_time + pausable_sleep(1, False)
                                break
                        elif session_type == "RP-E":
                            if elapsed_seconds(start_tone_time) > criterion_seconds:
                                criterion_count += 1
                                # print(f"Criterion count {criterion_count}")
                                log_event(f"Criterion count {criterion_count}", data_dir, log_file)
                                break

                        if blue_button.is_pressed():
                            log_event("Blue button pressed", data_dir, log_file)
                            # manual override
                            if start_tone_played:
                                is_touch_active = False
                                last_touch_time = datetime.now()
                                touch_count += 1
                                # print(f"Manual touch recorded at: {last_touch_time}, Session under manual control")
                                log_event("Manual touch recorded - Session under manual control")

                                # assess goal
                                if session_type == "RP-A" or session_type == "RP-R":
                                    if elapsed_seconds(start_tone_time) < criterion_seconds:
                                        criterion_count += 1
                                        # print(f"Criterion count {criterion_count}")
                                        log_event(f"Criterion count {criterion_count}", data_dir, log_file)
                                    else:
                                        criterion_count = 0
                                        # print("Criterion restart")
                                        log_event("Criterion restart", data_dir, log_file)
                                elif session_type == "RP-E":
                                    criterion_count = 0
                                    # print("Criterion restart")
                                    log_event("Criterion restart", data_dir, log_file)
                                    start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, True)
                                    break

                                time.sleep(0.1)
                                play_WAV(wav.correctTone, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    log_event("Dispensing pellets", data_dir, log_file)
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    log_event("Dispensing grain", data_dir, log_file)
                                    feeder_grain.dispense_feed_grain()

                                if criterion_count == criterionLimit:
                                    play_WAV(wav.criterionAchieved, 3)
                                    # print(f"Criterion reached at: {datetime.now()}")
                                    log_event("Criterion reached", data_dir, log_file)
                                    sys.exit()

                                if touch_count == trialLimit:
                                    play_WAV(wav.sessionTerminated, 3.5)
                                    #print(f"Session ended at: {datetime.now()}")
                                    log_event("Session ended", data_dir, log_file)
                                    sys.exit()

                                start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, False)

                            # reset the tone for another touch
                            start_tone_played = False
                            break

                        # do this if the blue button has never been pressed
                        elif is_touch_active:
                            # touch-mode
                            status = touchSensor.read()
                            if status[1] > 0 or status[2] > 0 or status[3] > 0:
                                last_touch_time = datetime.now()
                                touch_count += 1
                                # print(f"Touch-pad status read at: {last_touch_time}")
                                log_event("Touch-pad status read", data_dir, log_file)
                                time.sleep(0.01)

                                if session_type == "RP-A" or session_type == "RP-R":
                                    if elapsed_seconds(start_tone_time) < criterion_seconds:
                                        criterion_count += 1
                                        # print(f"Criterion count {criterion_count}")
                                        log_event(f"Criterion count {criterion_count}", data_dir, log_file)
                                    else:
                                        criterion_count = 0
                                        # print("Criterion restart")
                                        log_event("Criterion restart", data_dir, log_file)
                                elif session_type == "RP-E":
                                    criterion_count = 0
                                    # print("Criterion restart")
                                    log_event("Criterion restart", data_dir, log_file)
                                    start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, True)
                                    break

                                play_WAV(wav.correctTone, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    log_event("Dispensing pellets", data_dir, log_file)
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    log_event("Dispensing grain", data_dir, log_file)
                                    feeder_grain.dispense_feed_grain()

                                if criterion_count == criterionLimit:
                                    play_WAV(wav.criterionAchieved, 3)
                                    # print(f"Criterion achieved at: {datetime.now()}")
                                    log_event("Criterion achieved", data_dir, log_file)
                                    sys.exit()

                                if touch_count == trialLimit:
                                    play_WAV(wav.sessionTerminated, 3.5)
                                    # print(f"Session ended at: {datetime.now()}")
                                    log_event("Session ended", data_dir, log_file)
                                    sys.exit()

                                start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, False)
                                break

                if trial_number == trialLimit:
                    log_event("Session terminated - trial limit reached", data_dir, log_file)
                    play_WAV(wav.sessionTerminated, 3.5)
                    sys.exit()

except KeyboardInterrupt:
    log_event("Keyboard interrupt - exiting...", data_dir, log_file)
    gpio.cleanup()
