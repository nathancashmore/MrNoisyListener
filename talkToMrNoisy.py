import json
import click
from snowboy import snowboydecoder
from gpiozero import LED

from assistant.grpc import device_helpers, conversation_assistant

interrupted = False
google_assistant = object
led = LED(18)

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
    led.on()


def ask_google_callback(filename):
    global credentials
    global device_config
    global google_assistant

    print("Switching to input from file : " + filename)
    google_assistant.switch_to_input_from_file(filename)
    while True:

        continue_conversation = google_assistant.assist()

        if continue_conversation:
            google_assistant.switch_to_input_from_mic()

        if not continue_conversation:
            print("Conversation with google over")
            led.off()
            break


@click.command()
def main():
    global interrupted
    global google_assistant

    led.on()
    
    model = '/home/pi/MrNoisyListener/Mr_Noisy.pmdl'
    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5, audio_gain=0.5)

    with open(device_config) as f:
        device = json.load(f)
        device_id = device['id']
        device_model_id = device['model_id']
        print("Using device model :" + device_model_id + " and device id : " + device_id)

    device_handler = device_helpers.DeviceRequestHandler(device_id)
    print("setup device_handler")

    with conversation_assistant.GoogleAssistant(device_model_id, device_id, device_handler, credentials) \
            as assistant:

        print("Google Assistant setup complete.... waiting for request")
        google_assistant = assistant

        print('Listening for the Hotword Mr Noisy... Press Ctrl+C to exit')
        led.off()

        # main loop
        detector.start(detected_callback=detected_callback,
                       audio_recorder_callback=ask_google_callback,
                       interrupt_check=interrupt_callback,
                       sleep_time=0.03,
                       silent_count_threshold=2)

        detector.terminate()


if __name__ == '__main__':
    main()
