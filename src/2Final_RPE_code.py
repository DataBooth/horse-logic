from datetime import datetime, timedelta
import sys
import time

import pygame

from experiment_helper import (
    choose_session_type,
    initialise_sensors,
    initialise_directories,
    load_validate_experimental_parameters,
    set_subject_number,
    confirm_experiment_details,
    initialise_experiment,
    log_event,
    log_trial_parameters,
    initialise_GPIO,
    Servo_grain,
    Servo_pellets,
    Button,
    play_WAV,
    pausable_sleep,
    elapsed_seconds,
    listenForPause,
)

# NOTE new=Wav file paths- delete old paths

systemIsReadyWav = "/home/horselogic/Documents/test audio project_data/System_is_ready1.wav"
sessionStartedWav = "/home/horselogic/Documents/test audio project_data/Session_started1.wav"
trialPausedWav = "/home/horselogic/Documents/test audio project_data/Trial paused1.wav"
trialRestartedWav = "/home/horselogic/Documents/test audio project_data/Trial restarted1.wav"
sessionTerminated = "/home/horselogic/Documents/test audio project_data/End tone_1200_sess_completed.wav"
startToneWav = "/home/horselogic/Documents/test audio project_data/Start tone _600.wav"
correctToneWav = "/home/horselogic/Documents/test audio project_data/Correct tone_1000.wav"
incorrectToneWav = "/home/horselogic/Documents/test audio project_data/IncorrectTone.wav"
endToneWav = "/home/horselogic/Documents/test audio project_data/End tone_1200.wav"
criterionAchievedWav = "//home/horselogic/Code/2Final_RPE_code_DRAFT.pyhome/horselogic/Documents/test audio project_data/Criterion_reached.wav"
criterionNotReachedWav = "/home/horselogic/Documents/test audio project_data/Criterion_ not_reached.wav"
acquisitionSessionStartedWav = "/home/horselogic/Documents/test audio project_data/Acquistion_Session_Started.wav"
habitSessionStartedWav = "/home/horselogic/Documents/test audio project_data/Habit_session_started.wav"
extinctionSessionStartedWav = "/home/horselogic/Documents/test audio project_data/Extinction_session_started.wav"
reinstatementSessionStartedWav = "/home/horselogic/Documents/test audio project_data/Reinstatement_session_started.wav"


# RP-A= acquisition of response
# trialLimit = 20 per session, multiple sessions until acquisition criterion
# unlimited time between start tone and touch (or button)
# criterion = n touches in a row that occur under 20 sec from start tone
# no responseTimeout
# RP-H= habit formation
# trialLimit 20 fixed trials per session, 3 sesions
# reponseTimeout 45s
# RP-E= extinction of response
# trialLimit  = 20, multiple session until extinction criterion
# number of responses in a row
# criterion_seconds = 20s
# RP-R= reinstatement of response
# trialLimit = 20 per session, multiple sessions unil acquisition criterion
# no responseTimeout

# At beginning of each session for each horse- check and change session type to one of:
# RP-A = acquisition,
# RP-H = habit formation,
# RP-E= extinction,
# RP-R = reinstatement


# Session settings
trialLimit = 20  # all session types
criterionLimit = 3  # check for session type-may differ between session types
criterion_seconds = 20  # max duration in seconds for either a go or no-go response depending on session type
responseTimeout = 45  # used for RP-H only- maximum time to respond to a start tone

# Define mode of operation - test or live
trialSleepTime = 5
mode = "test"
if mode == "test":
    trialLimit = 5
    criterion_seconds = 10
    trialSleepTime = 5  # sleep time period to allow feed consumption after a dispense
    responseTimeout = 10


#### Start of experiment ####

pygame.mixer.init()  # Initialise the mixer module for playing WAV files

session_type = choose_session_type()
data_dir, tone_dir = initialise_directories()
p = load_validate_experimental_parameters(data_dir)

touchSensor, servo = initialise_sensors(p["SENSITIVITY"], p["SERVO_CHANNEL"])
subject_name, session_number = set_subject_number(p["N_TRIAL"], data_dir)

if not confirm_experiment_details(subject_name, session_number, session_type, p["N_TRIAL"]):
    sys.exit()
log_file, measurement_file, initial_delay = initialise_experiment(subject_name, p["INITIAL_DELAY"], session_type)
log_event(f"Subject {subject_name} - Session {session_number} started...", data_dir, log_file)
log_trial_parameters(p, data_dir, log_file)

# servo mode - change depending on which feed type is used
servo_mode = p["SERVO_MODE"]

# Create instances of Servo objects
feeder_grain = Servo_grain(servo)
feeder_pellets = Servo_pellets(servo)


# Initialise GPIO and create button instances
gpio, butpin_green, butpin_blue, butpin_red = initialise_GPIO()
green_button = Button(butpin_green)
blue_button = Button(butpin_blue)
red_button = Button(butpin_red)

# Initialize variables
trial_count = 0
touch_count = 0
last_touch_time = time.time()
is_touch_active = True
green_button_press_count = 0
blue_button_press_count = 0
last_green_press_time = time.time()
last_blue_press_time = time.time()

