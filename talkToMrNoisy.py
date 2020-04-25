import json
import logging
import os
import os.path
import click
from snowboy import snowboydecoder

from assistant.grpc import device_helpers, conversation_assistant

interrupted = False
assistant = object


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


def ask_google_callback():
    global assistant
    once = True

    # # Setup configuration
    # credentials = os.path.join(click.get_app_dir('google-oauthlib-tool'), 'credentials.json')
    # device_config = os.path.join(click.get_app_dir('mr-noisy'), 'device_config.json')
    # once = True
    #
    # with open(device_config) as f:
    #     device = json.load(f)
    #     device_id = device['id']
    #     device_model_id = device['model_id']
    #     logging.info("Using device model %s and device id %s",
    #                  device_model_id,
    #                  device_id)
    #
    # device_handler = device_helpers.DeviceRequestHandler(device_id)
    #
    # with conversation_assistant.GoogleAssistant(device_model_id, device_id, device_handler, credentials) as assistant:

    # If no file arguments supplied:
    # keep recording voice requests using the microphone
    # and playing back assistant response using the speaker.
    # When the once flag is set, don't wait for a trigger. Otherwise, wait.
    wait_for_user_trigger = not once
    while True:
        if wait_for_user_trigger:
            click.pause(info='Press Enter to send a new request...')
        continue_conversation = assistant.assist()
        # wait for user trigger if there is no follow-up turn in
        # the conversation.
        wait_for_user_trigger = not continue_conversation

        # If we only want one conversation, break.
        if once and (not continue_conversation):
            break

    logging.info("Finished conversation")


@click.command()
def main():
    global interrupted
    global assistant

    model = '/home/pi/MrNoisyListener/Mr_Noisy.pmdl'

    # Setup configuration
    credentials = os.path.join(click.get_app_dir('google-oauthlib-tool'), 'credentials.json')
    device_config = os.path.join(click.get_app_dir('mr-noisy'), 'device_config.json')

    with open(device_config) as f:
        device = json.load(f)
        device_id = device['id']
        device_model_id = device['model_id']
        logging.info("Using device model %s and device id %s",
                     device_model_id,
                     device_id)

    device_handler = device_helpers.DeviceRequestHandler(device_id)

    with conversation_assistant.GoogleAssistant(device_model_id, device_id, device_handler, credentials) as assistant:
        detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
        print('Listening for the Hotword Mr Noisy... Press Ctrl+C to exit')

        # main loop
        detector.start(detected_callback=ask_google_callback,
                       interrupt_check=interrupt_callback,
                       sleep_time=0.03)

        detector.terminate()


if __name__ == '__main__':
    main()
