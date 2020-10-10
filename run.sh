#!/usr/bin/env bash

while :
  do
	python ./snowboy/singleWord.py ./resources/Mr_Noisy.pmdl
	aplay ./resources/Welcome.wav &
	python ./google/pushtotalk_led.py --once
  done