start_tone_played = False

try:
    trial_number = 0

    while True:
        if green_button.is_pressed():
            green_button_press_count += 1
            if green_button_press_count == 1:
                # pause to avoid button double-press
                print(
                    f"System is ready for {subject_name} {session_number} Session type {session_type} at: {datetime.now()}"
                )
                play_WAV(systemIsReadyWav, p["SYSTEM_READY_SOUND_DURATION"])

            elif green_button_press_count == 2:
                # pause to avoid button double-press
                criterion_count = 0
                print(
                    f"Session started for {subject_name} {session_number} Session type {session_type} at: {datetime.now()}"
                )
                if session_type == "RP-A":
                    play_WAV(acquisitionSessionStartedWav, p["SESSION_STARTED_SOUND_DURATION"])
                elif session_type == "RP-H":
                    play_WAV(habitSessionStartedWav, 1)
                elif session_type == "RP-E":
                    play_WAV(extinctionSessionStartedWav, 1)
                elif session_type == "RP-R":
                    play_WAV(reinstatementSessionStartedWav, 1)
                else:
                    play_WAV(sessionTerminated, 1)
                pausable_sleep(0.5, False)

                while trial_number < trialLimit:
                    if session_type == "RP-E":
                        if criterion_count == criterionLimit:
                            play_WAV(criterionAchievedWav, 3)
                            print(f"Criterion reached at: {datetime.now()}")
                            sys.exit()

                    # begin next trial
                    trial_number += 1
                    print(f"Current trial: {trial_number}")
                    play_WAV(startToneWav, 1)
                    start_tone_played = True
                    start_tone_time = datetime.now()
                    print(f"Start tone played at: {start_tone_time}")

                    # waiting for either a touch or the blue button
                    while True:
                        start_tone_time = start_tone_time + listenForPause(
                            red_button, False, blue_button, touchSensor, trialPausedWav, trialRestartedWav
                        )

                        # elapsed = elapsed_seconds(start_tone_time)
                        # print(f"Session type {session_type} - elapsed {elapsed}")

                        # assess timeout
                        if session_type == "RP-H":
                            if elapsed_seconds(start_tone_time) > responseTimeout:
                                print(f"Habit formation incorrect response at {datetime.now()}")
                                play_WAV(incorrectToneWav, 1)
                                start_tone_time = start_tone_time + pausable_sleep(1, False)
                                break
                        elif session_type == "RP-E":
                            if elapsed_seconds(start_tone_time) > criterion_seconds:
                                criterion_count += 1
                                print(f"Criterion count {criterion_count}")
                                break

                        if blue_button.is_pressed():
                            # manual override
                            if start_tone_played:
                                is_touch_active = False
                                last_touch_time = datetime.now()
                                touch_count += 1
                                print(f"Manual touch recorded at: {last_touch_time}, Session under manual control")

                                # assess goal
                                if session_type == "RP-A" or session_type == "RP-R":
                                    if elapsed_seconds(start_tone_time) < criterion_seconds:
                                        criterion_count += 1
                                        print(f"Criterion count {criterion_count}")
                                    else:
                                        criterion_count = 0
                                        print("Criterion restart")
                                elif session_type == "RP-E":
                                    criterion_count = 0
                                    print("Criterion restart")
                                    start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, True)
                                    break

                                time.sleep(0.1)
                                play_WAV(correctToneWav, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    feeder_grain.dispense_feed_grain()

                                if criterion_count == criterionLimit:
                                    play_WAV(criterionAchievedWav, 3)
                                    print(f"Criterion reached at: {datetime.now()}")
                                    sys.exit()

                                if touch_count == trialLimit:
                                    play_WAV(sessionTerminated, 3.5)
                                    print(f"Session ended at: {datetime.now()}")
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
                                print(f"Touch-pad status read at: {last_touch_time}")
                                time.sleep(0.01)

                                if session_type == "RP-A" or session_type == "RP-R":
                                    if elapsed_seconds(start_tone_time) < criterion_seconds:
                                        criterion_count += 1
                                        print(f"Criterion count {criterion_count}")
                                    else:
                                        criterion_count = 0
                                        print("Criterion restart")
                                elif session_type == "RP-E":
                                    criterion_count = 0
                                    print("Criterion restart")
                                    start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, True)
                                    break

                                play_WAV(correctToneWav, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    feeder_grain.dispense_feed_grain()

                                if criterion_count == criterionLimit:
                                    play_WAV(criterionAchievedWav, 3)
                                    print(f"Criterion achieved at: {datetime.now()}")
                                    sys.exit()

                                if touch_count == trialLimit:
                                    play_WAV(sessionTerminated, 3.5)
                                    print(f"Session ended at: {datetime.now()}")
                                    sys.exit()

                                start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, False)
                                break

                if trial_number == trialLimit:
                    play_WAV(sessionTerminated, 3.5)
                    sys.exit()

except KeyboardInterrupt:
    log_event("Keyboard interrupt - exiting...", data_dir, log_file)
    gpio.cleanup()
