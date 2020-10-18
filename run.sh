#!/usr/bin/env bash

python /home/pi/snowboy/startup_lights.py &

while :
  do
    option=$(( $RANDOM % 2 ))
    welcome="Welcome_${option}.wav"

	python /home/pi/snowboy/singleWord.py /home/pi/resources/Mr_Noisy_2.pmdl
	aplay /home/pi/resources/${welcome} &
	python /home/pi/google/pushtotalk_led.py --once
  done
