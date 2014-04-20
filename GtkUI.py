#This is part of Blather
# -- this code is licensed GPLv3
# Copyright 2013 Jezra
import sys
import gobject
#Gtk
import pygtk
import gtk

class UI(gobject.GObject):
	__gsignals__ = {
		'command' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))
	}

	def __init__(self,args, continuous):
		gobject.GObject.__init__(self)
		self.continuous = continuous
		#make a window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_default_size(325, 55)
		self.window.connect("delete_event", self.delete_event)
		#give the window a name
		self.window.set_title("Blather Personal Servant (Gtk)")
		self.window.set_resizable(True) #why not resizable?

		layout = gtk.VBox()
		self.window.add(layout)
		#make a listen/stop button
		self.lsbutton = gtk.Button("Listen")
		layout.add(self.lsbutton)
		#make a continuous button
		self.ccheckbox = gtk.CheckButton("Continuous Listen")
		layout.add(self.ccheckbox)

		#connect the buttons
		self.lsbutton.connect("clicked",self.lsbutton_clicked)
		self.ccheckbox.connect("clicked",self.ccheckbox_clicked)

		#add a label to the UI to display the last command
		self.label = gtk.Label()
		layout.add(self.label)

		#create an accellerator group for this window
		accel = gtk.AccelGroup()
		#add the ctrl+q to quit
		accel.connect_group(gtk.keysyms.q, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE, self.accel_quit )
		#lock the group
		accel.lock()
		#add the group to the window
		self.window.add_accel_group(accel)

	def ccheckbox_clicked(self, widget):
		checked = self.ccheckbox.get_active()
		self.lsbutton.set_sensitive(not checked)
		if checked:
			self.lsbutton_stopped()
			self.emit('command', "continuous_listen")
		else:
			self.emit('command', "continuous_stop")

	def lsbutton_stopped(self):
		self.lsbutton.set_label("Listen")

	def lsbutton_clicked(self, button):
		val = self.lsbutton.get_label()
		if val == "Listen":
			self.emit("command", "listen")
			self.lsbutton.set_label("Stop")
			#clear the label
			self.label.set_text("")
		else:
			self.lsbutton_stopped()
			self.emit("command", "stop")

	def run(self):
		self.window.show_all()
		if self.continuous:
			self.ccheckbox.set_active(True)

	def accel_quit(self, accel_group, acceleratable, keyval, modifier):
		self.emit("command", "quit")

	def delete_event(self, x, y ):
		self.emit("command", "quit")

	def finished(self, text):
		print text
		#if the continuous isn't pressed
		if not self.ccheckbox.get_active():
			self.lsbutton_stopped()
		self.label.set_text(text)

	def set_icon(self, icon):
		gtk.window_set_default_icon_from_file(icon)

