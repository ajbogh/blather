#!/bin/sh

espeak "Yes sir";

# Use screen to separate a program from the cancel commands
# It will not be shut down when the voice recognition system is closed.
screen -d -m thunderbird;
