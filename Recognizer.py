#This is part of Blather
# -- this code is licensed GPLv3
# Copyright 2013 Jezra

import pygst
pygst.require('0.10')
import gst
import os.path
import gobject

#define some global variables
this_dir = os.path.dirname( os.path.abspath(__file__) )


class Recognizer(gobject.GObject):
	__gsignals__ = {
		'finished' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))
	}
	def __init__(self, language_file, dictionary_file, src = None):
		gobject.GObject.__init__(self)
		self.commands = {}
		if src:
			audio_src = 'alsasrc device="hw:%d,0"' % (src)
		else:
			audio_src = 'autoaudiosrc'

		#build the pipeline
		cmd = audio_src+' ! audioconvert ! audioresample ! vader name=vad ! pocketsphinx name=asr ! appsink sync=false'
		self.pipeline=gst.parse_launch( cmd )
		#get the Auto Speech Recognition piece
		asr=self.pipeline.get_by_name('asr')
		asr.connect('result', self.result)
		asr.set_property('lm', language_file)
		asr.set_property('dict', dictionary_file)
		asr.set_property('configured', True)
		#get the Voice Activity DEtectoR
		self.vad = self.pipeline.get_by_name('vad')
		self.vad.set_property('auto-threshold',True)

	def listen(self):
		self.pipeline.set_state(gst.STATE_PLAYING)

	def pause(self):
		self.vad.set_property('silent', True)
		self.pipeline.set_state(gst.STATE_PAUSED)

	def result(self, asr, text, uttid):
		#emit finished
		self.emit("finished", text)

