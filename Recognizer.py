#This is part of Blather
# -- this code is licensed GPLv3
# Copyright 2013 Jezra

import gi
import os.path
from gi.repository import GObject as gobject
import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone()

#define some global variables
this_dir = os.path.dirname( os.path.abspath(__file__) )

class Recognizer(gobject.GObject):
    __gsignals__ = {
        'finished' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))
    }
    def __init__(self, language_file, dictionary_file, strings_file, src = None):
        gobject.GObject.__init__(self)

        self.keywords = self.read_keywords(strings_file);

        print("A moment of silence, please...")
        with m as source: r.adjust_for_ambient_noise(source)
        print("Set minimum energy threshold to {}".format(r.energy_threshold))

    def read_keywords(self, strings_file):
        #read the.commands file
        strings = open(strings_file)
        keywords = []
        for line in strings:
            line = line.strip()
            keywords.append([line, 1])
        
        #close the strings file
        strings.close()
        return keywords

    def callback(self, recognizer, audio):
        print("Got it! Now to recognize it...")
        # recognize speech using Sphinx
        try:
            text = recognizer.recognize_sphinx(audio, "en-US", self.keywords, None)
            print("Sphinx thinks you said " + text)
            self.result(text)
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))

    def listen(self):
        print("Say something!")
        self.stop_listening = r.listen_in_background(m, self.callback)
        return

    def pause(self):
        try:
            self.stop_listening()
            print("No longer listening")
        except Exception:
            pass        
        return

    def result(self, text):
        #emit finished
        self.emit("finished", text)

