import os
from getch import getch

ESCAPE = '\x1b'
ARROW_KEY_UP = '[A'
ARROW_KEY_DOWN = '[B'
ARROW_KEY_RIGHT = '[C'
ARROW_KEY_LEFT = '[D'

class View:

	# Character width of the terminal
	columns = None
	# Line height of the terminal
	rows = None
	# The hash of the torrent currently in view
	viewingTorrent = None
	# The hash of the currently focussed torrent
	focussedTorrent = 0
	# List of discovered torrents
	torrents = []

	frameStart = 0
	frameEnd = 0

	def render(self):
		self.clear()

		if self.viewingTorrent == None:
			print("SELECT A TORRENT TO INSPECT PIECES")
			print("---")
		
			if len(self.torrents) > 0:
				print("    NAME")

				row = 0
				for torrentHash in self.torrents:
					if row < self.frameStart or row > self.frameEnd:
						row += 1
						continue

					torrent = self.torrents[torrentHash]

					checkbox = "[x]" if self.focussedTorrent == row else "[ ]"

					print("{} {}".format(checkbox, torrent['name']))

					row += 1
			else:
				print("No torrents found")

			print("---")
			print("(ENTER) Select\t(Q)uit\t(R)efresh torrents", self.frameStart, self.frameEnd, self.rows)

		key = getch()

		if key == ESCAPE:
			key = getch() + getch()

			if key == ARROW_KEY_DOWN:
				self.focussedTorrent = min(self.focussedTorrent + 1, len(self.torrents) - 1)

				if self.focussedTorrent > self.frameEnd:
					self.frameEnd = min(self.frameEnd + 1, len(self.torrents) - 1)
					self.frameStart = max(self.frameEnd - (self.rows - 7), 0)
			elif key == ARROW_KEY_UP:
				self.focussedTorrent = max(self.focussedTorrent - 1, 0)

				if self.focussedTorrent < self.frameStart:
					self.frameStart -= 1
					self.frameEnd = min(self.frameStart + (self.rows - 7), len(self.torrents) - 1)
		elif key == 'q':
			exit()

		self.render()

	def setTorrents(self, torrents):
		self.torrents = torrents

		self.checkDimensions()

		self.focussedTorrent = 0
		self.frameStart = 0
		self.frameEnd = min(self.rows - 7 - self.frameStart, len(self.torrents) - 1)

		self.render()

	def checkDimensions(self):
		terminalSize = os.get_terminal_size()
		self.columns = terminalSize[0]
		self.rows = terminalSize[1]

	def clear(self):
		os.system('clear')