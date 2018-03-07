import re
import csv
import glob

from scrapers.Normalizer.common.NormalizationException import NormalizationException
from scrapers.Normalizer.common.Filenames import get_mappings

debug_filename = ""
column_header_mapping = {}

undesireable_characters_regex = re.compile(r"(\ufeff|\n)")

for mappings_filename in get_mappings():
	csv_reader = csv.reader(open("Normalizer/mappings/" + mappings_filename, 'r'))
	for row in csv_reader:
		column_header_mapping[row[0]] = [item.strip() for item in row[3].split(';')]

# Function for returning the transformed version of a column_header
def transform_column_header(filename, column_header):
	header_to_test = undesireable_characters_regex.sub('', column_header.strip().upper().replace(' ', '_').replace('"', ''))
	for transformed_value, possible_values in column_header_mapping.items():
		if header_to_test in possible_values:
			if filename == debug_filename:
				print("Found value! Returned: " + transformed_value)
			return transformed_value
	if filename == debug_filename:
		print("Returned " + header_to_test.lower())
	return header_to_test.lower()

# Function for returning transformed column header list
def transform_column_line(filename, list_of_column_headers):
	assert len(list_of_column_headers) > 0
	transformed_column_line = []
	for column_header in list_of_column_headers:
		transformed_column_header = transform_column_header(filename, column_header)
		if filename == debug_filename:
			print("Old: " + column_header + ", new: " + transformed_column_header)
		if transformed_column_header != "" and transformed_column_header in transformed_column_line:
			if transformed_column_header == "typeofcare":
				print("Needed a new type of care! On " + filename)
				transformed_column_line.append("typeofcare2")
			elif transformed_column_header == "address_line_1":
				print("Check for duplicates on " + filename)
				transformed_column_line.append("location")
			else:
				raise NormalizationException(filename, "DUPLICATE ON " + str(transformed_column_line) + " with DUPLICATE HEADER " + transformed_column_header)
		else:
			transformed_column_line.append(transformed_column_header)
	if filename == debug_filename:
		print("Returned " + str(transformed_column_line))
	return transformed_column_line