#!/usr/bin/env python3

import socket
import xmltodict
import json
import code
import struct
import magicnumbers
import os

class Dom0Session:
	"""Manager for a connection to the dom0 server."""
	def __init__(self, host='192.168.0.14', port=3001, tasksFile='tasks.xml'):
		"""Initialize connection and parse tasks description."""
		self.connect(host, port)
		self.readTasks(tasksFile)

	def connect(self, host='192.168.0.14', port=3001):
		"""Connect to the Genode dom0 server."""
		self.conn = socket.create_connection((host, port))
		print('Connected.')

	def readTasks(self, tasksFile='tasks.xml'):
		"""Read XML file, discard meta data, and purge invalid tasks."""
		# Read XML file and discard meta data.
		tasks = xmltodict.parse(open(tasksFile, 'rb'))
		tasks = tasks['taskset']['periodictask']

		# Make sure we have an array of descriptions.
		if not isinstance(tasks, list):
			tasks = [tasks]

		# Enumerate binaries and purge obsolete entries.
		self.binaries = []
		for task in tasks:
			if task['pkg'] not in self.binaries:
				self.binaries.append(task['pkg'])
			del task['ucfirmrt']
			del task['uawmean']

		# Convert to JSON file.
		self.tasks = json.dumps(tasks)

	def sendDescs(self):
		"""Send task descriptions to the dom0 server."""
		meta = struct.pack('II', magicnumbers.task_desc, len(self.tasks))
		print('Sending tasks description.')
		self.conn.send(meta)
		self.conn.send(self.tasks.encode('ascii'))

	def sendBins(self):
		"""Send binary files to the dom0 server."""
		meta = struct.pack('II', magicnumbers.send_binaries, len(self.binaries))
		print('Sending {} binar{}.'.format(len(self.binaries), 'y' if len(self.binaries) == 1 else 'ies'))
		self.conn.send(meta)

		for name in self.binaries:
			print('Sending {}.'.format(name))
			file = open(name, 'rb').read()
			size = os.stat(name).st_size
			meta = struct.pack('8sI', name.encode('ascii'), size)
			self.conn.send(meta)
			self.conn.send(file)

			# Wait for 'go' message.
			msg = int.from_bytes(self.conn.recv(4), 'little')
			if msg != magicnumbers.go_send:
				print('Invalid answer received, aborting: {}'.format(msg))
				break

	def start(self):
		"""Send message to start the tasks on the server."""
		print('Starting tasks on server.')
		meta = struct.pack('I', magicnumbers.start)
		self.conn.send(meta)

	def startEx(self):
		"""Send task descriptions and binaries, and start the execution."""
		self.sendDescs()
		self.sendBins()
		self.start()

	def close(self):
		"""Close connection."""
		self.conn.close();

session = Dom0Session()

print('''
Available commands:
	session.sendDescs()	: Send task descriptions to server.
	session.sendBins()	: Send binaries to server.
	session.start()		: Start tasks on server.
	session.startEx()	: Do all of the above in order.

	session.readTasks([tasksFile])	: Load tasks file (default tasks.xml).
	session.connect([host, port])	: Connect to dom0 server (default 192.168.0.14:3001).
	session.close()			: Close connection.
''')

code.interact(local=locals())