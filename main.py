import sys
import os

from bencoding import Bdecoder
from torrents import TorrentList, TorrentReader
from downloadfinder import DownloadFinder
from view import View

def main(watch=False):
	envTorrentsDirs = "TORP_TORRENTS"
	envDownloadsDirs = "TORP_DOWNLOADS"

	if envTorrentsDirs not in os.environ or envDownloadsDirs not in os.environ:
		print("TORP_TORRENTS and TORP_DOWNLOADS environment variables must be set")
		exit(1)

	torrentsDirList = parseDirectoryPaths(os.environ[envTorrentsDirs])
	downloadsDirList = parseDirectoryPaths(os.environ[envDownloadsDirs])

	torrentsDirList = filter(os.path.isdir, torrentsDirList)
	downloadsDirList = filter(os.path.isdir, downloadsDirList)

	bdecoder = Bdecoder()
	torrentReader = TorrentReader(bdecoder)

	torrentList = TorrentList(torrentReader, torrentsDirList)
	downloadFinder = DownloadFinder(downloadsDirList)

	view = View()

	torrentList.findTorrents()

	for i in range(1, 21):
		torrentList.torrents[str(i)] = {'name': "Some torrent #{}".format(i)}

	view.setTorrents(torrentList.torrents)



def parseDirectoryPaths(pathExpression):
	return map(lambda path: path if path[-1] == os.sep else path + os.sep, pathExpression.split(':'))

if __name__ == "__main__":
	watch = "-w" in sys.argv

	main(watch);
