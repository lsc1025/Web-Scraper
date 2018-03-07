import csv
import os, sys

name_of_script = "company_name_adder.py"
path_to_script = sys.argv[0][:-len(name_of_script)]
sys.path.insert(0, os.path.abspath(path_to_script + "../.."))

from scrapers.Normalizer.common.TypeValidators import validate_file
from scrapers.Normalizer.common.Filenames import generate_normalized_filename
from scrapers.Normalizer.spreadsheet_generator import get_company_info_from_indices, populate_file_indices, FileIndices

def sanatized():
	return validate_file('company_name_report.csv') == True

def get_unique_identifier(indices, row):
	identifying_attributes = []
	if indices.name_index and row[indices.name_index]:
		identifying_attributes.append(row[indices.name_index])
	if indices.city_index and row[indices.city_index]:
		identifying_attributes.append(row[indices.city_index])
	if indices.phone_index and row[indices.phone_index]:
		identifying_attributes.append(row[indices.phone_index].replace('(', '').replace(')', '').replace(' ', '-'))
	if indices.email_index and row[indices.email_index]:
		identifying_attributes.append(row[indices.email_index])
	if indices.website_index and row[indices.website_index]:
		identifying_attributes.append(row[indices.website_index])

	return ("-".join([attribute.strip() for attribute in identifying_attributes])).upper()

def main():
	if not sanatized():
		return None

	with open('company_name_report.csv', 'r') as f:
		report_rows = [row for row in csv.reader(f)]

	company_name_label = 'company_name'
	report_header_row = report_rows[0]
	report_indices = populate_file_indices(report_header_row)
	filename_index = report_header_row.index('file')

	for i in range(1, len(report_rows)):
		report_row = report_rows[i]

		report_company_name = report_row[0]
		finalized_data_filename = generate_normalized_filename("././" + report_row[filename_index])

		with open(finalized_data_filename, 'r') as f:
			rows = [row for row in csv.reader(f)]

		if company_name_label not in rows[0]:
			rows[0] = rows[0] + [company_name_label]
			for i in range(1, len(rows)):
				rows[i] = rows[i] + [None]

		normalized_header_row = rows[0]
		normalized_indices = populate_file_indices(normalized_header_row)
		report_unique_identifier = get_unique_identifier(report_indices, report_row)

		print()
		print(report_unique_identifier)

		for i in range(1, len(rows)):
			row = rows[i]
			if get_unique_identifier(normalized_indices, row) == report_unique_identifier:
				assert rows[0][-1] == company_name_label
				if rows[i][-1] in [None, '']:
					rows[i][-1] = report_company_name
				print("New Row! " + str(row))
				break

		# Write data
		with open(finalized_data_filename, 'w') as f:
			writer = csv.writer(f)
			writer.writerows(rows)

main()