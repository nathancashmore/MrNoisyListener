import json
import logging
import os
import os.path
import click

from assistant.grpc import device_helpers, conversation_assistant


@click.command()
def main():
    # Setup logging.
    logging.basicConfig(level=logging.INFO)

    # Setup configuration
    credentials = os.path.join(click.get_app_dir('google-oauthlib-tool'), 'credentials.json')
    device_config = os.path.join(click.get_app_dir('mr-noisy'), 'device_config.json')
    once = False

    with open(device_config) as f:
        device = json.load(f)
        device_id = device['id']
        device_model_id = device['model_id']
        logging.info("Using device model %s and device id %s",
                     device_model_id,
                     device_id)

    device_handler = device_helpers.DeviceRequestHandler(device_id)

    with conversation_assistant.GoogleAssistant(device_model_id, device_id, device_handler, credentials) as assistant:

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


if __name__ == '__main__':
    main()
