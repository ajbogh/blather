#This is part of Blather
# -- this code is licensed GPLv3
# Copyright 2013 Jezra
import sys
import gobject
# Qt stuff
from PySide.QtCore import Signal, Qt
from PySide.QtGui import QApplication, QWidget, QMainWindow, QVBoxLayout
from PySide.QtGui import QLabel, QPushButton, QCheckBox, QIcon, QAction

class UI(gobject.GObject):
	__gsignals__ = {
		'command' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))
	}

	def __init__(self,args,continuous):
		self.continuous = continuous
		gobject.GObject.__init__(self)
		#start by making our app
		self.app = QApplication(args)
		#make a window
		self.window = QMainWindow()
		#give the window a name
		self.window.setWindowTitle("BlatherQt")
		self.window.setMaximumSize(400,200)
		center = QWidget()
		self.window.setCentralWidget(center)

		layout = QVBoxLayout()
		center.setLayout(layout)
		#make a listen/stop button
		self.lsbutton = QPushButton("Listen")
		layout.addWidget(self.lsbutton)
		#make a continuous button
		self.ccheckbox = QCheckBox("Continuous Listen")
		layout.addWidget(self.ccheckbox)

		#connect the buttons
		self.lsbutton.clicked.connect(self.lsbutton_clicked)
		self.ccheckbox.clicked.connect(self.ccheckbox_clicked)

		#add a label to the UI to display the last command
		self.label = QLabel()
		layout.addWidget(self.label)

		#add the actions for quiting
		quit_action = QAction(self.window)
		quit_action.setShortcut('Ctrl+Q')
		quit_action.triggered.connect(self.accel_quit)
		self.window.addAction(quit_action)

	def accel_quit(self):
		#emit the quit
		self.emit("command", "quit")

	def ccheckbox_clicked(self):
		checked = self.ccheckbox.isChecked()
		if checked:
			#disable lsbutton
			self.lsbutton.setEnabled(False)
			self.lsbutton_stopped()
			self.emit('command', "continuous_listen")
		else:
			self.lsbutton.setEnabled(True)
			self.emit('command', "continuous_stop")

	def lsbutton_stopped(self):
		self.lsbutton.setText("Listen")

	def lsbutton_clicked(self):
		val = self.lsbutton.text()
		if val == "Listen":
			self.emit("command", "listen")
			self.lsbutton.setText("Stop")
			#clear the label
			self.label.setText("")
		else:
			self.lsbutton_stopped()
			self.emit("command", "stop")

	def run(self):
		self.window.show()
		if self.continuous:
			self.ccheckbox.setCheckState(Qt.Checked)
			self.ccheckbox_clicked()
		self.app.exec_()
		self.emit("command", "quit")

	def finished(self, text):
		print text
		#if the continuous isn't pressed
		if not self.ccheckbox.isChecked():
			self.lsbutton_stopped()
		self.label.setText(text)

	def set_icon(self, icon):
		self.window.setWindowIcon(QIcon(icon))
