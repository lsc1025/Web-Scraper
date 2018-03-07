# Custom exception used to standardize debug
class NormalizationException(Exception):
	def __init__(self, filename, cause):
		self.filename = filename
		self.cause = cause
	def __str__(self):
		return "column_normalizer.py: Error normalizing " + self.filename + " for the reason of " + str(self.cause)