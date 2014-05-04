# Blather
Blather is a speech recognizer that will run commands when a user speaks preset sentences.

## Requirements
1. pocketsphinx
2. gstreamer-0.10 (and what ever plugin has pocket sphinx support)
3. gstreamer-0.10 base plugins (required for alsa)
4. pyside (only required for the Qt based UI)
5. pygtk (only required for the Gtk based UI)
6. python-psutil

## Usage
0. move commands.tmp to ~/.config/blather/commands.conf and fill the file with sentences and command to run
1. Run Blather.py, this will generate ~/.config/blather/sentences.corpus based on sentences in the 'commands' file
2. quit blather (there is a good chance it will just segfault)
3. go to <http://www.speech.cs.cmu.edu/tools/lmtool.html> and upload the sentences.corpus file
4. download the resulting XXXX.lm file to the ~/.config/blather/language directory and rename to file to 'lm'
5. download the resulting XXXX.dic file to the ~/.config/blather/language directory and rename to file to 'dic'
6. run Blather.py
    * for Qt GUI, run Blather.py -i q
    * for Gtk GUI, run Blather.py -i g
    * to start a UI in 'continuous' listen mode, use the -c flag
    * to use a microphone other than the system default, use the -d flag
7. start talking

#### Bonus
once the sentences.corpus file has been created, run the language_updater.sh script to automate the process of creating and downloading language files.

#### Examples
To run blather with the GTK UI and start in continuous listen mode:

    ./Blather.py -i g -c

To run blather with the GTK UI and start in continuous listen mode where you only have to say the keyword once during commands that are 10 seconds apart:

    ./Blather.py -i g -c -k 10

    "[keyword] command" ... "command 2" ... 10 seconds goes by ... "[keyword] command 3"

To run blather with no UI and using a USB microphone recognized and device 2:

    ./Blather.py -d 2

#### Finding the Device Number of a USB microphone
There are a few ways to find the device number of a USB microphone.

* `cat /proc/asound/cards`
* `arecord -l`

## Features
#### Keyword Activation
Blather uses a keyword for activation. You may choose any keyword you like such as "Blather", "Hal", "Computer", "Jarvis", "R2", etc. 
Find the keyword example in the commands.tmp for more information.

#### Plugins
Plugin scripts can be created within the ~/.config/blather/plugins directory. These can be any file type that can be executed in the terminal using absolute or relative paths.
For example scriptname.sh, where it can be executed by typing ~/.config/blather/plugins/scriptname.sh

The script can contain any code necessary to execute a task. No command-line parameters will be passed, however the script may use any resource such as 
websites, APIs, or services.

#### Cancelling commands
Some commands can start applications or phrases that may need to be cancelled. This can become apparent when using espeak commands and large phrases. 
It is useful to issue a "cancel" command to inform the speach recognition system that the previous command should be stopped.

Custom cancel commands can be configured in the commands.conf file in the format of "[yourword]:cancel". See the commands.tmp file for examples.

To prevent commands from being cancelled you can use linux screen to start the program in a disconnected thread:

    screen -d -m thunderbird

When using screen any cancel command or terminating Blather will leave the application running. This is especially useful for things like email or browser applications.

#### Automatic command updates
If the commands.conf file is updated then Blather will automatically detect that change on load as well as AFTER a voice is recognized and it will run the language updater and command read method to incorporate the changes into its system. This allows you to change the commands.conf file at any time, say a single command, then wait for the update to happen. It usually takes a couple of seconds before you can use the new commands.
