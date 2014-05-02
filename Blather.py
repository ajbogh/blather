#!/usr/bin/env python2

# -- this code is licensed GPLv3
# Copyright 2013 Jezra
# Modifications by: Allan Bogh - ajbogh@allanbogh.com

import sys
import signal
import gobject
import os.path
import subprocess
import shutil
import psutil
from optparse import OptionParser

#keywords defined in the commands.conf file
keywords = []
PERCENT_MATCH_LIMIT = 75

#where are the files?
conf_dir = os.path.expanduser("~/.config/blather")
lang_dir = os.path.join(conf_dir, "language")
file_dir = os.path.dirname(os.path.abspath(__file__))
plugin_dir = os.path.join(conf_dir, "plugins")
command_file = os.path.join(conf_dir, "commands.conf")
strings_file = os.path.join(conf_dir, "sentences.corpus")
history_file = os.path.join(conf_dir, "blather.history")
language_update_script = os.path.join(file_dir, "language_updater.sh")
lang_file = os.path.join(lang_dir,'lm')
dic_file = os.path.join(lang_dir,'dic')
#make the lang_dir if it doesn't exist
if not os.path.exists(lang_dir):
	os.makedirs(lang_dir)
if not os.path.exists(plugin_dir):
	shutil.copytree(os.path.join(file_dir, "plugins"), plugin_dir)

