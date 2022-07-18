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

	torrents = []

	def render(self):
		if self.viewingTorrent == None:
			print("SELECT A TORRENT TO INSPECT PIECES")
			print("---")
		
			if len(self.torrents) > 0:
				print("    NAME")

				for torrentHash in self.torrents:
					torrent = self.torrents[torrentHash]
					print("[ ] " + torrent['name'])
			else:
				print("No torrents found")

			print("---")
			print("(q)uit (r)efresh torrents")

	def setTorrents(self, torrents):
		self.torrents = torrents

		self.render()

	def checkDimensions(self):
		print("Something happened")

	def clear(self):
		print(ESCAPE + "[2J" + ESCAPE + "[H")