import os

class View:

	# Character width and line height of the terminal
	terminalSize = (0, 0)
	# Data for rendering the view
	state = None

	def update(self, state):
		self.state = state
		self.render()

	def checkDimensions(self):
		self.terminalSize = os.get_terminal_size()

	def clear(self):
		os.system('clear')

class SelectTorrentView(View):
	lastSelected = 0
	fixtureRows = 7

	frameStart = 0
	frameEnd = 0

	def __init__(self, state):
		self.state = state
		self.checkDimensions()

	def render(self):
		self.clear()

		print("SELECT A TORRENT TO INSPECT PIECES")
		print("---")

		if len(self.state['torrentOrder']) > 0:
			print("    NAME")

			if self.frameEnd < 1:
				self.frameEnd = min(self.terminalSize[1] - self.fixtureRows, len(self.state['torrentOrder']) - 1)

			currentTorrentIndex = 0
			if self.state['currentTorrent'] in self.state['torrentOrder']:
				currentTorrentIndex = self.state['torrentOrder'].index(self.state['currentTorrent'])

			if currentTorrentIndex > self.lastSelected and currentTorrentIndex > self.frameEnd:
				self.frameEnd = min(self.frameEnd + 1, len(self.state['torrentOrder']) - 1)
				self.frameStart = max(self.frameEnd - (self.terminalSize[1] - 7), 0)
			elif currentTorrentIndex < self.lastSelected and currentTorrentIndex < self.frameStart:
				self.frameStart -= 1
				self.frameEnd = min(self.frameStart + (self.terminalSize[1] - 7), len(self.state['torrentOrder']) - 1)

			row = 0
			for torrentHash in self.state['torrentOrder']:
				if row < self.frameStart or row > self.frameEnd:
					row += 1
					continue

				torrent = self.state['torrents'][torrentHash]

				checkbox = "[x]" if self.state['currentTorrent'] == torrentHash else "[ ]"

				print("{} {}".format(checkbox, torrent['name']))

				row += 1

			self.lastSelected = currentTorrentIndex
		else:
			print("No torrents found")

		print("---")
		print("(ENTER) Select  (R)efresh torrents  (Q)uit")

class TorrentPiecesView(View):

	def __init__(self, state):
		self.state = state

	def render(self):
		self.clear()

		numPieces = len(self.state['havePieces'])
		totalPieces = self.state['torrent']['piece_count']

		print("TORRENT PIECES")
		print("---")
		print(self.state['torrent']['name'])
		print("{:.2f}% Completed ({}/{} pieces)".format((numPieces / totalPieces) * 100, numPieces, totalPieces))
		print("---")
		print("(B)ack  (R)efresh pieces  (Q)uit")