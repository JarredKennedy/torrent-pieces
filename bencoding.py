MAX_INT_LENGTH = 10

class BencodeNode:
	TYPE_STRING = 1
	TYPE_INT = 2
	TYPE_LIST = 3
	TYPE_DICT = 4

	nodeType = 0
	value = None
	offset = 0
	length = 0
	child = None
	sibling = None

# Decoder for bencoding format used in torrent files.
class Bdecoder:

	def decode(self, file):
		node = None

		token = file.read(1)
		if token == b'i':
			offset = file.tell()
			offsetMax = offset + MAX_INT_LENGTH + 1 # +1 is for the 'e' marking the end of the value
			read = file.read(1)

			node = BencodeNode()
			node.nodeType = BencodeNode.TYPE_INT
			node.offset = offset - 1
			node.value = b''

			if read == b'e': node.value = 0

			while read != '' and read != b'e' and file.tell() <= offsetMax and ((read >= b'0' and read <= b'9') or (len(node.value) == 1 and read == b'-')):
				node.value += read
				read = file.read(1)

			if read == '':
				raise Exception("Invalid integer: found EOF @{}".format(offset))
			elif read != b'e':
				if (read < b'0' or read > b'9'):
					raise Exception("Invalid integer: value at {} does not represent a number @{}".format(file.tell(), offset))
				else:
					raise Exception("Invalid integer: number expression exceeded maximum length of {} @{}".format(MAX_INT_LENGTH, offset))

			# Explicitly check for i-e case and evaluate as 0
			node.value = int(node.value) if node.value != b'-' else 0
			node.length = file.tell() - node.offset
		elif token == b'l':
			node = BencodeNode()
			node.nodeType = BencodeNode.TYPE_LIST
			node.offset = file.tell() - 1
			head = node

			element = self.decode(file)
			while element != None:
				if head == node:
					head.child = element
				else:
					head.sibling = element

				head = element
				element = self.decode(file)
			
			node.length = file.tell() - node.offset
		elif token == b'd':
			offset = file.tell()
			node = BencodeNode()
			node.nodeType = BencodeNode.TYPE_DICT
			node.offset = offset - 1
			head = node

			element = self.decode(file)
			while element != None:
				if element.nodeType != BencodeNode.TYPE_STRING:
					raise Exception("Invalid dictionary key: element at {} is not a string @{}".format(file.tell(), offset))

				if head == node:
					head.child = element
				else:
					head.sibling = element

				# The value at the key is stored as the child of the key string node
				element.child = self.decode(file)

				head = element
				element = self.decode(file)

			node.length = file.tell() - node.offset
		elif (token >= b'0' and token <= b'9'):
			offset = file.tell()
			node = BencodeNode()
			node.nodeType = BencodeNode.TYPE_STRING
			node.offset = offset - 1
			length = token
			read = file.read(1)

			while read >= b'0' and read <= b'9':
				length += read
				read = file.read(1)

			if read == '':
				raise Exception("Invalid string: found EOF @{}".format(offset))
			elif read != b':' and (read < b'0' or read > b'9'):
				raise Exception("Invalid string: value at {} does not represent a number @{}".format(file.tell(), offset))

			length = int(length)
			node.value = file.read(length)

			if len(node.value) != length:
				raise Exception("Invalid string: expected string of length {} @{}".format(length, offset))

			node.length = file.tell() - node.offset

		return node