import os
import stat
import glob
from itertools import repeat

class Downloads:
	directories = []

	def __init__(self, directories):
		self.directories = directories

	def findTorrentFiles(self, torrent):
		topLvlMatch = None

		for directory in self.directories:
			target = glob.escape(directory + torrent['name']) + '*'

			candidates = glob.glob(target)

			if len(candidates) > 0:
				# The shortest match for the pattern above is the closest match
				topLvlMatch = min(candidates)
				break

		if topLvlMatch == None:
			filePaths = list(map(lambda file: os.sep.join(file[0]), torrent['files']))
			return list(zip(filePaths, repeat(None, len(filePaths))))

		# This can throw but a crash from this is expected
		tlStat = os.stat(topLvlMatch)

		matches = []
		if stat.S_ISDIR(tlStat.st_mode) == 0:
			# This is a single file torrent
			matches.append((torrent['name'], topLvlMatch))
		else:
			topLvlMatch = topLvlMatch if topLvlMatch[-1] == os.sep else topLvlMatch + os.sep

			for file in torrent['files']:
				filePath = os.sep.join(file[0])

				match = glob.glob(glob.escape(topLvlMatch + filePath) + '*')

				if len(match) < 1:
					matches.append((filePath, None))
					continue
				
				matches.append((filePath, min(match)))

		return matches