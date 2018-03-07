import re
import csv
import glob
import os, sys

name_of_script = "spreadsheet_generator.py"
path_to_script = sys.argv[0][:-len(name_of_script)]
sys.path.insert(0, os.path.abspath(path_to_script + "../.."))

none_array = [None, '']

class FileIndices:
	def __init__(self, company_name_index, name_index, phone_index, address_line_1_index, city_index, province_index, country_index, email_index, website_index, row_id_index = 0):
		self.company_name_index = company_name_index
		self.name_index = name_index
		self.phone_index = phone_index
		self.address_line_1_index = address_line_1_index
		self.city_index = city_index
		self.province_index = province_index
		self.country_index = country_index
		self.email_index = email_index
		self.website_index = website_index
		self.row_id_index = row_id_index

class CompanyInfo:
	def __init__(self, company_name, name, phone, address_line_1, city, province, country, email, website, file, row_id):
		self.company_name = company_name
		self.name = name
		self.phone = phone
		self.address_line_1 = address_line_1
		self.city = city
		self.province = province
		self.country = country
		self.email = email
		self.website = website
		self.file = file
		self.row_id = row_id

def get_value_or_none(index, row):
	if index not in none_array and len(row) > index and row[index] not in none_array:
		return row[index]
	else:
		return None

def get_company_info_from_indices(file_indices, row):
	return CompanyInfo(get_value_or_none(file_indices.company_name_index, row),
		get_value_or_none(file_indices.name_index, row),
		get_value_or_none(file_indices.phone_index, row),
		get_value_or_none(file_indices.address_line_1_index, row),
		get_value_or_none(file_indices.city_index, row),
		get_value_or_none(file_indices.province_index, row),
		get_value_or_none(file_indices.country_index, row),
		get_value_or_none(file_indices.email_index, row),
		get_value_or_none(file_indices.website_index, row),
		None,
		get_value_or_none(file_indices.row_id_index, row))

def get_all_filenames():
	canada_original_csv_filenames = "Canada/*/*/output/*.csv"
	usa_original_csv_filenames = "USA/*/*/output/*.csv"
	all_filenames = glob.glob(canada_original_csv_filenames) + glob.glob(usa_original_csv_filenames)

	filename_blacklist = glob.glob("USA/National/42-NursingHomes/output/*")

	all_filenames = [filename for filename in all_filenames if filename not in filename_blacklist]
	return all_filenames

company_name_cache = {}
company_name_rows = {}

bad_company_names = re.compile("(\d+/\d+/\d+|CANADA-QC-18-ASSISTEDLIVING\(ASSOC\)-OUTPUT-\d+)")

print_company_name_rows = True

def parse_labels_into_list(label_str):
	return label_str.split('; ')

def fix_header_row(header_row):
	return [entry.strip().replace(' ', '_').upper() for entry in header_row]

def get_index_or_none(header_row, labels):
	for i in range(len(header_row)):
		header_row_item = header_row[i]
		if header_row_item in labels:
			return i
	return None

def populate_file_indices(header_row):
	company_name_labels = ['COMPANY_NAME_/_NAME_OF_OPERATORS', 'LEGAL_BUSINESS_NAME', 'CORPORATE_NAME', 'LICENSEE', 'OWNCOMP', 'COMPANY_NAME']
	name_labels = parse_labels_into_list('CURRENT_FACILITY_NAME; FACILITY_NAME; LEGALNAME; NAME; NAME_OF_FACILITY; NAME_OF_HOME; RESPITE_PROVIDER_NAME; SHORT_NAME; SORT_NAM')
	phone_labels = parse_labels_into_list('CONTACT_PHONE; FACILITY_PHONE; FACILITY_TELEPHONE_NUMBER; PHONE; PHONE1; PRIMARY_PHONE; PROVIDER_PHONE_NUMBER; SITE_PHONE; TELEPHONE; WEBSITE_PHONE_#')
	address_line_1_labels = parse_labels_into_list('ADDRESS; ADDRESS_1; ADDRESS_LINE_1; ADDRESS_LINE1; ADDRESS1; FACILITY_ADDRESS; LOCATION; PHYSICAL_ADDRESS; STREET; STREET_ADDRESS')
	city_labels = parse_labels_into_list('CITY; FAC_CITY; FACILITY_CITY; P_CITY; STREET_CITY; MUNICIPALITY')
	province_lables = parse_labels_into_list('FACILITY_STATE; PROVINCE; STATE; STREET_STATE')
	country_labels = parse_labels_into_list('COUNTRY')
	email_labels = parse_labels_into_list('EMAIL; EMAIL_ADDRESS; FACILITY_EMAIL; SITE_EMAIL')
	website_labels = parse_labels_into_list('LINK; SITE_WEBSITE; WEB; WEB_ADDRESS; WEBSITE')
	row_id_labels = ['ROW_ID']

	header_row = fix_header_row(header_row)
	'''
	print("Got index of " + str(get_index_or_none(header_row, name_labels)) + " for name column")
	print("Header Row: " + str(header_row))
	'''
	return FileIndices(get_index_or_none(header_row, company_name_labels),
		get_index_or_none(header_row, name_labels),
		get_index_or_none(header_row, phone_labels),
		get_index_or_none(header_row, address_line_1_labels),
		get_index_or_none(header_row, city_labels),
		get_index_or_none(header_row, province_lables),
		get_index_or_none(header_row, country_labels),
		get_index_or_none(header_row, email_labels),
		get_index_or_none(header_row, website_labels),
		get_index_or_none(header_row, row_id_labels))	

