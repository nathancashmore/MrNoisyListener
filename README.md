# MrNoisyListener
Google assistant with an alternative hotword.  

This contains a couple of files to provide a very simple extension of the [Snowboy](https://snowboy.kitt.ai/) 
and [Google Assistant](https://developers.google.com/assistant/sdk/guides/service/python/embed/setup?hardware=rpi) examples
to allow a raspery pi to talk to google.

# Prerequisite
* Rasperry Pi with latest [Lite version of OS](https://www.raspberrypi.org/downloads/raspberry-pi-os/)
* Installation of Google Assistant, Snowboy and relevant soundcard dependencies

# Setup
Execute the ```deploy.sh``` script to copy files across to the appropriate directories where the structure is as follows:
```
/home
 |
 --pi
   |
   --google : Directory containing Google Assistant sample code
   --snowboy : Directory containing Snowboy sample code
```   
# Execute
From the ```/home/pi``` home directory just execute ```./run.sh```


# Reference
More details of the original project can be found at the link below.
* [A new fashioned radio](http://dev.staticvoid.co.uk/2020/04/21/new-fashioned-radio/)
