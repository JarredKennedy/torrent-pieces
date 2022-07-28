import sys
import os
from getch import getch

from bencoding import Bdecoder
from torrents import TorrentStore, TorrentReader
from downloads import Downloads
from views import SelectTorrentView, TorrentPiecesView

parseDirectoryPaths = lambda pathExpression: map(lambda path: path if path[-1] == os.sep else path + os.sep, pathExpression.split(':'))

envTorrentsDirs = "TORP_TORRENTS"
envDownloadsDirs = "TORP_DOWNLOADS"

if envTorrentsDirs not in os.environ or envDownloadsDirs not in os.environ:
	print("TORP_TORRENTS and TORP_DOWNLOADS environment variables must be set")
	exit(1)

torrentsDirList = parseDirectoryPaths(os.environ[envTorrentsDirs])
downloadsDirList = parseDirectoryPaths(os.environ[envDownloadsDirs])

torrentsDirList = list(filter(os.path.isdir, torrentsDirList))
downloadsDirList = list(filter(os.path.isdir, downloadsDirList))

bdecoder = Bdecoder()
torrentReader = TorrentReader(bdecoder)

torrentStore = TorrentStore(torrentReader, torrentsDirList)
downloads = Downloads(downloadsDirList)

torrentData = {}
piecesData = {}

selectTorrentView = SelectTorrentView(torrentData)
torrentPiecesView = TorrentPiecesView(piecesData)

currentView = None

def main():
	setView(selectTorrentView)
	handleUserInput()

def handleUserInput():
	ESCAPE = '\x1b'
	ARROW_KEY_UP = '[A'
	ARROW_KEY_DOWN = '[B'
	ARROW_KEY_RIGHT = '[C'
	ARROW_KEY_LEFT = '[D'
	ENTER = '\x0A'

	key = getch()

	if key == ESCAPE:
		key = getch() + getch()

		currentTorrentIndex = 0
		if torrentData['currentTorrent'] in torrentData['torrentOrder']:
			currentTorrentIndex = torrentData['torrentOrder'].index(torrentData['currentTorrent'])

		if currentView == selectTorrentView and key == ARROW_KEY_DOWN:
			nextTorrentIndex = min(currentTorrentIndex + 1, len(torrentData['torrentOrder']) - 1)
			focusTorrent(torrentData['torrentOrder'][nextTorrentIndex])
		elif currentView == selectTorrentView and key == ARROW_KEY_UP:
			nextTorrentIndex = max(currentTorrentIndex - 1, 0)
			focusTorrent(torrentData['torrentOrder'][nextTorrentIndex])
	elif currentView == selectTorrentView and key == ENTER:
		selectTorrent(torrentData['currentTorrent'])
	elif currentView == torrentPiecesView and key == 'b':
		returnToSelectTorrent()
	elif key == 'q':
		quitProgram()
	else:
		handleUserInput()

def focusTorrent(torrentHash):
	torrentData['currentTorrent'] = torrentHash
	selectTorrentView.render()
	handleUserInput()

def selectTorrent(torrentHash):
	torrent = torrentStore.torrents[torrentHash]
	piecesData['torrent'] = torrent
	piecesData['files'] = downloads.findTorrentFiles(torrent)
	piecesData['havePieces'] = downloads.readPieces(torrent, piecesData['files'])

	torrentPiecesView.update(piecesData)
	setView(torrentPiecesView)
	handleUserInput()

def returnToSelectTorrent():
	setView(selectTorrentView)
	handleUserInput()

def quitProgram():
	print("\nQuit")
	exit()

def setView(view):
	global currentView

	currentView = view

	if view == selectTorrentView:
		torrentStore.findTorrents()

		# for i in range(1, 21):
		# 	torrentStore.torrents[str(i)] = {'name': "Some torrent #{}".format(i)}

		torrentData['torrents'] = torrentStore.torrents
		torrentData['torrentOrder'] = list(torrentStore.torrents.keys())
		torrentData['currentTorrent'] = torrentData['torrentOrder'][0]

		selectTorrentView.render()

if __name__ == '__main__':
	main()