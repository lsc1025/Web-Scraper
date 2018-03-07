import csv

from scrapers.Normalizer.common.Filenames import get_mappings
from scrapers.Normalizer.common.TypeNormalizers import *
from scrapers.Normalizer.common.TypeValidatorRegexes import *
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.common.Regexes import tld_regex, street_address_regex

require_input_at_no_match = False
report_missed_matches = False
test_uncommon_matches = False
debug_no_match = True

missed_matches_report = {}
no_match_list = []
no_type_of_care_list = []
no_valid_type_of_care_list = {}

common_mismatched_regexes = [phone_with_label_regex, phone_with_label_no_area_code_regex, email_regex, url_regex]
uncommon_mismatched_regexes = [boolean_regex, dollar_amount_regex, for_profit_regex, since_regex, owner_type_regex, rents_regex, percentage_regex, range_of_pricing_regex, po_box_or_apartment_number_regex, postal_code_or_zip_code_regex, province_regex, country_regex]

column_name_to_type = {'row_id': 'empty', 'file': 'str', 'row_ids': 'list_of_str', 'total_count_of_company_name': 'int'}

for mappings_filename in get_mappings():
	csv_reader = csv.reader(open("Normalizer/mappings/" + mappings_filename, 'r'))
	for row in csv_reader:
		if row[0] != "normalized_column_name":
			column_name_to_type[row[0]] = row[2]

#TODO Full Address

type_to_regex_map = {
	'str': [str_regex],
	'int': [int_regex],
	'float': [float_regex],
	'name': [name_regex],
	'boolean': [boolean_regex, int_regex],
	'list_of_str': [list_of_str_regex, str_regex],
	'dollar_amount': [dollar_amount_regex],
	'for_profit_relation': [for_profit_regex],
	'since_type': [since_regex],
	'owner_type_relation': [owner_type_regex],
	'phone_number': [phone_with_label_regex, phone_with_label_no_area_code_regex],
	'email_address': [email_regex],
	'address': [str_regex],
	'url': [url_regex],
	'low_high': [low_high_regex],
	'rents_list': [rents_regex, str_regex],
	'percentage': [percentage_regex],
	'range_of_pricing': [range_of_pricing_regex],
	'type_of_care_relation': [name_regex], 
	'province_relation': [province_regex],
	'po_box_or_apartment_number': [po_box_or_apartment_number_regex, name_regex],
	'postal_code_or_zip_code': [postal_code_or_zip_code_regex, int_regex],
	'country_relation': [country_regex, name_regex],
	'facility_id': [facility_id_regex],
	'empty': [none_regex]
}

rate_regexes = [dollar_amount_regex, float_regex, dollar_amount_plus_regex, rgi_regex, board_package_regex]

column_name_to_regex_map = {
	'name': [name_regex, str_regex],
	'low_rate': rate_regexes,
	'high_rate': rate_regexes,
	'rent_rate': [percentage_regex, based_on_notice_of_assessment_regex, percent_of_regex],
	'postal_code': [postal_code_or_zip_code_regex, int_regex],
	'facility_id': [facility_id_regex, int_regex],
	'row_id': [str_regex],
	'city': [name_regex, city_with_parentheses_regex]
}

def validate_column_entry(filename, column_name, type, data, row_number):
	if data in ["", "Not Specified", "Not specified", 'not specified', "N/A", "N/a", "n/a", "NO DATE PROVIDED", 'under construction', 'none'] and column_name != "row_id": 
		return ""
	elif type == "url":
		if tld_regex.search(data) == None or "@" in data:
			return ""
	
	type_regexes = column_name_to_regex_map.get(column_name) if column_name in column_name_to_regex_map.keys() else type_to_regex_map.get(type)
	match_none_input = "ERROR! Data '" + data + "' of type '" + type + "' in file " + filename + " was found to be invalid. Do you want to stop the program? (y/n)"
	bad_input = "Please input either 'y' or 'n'"

	if type_regexes is None:
		return data

	for regex in type_regexes:
		print("Regexing... '" + data + "' against type '" + type + "' on column_name '" + column_name + "'")
		match = regex.match(data.lower())
		if match != None:
			#print("Normalizing... '" + data + "'")
			normalized_entry = normalize_column_entry(filename, column_name, type, match, data, row_number)
			#print("Got normalized form... '" + str(normalized_entry) + "'")
			if type == "type_of_care_relation" and normalized_entry in ['', None] and data not in ['', None]:
				return None
			else:
				return normalized_entry
		elif regex == type_regexes[-1]: # no match for data
			if require_input_at_no_match:
				response = input(match_none_input)
				while response not in ["y", "n"]:
					response = input(bad_input)
				if response == 'y':
					print("Returned False")
					return False
				else:
					return ""
			if report_missed_matches:
				for regex in (common_mismatched_regexes if not test_uncommon_matches else common_mismatched_regexes + uncommon_mismatched_regexes):
					if regex.match(data):
						if not filename in missed_matches_report:
							missed_matches_report[filename] = 0
						missed_matches_report[filename] += 1
						return None
			if debug_no_match:
				print("Data '" + data + "' of type '" + type + "' in file " + filename + " was found to be invalid")
				joined_data = ",".join([filename, type, data])
				if not joined_data in no_match_list:
					no_match_list.append(joined_data)

