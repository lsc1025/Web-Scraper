import re

from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.common.Regexes import comma_or_period_required_regex, email_regex
from scrapers.Normalizer.common.TypesOfCare import get_types_of_care
from scrapers.Normalizer.common.TypeValidatorRegexes import dollar_amount_regex, roman_number_regex, city_with_parentheses_regex

def normalize_column_entry(filename, column_name, type, match, data, row_number):
	assert match != None

	def return_extension_map(phone_number, extension_number):
		return {column_name: phone_number, column_name + '_extension': extension_number}

	if column_name == "city" and city_with_parentheses_regex.match(data):
		space_split = data.split(' ')[:-1]
		return " ".join(space_split)
	elif type in ["name", 'for_profit_relation']:
		result = []

		data = re.compile("(í©|ì©|ã©)").sub("é", data.lower())
		data = data.replace("‰ûò", " ")
		data = re.compile("ì»").sub("ê", data)
		data = data.replace("”ûä", "")
		data = re.compile("(‰ûª|äó»)").sub("'", data)
		data_parts = data.split(" ")
		for i in range(len(data_parts)):
			part = data_parts[i]
			if roman_number_regex.match(part):
				result.append(part.upper())
			else:
				result.append(part.capitalize())

		final_result = " ".join(result)

		if len(final_result.encode()) != len(final_result):
			print("UTF-8 Problems on " + final_result)

		return final_result
	elif type == "boolean":
		return 'FALSE' if data.lower() in ['false', 'no', '0'] else 'TRUE'
	elif type == 'dollar_amount':
		return '$' + data if data[0] != '$' and dollar_amount_regex.match(data) else data
	elif type == 'phone_number':
		result = None

		if len(match.groups()) == 5:
			assert match.group(2) != None
			assert match.group(3) != None
			assert match.group(4) != None

			result = '(' + match.group(2) + ') ' + match.group(3) + ' ' + match.group(4)
			if match.group(1) != None:
				result = '+' + match.group(1) + " " + result
			if match.group(5) != None:
				result = return_extension_map(result, match.group(5))
		elif len(match.groups()) == 3:
			assert match.group(1) != None
			assert match.group(2) != None

			result = match.group(1) + ' ' + match.group(2)
			if match.group(3) != None:
				result = return_extension_map(result, match.group(3))

		return result 
	elif type == 'url':
		assert match.group(2) != None
		assert match.group(3) != None

		top_level_domain = {
			"cm": "com",
			"ort": "org",
			"rog": "org",
			"workpress": "wordpress"
		}.get(match.group(3), match.group(3))

		result = comma_or_period_required_regex.sub('.', match.group(2)) + '.' + top_level_domain
		if match.group(1) != None:
			if match.group(1)[-3:] == "www":
				result = match.group(1) + '.' + result
			else:
				result = match.group(1) + result
		if match.group(4) != None:
			result = result + '/' + match.group(4)
		return result
	elif type == "postal_code_or_zip_code":
		return ('0' * (5 - len(data))) + data if len(data) < 5 else data
	elif type == 'province_relation':
		return data.upper() if data != 'Louisiana' else data
	elif type == 'type_of_care_relation':
		return get_types_of_care(data.split(';'))
	elif type == "email_address":
		emails = []
		split_by_space = data.split(' ')
		for item in split_by_space:
			if email_regex.match(item):
				emails.append(item)
		return ';'.join(emails)
	else: # int, float, list_of_str, country_relation, address
		return data