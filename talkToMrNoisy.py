import json
import logging
import click
from snowboy import snowboydecoder

from assistant.grpc import device_helpers, conversation_assistant

interrupted = False
assistant = object

credentials = '/home/pi/.config/google-oauthlib-tool/credentials.json'
device_config = '/home/pi/.config/mr-noisy/device_config.json'

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


def ask_google_callback():
    global assistant
    global credentials
    global device_config

    with open(device_config) as f:
        device = json.load(f)
        device_id = device['id']
        device_model_id = device['model_id']
        logging.info("Using device model %s and device id %s",
                     device_model_id,
                     device_id)

    device_handler = device_helpers.DeviceRequestHandler(device_id)

    with conversation_assistant.GoogleAssistant(device_model_id, device_id, device_handler, credentials) as assistant:
        while True:
            continue_conversation = assistant.assist()
            if not continue_conversation:
                break

@click.command()
def main():
    global interrupted
    global assistant

    model = '/home/pi/MrNoisyListener/Mr_Noisy.pmdl'

    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.6, audio_gain=1.0)
    print('Listening for the Hotword Mr Noisy... Press Ctrl+C to exit')

    # main loop
    detector.start(detected_callback=ask_google_callback,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)

    detector.terminate()

if __name__ == '__main__':
    main()
