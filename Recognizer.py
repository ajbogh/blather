#This is part of Blather
# -- this code is licensed GPLv3
# Copyright 2013 Jezra

import gi
gi.require_version('Gst', '1.0')
import os.path
from gi.repository import GObject as gobject
from gi.repository import Gst as gst
gst.init(None)

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
		cmd = audio_src+' ! audioconvert ! audioresample ! pocketsphinx name=asr ! appsink sync=false'
		self.pipeline=gst.parse_launch( cmd )
		#get the Auto Speech Recognition piece
		asr=self.pipeline.get_by_name('asr')
		bus=self.pipeline.get_bus()
		bus.add_signal_watch()
		bus.connect('message::element', self.element_message)
		asr.set_property('lm', language_file)
		asr.set_property('dict', dictionary_file)
		asr.set_property('configured', True)

	def listen(self):
		self.pipeline.set_state(gst.STATE_PLAYING)

	def pause(self):
		self.vad.set_property('silent', True)
		self.pipeline.set_state(gst.STATE_PAUSED)

	def element_message(self, bus, msg):
		msgtype = msg.get_structure().get_name()
		if msgtype != 'pocketsphinx' and msg.get_structure().get_value('final'):
			self.result(self, bus, msg.get_structure().get_value('hypothesis'), msg.get_structure().get_value('confidence'))

	def result(self, asr, text, uttid):
		#emit finished
		self.emit("finished", text)