none_list = [None, '']

def validate_row(filename, header_row, header_to_index, row, typeofcare_index, row_number):
	new_content_row = [None] * len(row)
	for i in range(len(row)):
		row_item = row[i]
		column_name = header_row[i]
		formatted_item = row_item.strip().replace('\n', ' ')
		is_validated = validate_column_entry(filename, column_name, column_name_to_type[column_name], formatted_item, row_number)
		if is_validated == False:
			return False
		elif isinstance(is_validated, type({})):
			for key in is_validated.keys():
				new_content_row[header_to_index[key]] = is_validated[key]
				print(key + " is now set to " + str(new_content_row[header_to_index[key]]))
		elif new_content_row[i] == None:
			new_content_row[i] = is_validated

	if new_content_row[header_to_index['city']] in none_list:
		return []
	elif new_content_row[typeofcare_index] in [None, '']:
		if row[typeofcare_index] not in [None, '']:
			#print("No VALID type of care on row " + str(row_number) + " in file " + filename)
			invalid_type_of_care = row[typeofcare_index]
			if filename not in no_valid_type_of_care_list.keys():
				no_valid_type_of_care_list[filename] = []
			if invalid_type_of_care not in no_valid_type_of_care_list[filename]:
				no_valid_type_of_care_list[filename].append(invalid_type_of_care)
			return []
		else:
			#print("No GIVEN type of care on row " + str(row_number) + " in file " + filename)
			if filename not in no_type_of_care_list:
				no_type_of_care_list.append(filename)
			return []

	'''
	elif new_content_row[header_to_index['address_line_1']] in [None, '']:
		for i in range(len(new_content_row)):
			if street_address_regex.match(str(new_content_row[i])):
				new_content_row[header_to_index['address_line_1']] = new_content_row[i]
				break
	'''
	return new_content_row

def validate_file(filename):
	typeofcare_index = -1
	row_number = 0

	with open(filename, 'r') as infile:
		reader = csv.reader(infile)
		original_header_row = next(reader)
		header_row = []
		header_to_index = {}
		for i in range(len(original_header_row)):
			row_item = original_header_row[i]
			if row_item == "typeofcare":
				typeofcare_index = i
			header_row.append(row_item)
			header_to_index[row_item] = i
		content_rows = [row for row in reader]

	with open(filename, 'w') as outfile:
		writer = csv.writer(outfile)

		new_rows = [header_row]
		for row in content_rows:
			new_row = validate_row(filename, header_row, header_to_index, row, typeofcare_index, row_number)
			if new_row != []:
				new_rows.append(new_row)
				row_number += 1

		writer.writerows(new_rows)
		return True

def get_report():
	for filename in missed_matches_report.keys():
		print(filename + ": " + str(missed_matches_report[filename]))
	return missed_matches_report

def get_no_match_list():
	for entry in no_match_list:
		print(entry)
	return no_match_list

def get_no_type_of_care_list():
	print()
	print("NO GIVEN TYPE OF CARE LIST:")
	for entry in no_type_of_care_list:
		print(entry)
	return no_type_of_care_list

def get_no_valid_type_of_care_list():
	print()
	print("NO VALID TYPE OF CARE LIST:")
	for key in no_valid_type_of_care_list.keys():
		print(key + ": " + str(no_valid_type_of_care_list[key]))
	return no_valid_type_of_care_list