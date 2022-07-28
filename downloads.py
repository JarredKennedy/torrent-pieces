import os
import stat
import glob
from itertools import repeat
from math import floor

class Downloads:
	# Directories specified by the user where downloading files are being written.
	directories = []

	# File paths known to have been completely downloaded
	# This prevents the readPieces method needing to read these files again
	knownCompleted = []

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

	def readPieces(self, torrent, torrentFiles):
		havePieces = []
		piece = 0
		totalPieces = torrent['piece_count']
		pieceSize = torrent['piece_size']

		# Want to first generate a list of pieces that have been downloaded.
		# This means a list of integers indicating piece 0, piece 1, ..., piece n.
		# With this list, it can be reported how many of the pieces have been downloaded.

		pieceOffset = 0
		fileIndex = 0
		while fileIndex < len(torrentFiles):
			filePath = torrentFiles[fileIndex][1]
			fileSize = torrent['files'][fileIndex][1]

			if filePath == None:
				bytesPassed = fileSize + abs(pieceOffset)
				piece += floor(bytesPassed / pieceSize)
				# pieceOffset increases because, unlike the case where it's already known a piece exists,
				# in this case it's already known this piece doesn't exist because a file which this
				# piece is part of doesn't exist.
				pieceOffset = bytesPassed % pieceSize
				fileIndex += 1
				continue

			file = open(filePath, 'rb')

			if pieceOffset < 0:
				# A negative pieceOffset means the current piece continues from the previous file
				# and has thus far been NUL bytes. Continue to read-and-check the rest of the piece
				# which is the pieceSize - |pieceOffset| bytes long.
				bytesToRead = pieceSize - abs(pieceOffset)
				offsetBefore = file.tell()
				rangeEmpty = self.isFileRangeEmpty(file, 0, bytesToRead)

				if not rangeEmpty:
					havePieces.append(piece)

				# If the piece being checked extends beyond this file then continue checking or skipping
				# this piece in the next file.
				if offsetBefore + bytesToRead >= fileSize:
					bytesRead = fileSize - offsetBefore
					if rangeEmpty:
						pieceOffset = bytesRead - bytesToRead
					else:
						pieceOffset = bytesToRead - bytesRead
						piece += 1
					fileIndex += 1
					continue
				elif not rangeEmpty:
					# If the remainder of the piece was not empty, not all of the remainder of the piece
					# has been read. If this piece does not end the file or extend into the next file, set
					# the file offset to the end of the current piece.
					file.seek(offsetBefore + bytesToRead)

				piece += 1
			elif pieceOffset > 0:
				# A pieceOffset >0 means the current piece continues from the previous file where
				# it has already been determined that this piece is not empty and can therefore be
				# skipped in this file.
				bytesToSkip = pieceSize - pieceOffset
				if file.tell() + bytesToSkip < fileSize:
					print(bytesToSkip, pieceSize, pieceOffset)
					file.seek(bytesToSkip)
				else:
					pieceOffset = fileSize - file.tell()
					fileIndex += 1
					continue

			# Zero out the pieceOffset
			pieceOffset = 0

			piecesInFile = floor((fileSize - file.tell()) / pieceSize)
			leftoverBytes = (fileSize - file.tell()) - piecesInFile * pieceSize

			offsetBeforePiece = file.tell()
			for filePiece in range(piecesInFile):
				print("Processing piece", piece)

				rangeEmpty = self.isFileRangeEmpty(file, offsetBeforePiece + filePiece * pieceSize, pieceSize)

				if not rangeEmpty:
					havePieces.append(piece)

				piece += 1

			if leftoverBytes > 0:
				leftoverBytesEmpty = self.isFileRangeEmpty(file, fileSize - leftoverBytes, leftoverBytes)

				if leftoverBytesEmpty:
					pieceOffset = -leftoverBytes
				else:
					pieceOffset = leftoverBytes
					havePieces.append(piece)
					piece += 1

			fileIndex += 1

		return havePieces
		# currentPiece = 0
		# for i in range(4):
		# 	piecesInRegion = 0

		# 	while currentPiece < len(have):
		# 		piece = have[currentPiece]

		# 		if piece < i * regionSize or piece > (i + 1) * regionSize:
		# 			break

		# 		currentPiece += 1
		# 		piecesInRegion += 1

		# 	regions[i] = piecesInRegion / regionSize

	def isFileRangeEmpty(self, file, offset, length):
		file.seek(offset)

		nulByte = b'\x00'
		chunkSize = 25600
		# Checking for a whole NUL chunk decreases running time ~30%
		nulChunk = nulByte * chunkSize
		bytesRead = 0

		while length > bytesRead:
			bytesToRead = min(length - bytesRead, chunkSize)
			data = file.read(bytesToRead)
			bytesRead += bytesToRead

			if data == b'':
				break

			if data != nulChunk and data.count(nulByte) != bytesToRead:
				return False

		return True