class Blather:
	def __init__(self, opts):
		#import the recognizer so Gst doesn't clobber our -h
		from Recognizer import Recognizer
		self.ui = None
		#keep track of the opts
		self.opts = opts
		ui_continuous_listen = False
		self.continuous_listen = False
		self.commands = {}
		self.read_commands()
		self.recognizer = Recognizer(lang_file, dic_file, opts.microphone )
		self.recognizer.connect('finished',self.recognizer_finished)
	
		self.commandFileTime = 0
		#updates language file and commands on start
		self.checkCommandFile()

		self.commandFileTime = os.path.getmtime(command_file)

		#read options
		if opts.interface != None:
			if opts.interface == "q":
				#import the ui from qt
				from QtUI import UI
			elif opts.interface == "g":
				from GtkUI import UI
			else:
				print "no GUI defined"
				sys.exit()

			self.ui = UI(args,opts.continuous)
			self.ui.connect("command", self.process_command)
			#can we load the icon resource?
			icon = self.load_resource("icon.png")
			if icon:
				self.ui.set_icon(icon)

		if self.opts.history:
			self.history = []

	def read_commands(self):
		#read the.commands file
		file_lines = open(command_file)
		strings = open(strings_file, "w")
		for line in file_lines:
				print line
				#trim the white spaces
				line = line.strip()
				#if the line has length and the first char isn't a hash
				if len(line) and line[0]!="#":
						#this is a parsible line
						(key,value) = line.split(":",1)
						print key, value
						#get the keyword out of the commands file
						if value == "keyword" and key.strip().lower() not in keywords:
							keywords.append(key.strip().lower())
							continue
						self.commands[key.strip().lower()] = value.strip()
						strings.write( key.strip()+"\n")

		#close the strings file
		strings.close()

	def log_history(self,text):
		if self.opts.history:
			self.history.append(text)
			if len(self.history) > self.opts.history:
				#pop off the first item
				self.history.pop(0)

			#open and truncate the blather history file
			hfile = open(history_file, "w")
			for line in self.history:
				hfile.write( line+"\n")
			#close the  file
			hfile.close()

	def recognizer_finished(self, recognizer, text):
		#split the words spoken into an array
		t = text.lower()
		textWords = t.split(" ")

		#get the keys array for all commands
		biggestKey = ""
		biggestKeySet = []
		biggestKeyCount = 0
		
		ret = self.search_for_matches(textWords)
		biggestKey = ret['biggestKey']
		biggestKeySet = ret['biggestKeySet']
		biggestKeyCount = ret['biggestKeyCount']

		#find the match percentage
		percentMatch = self.calculate_match_percentage(biggestKeySet, biggestKeyCount)

		#call the process
		if biggestKeyCount > 0 and ((len(textWords) <= 2 and len(biggestKeySet) == len(textWords)) or percentMatch >= PERCENT_MATCH_LIMIT): #must be equal or a 60% match
			print("Best match: " + biggestKey, "Detected: " + text.lower(), "Percent match: " + str(percentMatch));
			cmd = self.commands[biggestKey]
			if cmd == "cancel" and hasattr(self, 'runningProcess'):
				print("Cancelling previous command with PID "+str(self.runningProcess.pid))
				
				self.terminate_child_processes(self.runningProcess.pid)

				#terminate parent process
				self.runningProcess.terminate();
			elif cmd != "cancel":
				print cmd
				if "plugins/" in cmd:
					#execute a plugin script
					self.runningProcess = subprocess.Popen(os.path.join(file_dir,cmd), shell=True)
				else:
					self.runningProcess = subprocess.Popen(cmd, shell=True)
				self.log_history(text)
		else:
			print("No matching command", "Percent match: " + str(percentMatch))
		#if there is a UI and we are not continuous listen
		if self.ui:
			if not self.continuous_listen:
				#stop listening
				self.recognizer.pause()
			#let the UI know that there is a finish
			self.ui.finished(t)
		#check if the command.conf file has changed.
		self.checkCommandFile()

	def run(self):
		if self.ui:
			self.ui.run()
		else:
			blather.recognizer.listen()

	def quit(self):
		sys.exit(0)

	def checkCommandFile(self):
		newFileTime = os.path.getmtime(command_file)
		if newFileTime > self.commandFileTime:
			print("Command.conf file modified")
			subprocess.call(language_update_script)
			print("Language file updated")
			self.commandFileTime = newFileTime
			self.read_commands()

	def process_command(self, UI, command):
		print command
		if command == "listen":
			self.recognizer.listen()
		elif command == "stop":
			self.recognizer.pause()
		elif command == "continuous_listen":
			self.continuous_listen = True
			self.recognizer.listen()
		elif command == "continuous_stop":
			self.continuous_listen = False
			self.recognizer.pause()
		elif command == "quit":
			self.quit()

	def load_resource(self,string):
		local_data = os.path.join(os.path.dirname(__file__), 'data')
		paths = ["/usr/share/blather/","/usr/local/share/blather", local_data]
		for path in paths:
			resource = os.path.join(path, string)
			if os.path.exists( resource ):
				return resource
		#if we get this far, no resource was found
		return False

	def search_for_matches(self, textWords):
		#TODO: https://github.com/ajbogh/blather/issues/1
		ret = {'biggestKey':'', 'biggestKeySet':{}, 'biggestKeyCount':0}
		for key in self.commands.keys():			
			#split the keys on each word
			words = set(key.split(" "))
			#append the keyword to the command if it's not there already
			##only if the timed keyword activation is needed
			if len(set(keywords).intersection(set(words))) == 0:
				words.update(keywords)
			#find the matching words
			matches = words.intersection(set(textWords))
			#determine if the words match
			if len(matches) > 1 and len(matches) > ret['biggestKeyCount'] and len(set(keywords).intersection(set(textWords))) > 0:
				ret['biggestKeySet'] = words
				ret['biggestKeyCount'] = len(matches)
				ret['biggestKey'] = key
		return ret

	def calculate_match_percentage(self, biggestKeySet, biggestKeyCount):
		percentMatch = 0
		if len(biggestKeySet) > 0:
			percentMatch = (biggestKeyCount/float(len(biggestKeySet))) * 100
		return percentMatch

	# terminate_child_processes kills any child processes under a parent pid.
	# It uses pgrep to list child processes, so the system must have pgrep installed in order
	# to use the 'cancel' commands
	def terminate_child_processes(self, pid):
		out = subprocess.Popen(['pgrep', '-P', str(pid)], stdout=subprocess.PIPE).communicate()[0]
		childProcesses = out.splitlines()
		# Kill any orphaned children.
		for pid in childProcesses:
			#recursive call to kill entire family tree
			self.terminate_child_processes(int(pid))
			print("Killing child with PID "+str(pid))
			p = psutil.Process(int(pid))
			p.terminate()


if __name__ == "__main__":
	#create a bunch of commandline options
	parser = OptionParser()
	parser.add_option("-i", "--interface",  type="string", dest="interface",
		action='store',
		help="Interface to use (if any). 'q' for Qt, 'g' for GTK")
	parser.add_option("-c", "--continuous",
		action="store_true", dest="continuous", default=False,
		help="starts interface with 'continuous' listen enabled")
	parser.add_option("-H", "--history", type="int",
		action="store", dest="history",
		help="number of commands to store in history file")
	parser.add_option("-m", "--microphone", type="int",
		action="store", dest="microphone", default=None,
		help="Audio input card to use (if other than system default)")

	(options, args) = parser.parse_args()
	#make our blather object
	blather = Blather(options)
	#init gobject threads
	gobject.threads_init()
	#we want a main loop
	main_loop = gobject.MainLoop()
	#handle sigint
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	#run the blather
	blather.run()
	#start the main loop

	try:
		main_loop.run()
	except:
		print "time to quit"
		main_loop.quit()
		sys.exit()

