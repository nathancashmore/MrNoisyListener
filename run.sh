#!/usr/bin/env bash

python /home/pi/snowboy/startup_lights.py &

while :
  do
	python /home/pi/snowboy/singleWord.py /home/pi/resources/Mr_Noisy.pmdl
	aplay /home/pi/resources/Welcome.wav &
	python /home/pi/google/pushtotalk_led.py --once
  done
