import os
import hashlib

from bencoding import BencodeNode

class TorrentList:

	directories = []
	torrentReader = None

	# Dictionary mapping a torrent hash to a dictionary representing a torrent
	torrents = {}

	def __init__(self, torrentReader, directories):
		self.torrentReader = torrentReader
		self.directories = directories

	def findTorrents(self):
		for directory in self.directories:
			for fileName in os.listdir(directory):
				torrent = self.torrentReader.readFile(directory + fileName)

				if (type(torrent) == dict):
					self.torrents[torrent['hash']] = torrent



class TorrentReader:

	decoder = None

	def __init__(self, decoder):
		self.decoder = decoder

	def readFile(self, filePath):
		file = open(filePath, 'rb')
		tree = self.decoder.decode(file)
		
		if type(tree) != BencodeNode:
			raise Exception("Expected BencodeNode got {}".format(type(tree)))

		torrent = self.treeToTorrent(tree, file)

		return torrent

	def treeToTorrent(self, tree, file):
		torrent = {}

		# The child of the root is the first of the top-level dictionary keys (announce, info)
		infoNode = self.pluckNode(tree, b'info')

		if infoNode == None:
			raise Exception("Could not find info node")

		file.seek(infoNode.offset)
		torrent['hash'] = hashlib.sha1(file.read(infoNode.length)).hexdigest()

		torrent['name'] = (self.pluckNode(infoNode, b'name')).value.decode('utf-8')
		torrent['piece_size'] = (self.pluckNode(infoNode, b'piece length')).value
		# 'pieces' is a binary string of concatenated piece hashes. Each hash is 20 bytes.
		torrent['piece_count'] = int(len((self.pluckNode(infoNode, b'pieces')).value) / 20)

		torrent['files'] = []
		fileListNode = self.pluckNode(infoNode, b'files')

		fileNode = fileListNode.child
		while fileNode != None:
			filePaths = self.treeToList(self.pluckNode(fileNode, b'path'))
			filePaths = list(map(lambda path: path.decode('utf-8'), filePaths))
			fileSize = (self.pluckNode(fileNode, b'length')).value
			
			torrent['files'].append((filePaths, fileSize))

			fileNode = fileNode.sibling

		return torrent

	def pluckNode(self, tree, nodePath):
		node = tree

		keys = nodePath.split(b'.')
		matchKey = 0

		while node != None:
			if node.nodeType == BencodeNode.TYPE_DICT:
				node = node.child
				continue
			elif node.nodeType == BencodeNode.TYPE_STRING and node.value == keys[matchKey]:
				if matchKey == len(keys) - 1:
					return node.child
				else:
					matchKey += 1
					node = node.child
					continue

			node = node.sibling

		return None

	def treeToList(self, listNode):
		listValue = []

		if listNode.nodeType == BencodeNode.TYPE_LIST:
			node = listNode.child
			while node != None:
				listValue.append(node.value)
				node = node.sibling

		return listValue