def populate_cache():
	total = 0

	for filename in get_all_filenames():
		with open(filename, 'r') as f:
			rows = [row for row in csv.reader(f)]
		#print(filename)
		company_name_labels = ['COMPANY_NAME_/_NAME_OF_OPERATORS', 'LEGAL_BUSINESS_NAME', 'CORPORATE_NAME', 'LICENSEE', 'OWNCOMP', 'COMPANY_NAME']

		header_row = [entry.strip().replace(' ', '_').upper() for entry in rows[0]]
		company_name_index = -1

		file_indices = populate_file_indices(rows[0])
		company_name_index = file_indices.company_name_index

		if company_name_index != None:
			local_total = 0
			
			for i in range(1, len(rows)):
				if len(rows[i]) > company_name_index:
					row_id = rows[i][0]
					company_name = rows[i][company_name_index]
					corrected_company = company_name.upper().strip()
					if corrected_company not in none_array and not bad_company_names.match(corrected_company):
						local_total += 1
						if corrected_company not in company_name_cache:
							company_name_cache[corrected_company] = 0
							company_name_rows[corrected_company] = []
						company_name_cache[corrected_company] += 1
						company_name_rows[corrected_company].append(get_company_info_from_indices(file_indices, rows[i]))
						company_name_rows[corrected_company][-1].file = filename
			
			total += local_total

	return company_name_rows if print_company_name_rows else company_name_cache

def join_mapped_iterable(lambda_function, iterable):
	return "; ".join([item for item in map(lambda_function, iterable) if item != "None"])

def get_mapped_iterable(lambda_function, iterable):
	return [item for item in map(lambda_function, iterable)]

def get_csv_line(list_of_items):
	return [(str(item) if item else "") for item in list_of_items]

def generate_spreadsheet():
	if not print_company_name_rows:
		print("company_name,total_count_of_company_name")

		names = [str(company_name_cache[name]) + "-" + name for name in company_name_cache]
		names.sort()
		names.sort(key=lambda name: 10000 - int(name.split('-')[0]))

		for name in names:
			actual_name = "-".join(name.split('-')[1:])
			print("\"" + actual_name + "\"" + "," + str(company_name_cache[actual_name]))

		print("ALL_COMPANIES_TOTAL," + str(total))
	else:
		rows = []
		rows.append("company_name,name,primary_phone,address_line_1,city,province,country,email,website,file,row_ids,total_count_of_company_name".split(','))
		for name in company_name_rows:
			number_of_occurances = len(company_name_rows[name])
			if number_of_occurances > 2:
				for i in range(number_of_occurances):
					rows.append(get_csv_line([name,
						get_mapped_iterable(lambda info: info.name, company_name_rows[name])[i],
						get_mapped_iterable(lambda info: info.phone, company_name_rows[name])[i],
						get_mapped_iterable(lambda info: info.address_line_1, company_name_rows[name])[i],
						get_mapped_iterable(lambda info: info.city, company_name_rows[name])[i],
						get_mapped_iterable(lambda info: info.province, company_name_rows[name])[i],
						get_mapped_iterable(lambda info: info.country, company_name_rows[name])[i],
						get_mapped_iterable(lambda info: info.email, company_name_rows[name])[i],
						get_mapped_iterable(lambda info: info.website, company_name_rows[name])[i],
						get_mapped_iterable(lambda info: info.file, company_name_rows[name])[i],
						get_mapped_iterable(lambda info: info.row_id, company_name_rows[name])[i],
						number_of_occurances]))

		with open('company_name_report.csv', 'w') as f:
			csv.writer(f).writerows(rows)

populate_cache()
generate_spreadsheet()
