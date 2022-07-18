class DownloadFinder:

	def __init__(self, downloadDirectories):
		self.downloadDirectories = downloadDirectories

	def printDirectories(self):
		print(', '.join(self.downloadDirectories))