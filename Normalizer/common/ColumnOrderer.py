import csv
import os

from scrapers.Normalizer.common.Filenames import get_mappings
from scrapers.Normalizer.common.ColumnMigrator import apply_migrations_to_rows, get_fieldname_blacklist

fieldnames = ['row_id']
included_columns = []
types_of_care = {}

DEBUG = False
DEBUG_FILENAME = ""
DEBUG_ROWS = 10

for mappings_filename in get_mappings():
	csv_reader = csv.reader(open("Normalizer/mappings/" + mappings_filename, 'r'))
	for row in csv_reader:
		if row[0] != "normalized_column_name":
			fieldnames.append(row[0])
			for row_item in row[3].split(';'):
				included_columns.append(row_item.strip())

whitelist = [
	'row_id',
	'name',
	'typeofcare',
	'description',
	'primary_phone',
	'primary_phone_extension',
	'secondary_phone',
	'secondary_phone_extension',
	'fax',
	'email',
	'website',
	'low_rate',
	'address_line_1',
	'address_line_2',
	'neighborhood',
	'latitude',
	'longitude',
	'city',
	'province',
	'postal_code',
	'country'
]

def test():
	fieldnames = ['A', 'C', 'D', 'B']
	filter_csv('file.csv', fieldnames=fieldnames)
	order_csv('file.csv', fieldnames=fieldnames)

def filter_csv(filename, whitelist=whitelist):
	filtered_indices = []
	rows = []
	typeofcare_indices = []

	with open(filename, 'r') as infile:
		lines = infile.readlines()
		header = lines[0].replace('\n', '').split(',')
		for i in range(len(header)):
			header_item = header[i]
			if header_item in whitelist:
				filtered_indices.append(i)
				if header_item == "typeofcare":
					typeofcare_indices.append(i)

	with open(filename, 'r') as infile:
		csv_reader = csv.reader(infile)

		if DEBUG and (filename == DEBUG_FILENAME or DEBUG_FILENAME == ""):
			print()
			print("SAMPLE OF ROWS EXCLUDED IN ORDER OPERATION on " + filename + ":")

		debug_rows_count = 0

		for row in csv_reader:
			new_row = ['row_id']
			for i in filtered_indices:
				if i < len(row):
					new_row.append(row[i])
					if DEBUG:
						print("Filtered Indices: " + str(filtered_indices))
						print("appending... " + str(row[i]) + " from filtered index " + str(i))
			
			rows.append(new_row)

			for i in range(len(row)):
				if i in typeofcare_indices and row[i] != "" and row[i] != "typeofcare":
					if not row[i] in types_of_care.keys():
						types_of_care[row[i]] = []
					if not filename[14:] in types_of_care[row[i]]:
						types_of_care[row[i]].append(filename[14:])

			if DEBUG and (filename == DEBUG_FILENAME or DEBUG_FILENAME == "") and debug_rows_count < DEBUG_ROWS:
				print(",".join([row[i] for i in range(len(row)) if not i in filtered_indices]))
				debug_rows_count += 1

	with open(filename, 'w') as outfile:
		writer = csv.writer(outfile)
		for row in rows:
			writer.writerow(row)

def order_csv(filename, fieldnames=fieldnames):
	with open(filename, 'r') as infile:
		dict_rows = [row for row in csv.DictReader(infile)]

	with open(filename, 'w') as outfile:
		writer = csv.DictWriter(outfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(dict_rows)

def filter_and_order_csv(input_filename, output_filename, rows, fieldnames=fieldnames):
	apply_migrations_to_rows(input_filename, output_filename, rows)
	if os.path.isfile(output_filename):
		filter_csv(output_filename, whitelist=whitelist)
		order_csv(output_filename, fieldnames=whitelist)

def get_included_columns():
	for column in included_columns:
		print(column)
	print(included_columns)
	return included_columns

def get_fieldnames():
	for name in fieldnames:
		print('"' + name + '",')
	print(fieldnames)
	return fieldnames

def get_types_of_care():
	print(types_of_care)
	for key in types_of_care.keys():
		print("\t" + key + ": " + str(types_of_care[key]))
	return types_of_care