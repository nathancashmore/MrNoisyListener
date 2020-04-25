import json
import logging
import os
import os.path
import sys
import click
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

from assistant.grpc import audio_helpers, device_helpers, conversation_assistant

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5

@click.command()
def main():

    # Setup logging.
    logging.basicConfig(level=logging.INFO)

    # Setup configuration
    api_endpoint = ASSISTANT_API_ENDPOINT
    credentials = os.path.join(click.get_app_dir('google-oauthlib-tool'), 'credentials.json')
    device_config = os.path.join(click.get_app_dir('googlesamples-assistant'), 'device_config.json')
    lang = 'en-GB'
    grpc_deadline = DEFAULT_GRPC_DEADLINE
    once = False

    # Load OAuth 2.0 credentials.
    try:
        with open(credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run google-oauthlib-tool to initialize '
                      'new OAuth 2.0 credentials.')
        sys.exit(-1)

    # Create an authorized gRPC channel.
    grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, api_endpoint)
    logging.info('Connecting to %s', api_endpoint)

    # Configure audio source and sink.
    audio_sink = audio_helpers.SoundDeviceStream(
        sample_rate=16000,
        sample_width=2,
        block_size=6400,
        flush_size=25600
    )

    audio_source = audio_helpers.SoundDeviceStream(
        sample_rate=16000,
        sample_width=2,
        block_size=6400,
        flush_size=25600
    )

    # Create conversation stream with the given audio source and sink.
    conversation_stream = audio_helpers.ConversationStream(
        source=audio_source,
        sink=audio_sink,
        iter_size=3200,
        sample_width=2,
    )

    with open(device_config) as f:
        device = json.load(f)
        device_id = device['id']
        device_model_id = device['model_id']
        logging.info("Using device model %s and device id %s",
                     device_model_id,
                     device_id)

    device_handler = device_helpers.DeviceRequestHandler(device_id)

    with conversation_assistant.GoogleAssistant(lang, device_model_id, device_id,
                         conversation_stream, grpc_channel, grpc_deadline,
                         device_handler) as assistant:

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
