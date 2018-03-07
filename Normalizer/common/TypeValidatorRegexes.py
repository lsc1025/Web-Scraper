from re import compile

from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.common.Provinces import states_and_provinces_lower
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.common.Regexes import phone_number_no_area_code_regex_expr, phone_number_regex_expr, street_address_regex, po_box_regex_expr, postal_code_regex_expr, unit_regex_expr, email_regex, unit_street_regex, url_regex, address_regex

def expr_list_of_options(list_of_options):
	return '(' + '|'.join(list_of_options) + ')'

def compile_list_of_options(list_of_options):
	return compile(expr_list_of_options(list_of_options))


# BASIC TYPES
none_regex = compile('^$')
str_regex = compile('.+')
int_regex = compile('\d+')
float_regex = compile('-?\d+\.?\d*')
name_regex = compile('^((\D|\d)+(-|&|,|\'|\"| )*)+$')
boolean_regex = compile('^' + expr_list_of_options(["true", "false", "yes", "no", "1", "0"]) + '$')
list_of_str_regex = compile("(.+;?)+")

dollar_amount_regex_expr = "\$?(\d|,)+(\.\d{2})?"
dollar_amount_regex = compile(dollar_amount_regex_expr)

percentage_regex_expr = "\d+(-\d+)?%"


# COST-RELATED TYPES
for_profit_regex = compile_list_of_options(['public not-for-profit', 'private for-profit', 'private not-for-profit'])
since_regex = compile('(Since|since)? ?\d{2}/\d{2}/\d{4}')
owner_type_regex = compile_list_of_options(['individual', 'organization'])

low_high_regex = compile("(\d|,)+/(\d|,)+")

rents_regex_expr = ("((Bachelor/Studio|(One|Two|Three) Bedroom) - " + dollar_amount_regex_expr + "( \+ )?(up )?(\d+ sq/ft)?(\(Co-op shares " + dollar_amount_regex_expr + "\))?;?)+").lower()
rents_regex = compile(rents_regex_expr)
percentage_regex = compile(percentage_regex_expr)
range_of_pricing_regex = compile(dollar_amount_regex_expr + " (to " + dollar_amount_regex_expr + "|and up)")


# ADDRESS COMPONENT TYPES
apartment_number_regex_expr = '(Suite|Apartment|Apt|STE|#):? ?\d+'.lower()
apartment_number_regex = compile(apartment_number_regex_expr)
c_o_title_regex_expr = "C/O (\D+ ?)+"
c_o_title_regex = compile(c_o_title_regex_expr)

po_box_or_apartment_number_regex = compile_list_of_options([po_box_regex_expr, unit_regex_expr, apartment_number_regex_expr, c_o_title_regex_expr])
postal_code_or_zip_code_regex = compile_list_of_options([postal_code_regex_expr,'\d{5}'])

province_regex = compile_list_of_options(states_and_provinces_lower())
country_regex = compile_list_of_options(['canada', 'can', 'usa', 'us'])

corner_regex = compile("\D+ & \D+(\.| )?")
address_line_1_regex = compile("(\D+ \d+)")


# PHONE REGEX
phone_label_regex_expr = "(?:(?:Phone|Ph|FAX)(?::|\.)* *)?".lower()
phone_with_label_regex = compile(phone_label_regex_expr + phone_number_regex_expr)
phone_with_label_no_area_code_regex = compile(phone_label_regex_expr + phone_number_no_area_code_regex_expr)


# CUSTOM REGEX
dollar_amount_plus_regex = compile(dollar_amount_regex_expr + " .+")
rgi_regex = compile("RGI".lower())
based_on_notice_of_assessment_regex = compile("based on Notice of Assessment".lower())
board_package_regex = compile(("Board Package plus " + percentage_regex_expr + " .+").lower())

percent_of_regex = compile("\d+ percent of .+")

cost_regex_exprs = ["market rate", "safer", ".+: " + percentage_regex_expr + " of net income",
	percentage_regex_expr + " of net income",
	".+: approx\. \$" + dollar_amount_regex_expr + "(-" + dollar_amount_regex_expr + ")?/month)+"]

facility_id_regex = compile("AF\d{4}(A|B|C)")

roman_number_regex_options = expr_list_of_options(["I", "V", "X", "i", "v", "x"]) # C is excluded -- don't think we'll see anything that high
roman_number_regex = compile("^" + roman_number_regex_options + "{1,4}" + "$") # restrictions apply because, again, we shouldn't get very many high numbers in roman numerals

city_with_parentheses_regex = compile('^.+ \(\d+\)$')