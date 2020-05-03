import json
import click
from snowboy import snowboydecoder

from assistant.grpc import device_helpers, conversation_assistant

interrupted = False

credentials = '/home/pi/.config/google-oauthlib-tool/credentials.json'
device_config = '/home/pi/.config/mr-noisy/device_config.json'


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


def detected_callback():
    print('recording audio...')


def ask_google_callback(filename):
    global credentials
    global device_config

    print("Question found in: " + filename)

    with open(device_config) as f:
        device = json.load(f)
        device_id = device['id']
        device_model_id = device['model_id']
        print("Using device model :" + device_model_id + " and device id : " + device_id)

    device_handler = device_helpers.DeviceRequestHandler(device_id)

    with conversation_assistant.GoogleAssistant(device_model_id, device_id, device_handler, credentials, filename) \
            as assistant:
        while True:
            continue_conversation = assistant.assist()

            if continue_conversation:
                assistant.switch_to_input_from_mic()

            if not continue_conversation:
                print("Conversation with google over")
                break


@click.command()
def main():
    global interrupted

    model = '/home/pi/MrNoisyListener/Mr_Noisy.pmdl'

    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.6, audio_gain=1.0)
    print('Listening for the Hotword Mr Noisy... Press Ctrl+C to exit')

    # main loop
    detector.start(detected_callback=detected_callback,
                   audio_recorder_callback=ask_google_callback,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03,
                   silent_count_threshold=2)

    detector.terminate()


if __name__ == '__main__':
    main()
