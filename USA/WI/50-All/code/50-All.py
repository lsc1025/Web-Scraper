import re
import csv
import os, sys

from selenium import webdriver
from selenium import common
from bs4 import BeautifulSoup

module_name = "50-All"
sys.path.insert(0, os.path.abspath(sys.argv[0][:-len(module_name + ".py")] + "../../../../.."))

name_and_type_regex = re.compile('(.+) \((.+)\)')
contact_label = "Contact Name: "
phone_label = "Telephone Number: "

from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.common.GenericOutput import get_blank_information
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.common.Parsers import parse_city_province_zip_code

class DQAScraper():
    def __init__(self):
        self.web_driver = webdriver.PhantomJS()
        self.url = 'https://www.forwardhealth.wi.gov/WIPortal/subsystem/public/DQAProviderSearch.aspx'
        self.results = []  

    def screenshot(self):
        file_path = sys.argv[0][:-len(module_name + ".py")] + '../input/screenshot.png'
        self.web_driver.get_screenshot_as_file(file_path)

    def scrape(self):
        self.web_driver.get(self.url)
        csv_output = open(sys.argv[0][:-len(module_name + ".py")] + '../output/50-All.csv', 'w')
        csv_writer = csv.writer(csv_output)

        print("Got URL")

        county_selection = self.web_driver.find_element_by_xpath('//select[@id="MainContent_GenericPageCtrl1_ctl02_CriteriaPanel_County_0"]')
        county_options_len = len(county_selection.find_elements_by_tag_name("option"))

        self.screenshot()
        csv_writer.writerow(get_blank_information().keys())

        for i in range(69, county_options_len):
            option = county_selection.find_elements_by_tag_name("option")[i]
            county = option.text

            print("Entering county " + county + "...")

            option.click()
            self.screenshot()

            residential_care_clickbox = self.web_driver.find_element_by_xpath('//input[@id="MainContent_GenericPageCtrl1_ctl02_CriteriaPanel_IndAllResidentialCare_0"]')
            residential_care_clickbox.click()
            self.screenshot()

            search_button = self.web_driver.find_element_by_xpath('//input[@id="ctl00_MainContent_GenericPageCtrl1_ctl02_CriteriaPanel_ctl03_ctl00_SearchButton_input"]')

            search_button.click()
            self.screenshot()

            try:
                error_element = self.web_driver.find_element_by_xpath("//tr[@class='Message ErrorMessage']/td[@class='MessageText']")
                print("Got error text: " + error_element.text)

                if error_element.text == "At a minimum, one Provider/Facility Type is required.":
                    residential_care_clickbox = self.web_driver.find_element_by_xpath('//input[@id="MainContent_GenericPageCtrl1_ctl02_CriteriaPanel_IndAllResidentialCare_0"]')
                    residential_care_clickbox.click()
                    self.screenshot()

                    search_button = self.web_driver.find_element_by_xpath('//input[@id="ctl00_MainContent_GenericPageCtrl1_ctl02_CriteriaPanel_ctl03_ctl00_SearchButton_input"]')
                    search_button.click()
                    self.screenshot()

                assert error_element.text == "No records were found for your search criteria."
            except:
                county_results = self.scrape_search_results(county)
                self.results.append(county_results)
                for result in county_results:
                    csv_writer.writerow([result[key] for key in result.keys()])

            county_selection = self.web_driver.find_element_by_xpath('//select[@id="MainContent_GenericPageCtrl1_ctl02_CriteriaPanel_County_0"]')

        print(self.results)


    def scrape_search_results(self, county):
        self.screenshot()
        residence_links = self.web_driver.find_elements_by_xpath("//table[@id='MainContent_GenericPageCtrl1_ctl05_Datalist']//tr/td/table//tr/td/a")
        pagination_links = self.web_driver.find_elements_by_xpath("//tr[@class='iC_DataListPager']/td/a")
        search_results_len = len(residence_links) - len(pagination_links)
        scraping_results = []

        for i in range(search_results_len):
            link = self.web_driver.find_elements_by_xpath("//table[@id='MainContent_GenericPageCtrl1_ctl05_Datalist']//tr/td/table//tr/td/a")[i]
            link.click()
            self.screenshot()
            scraping_results.append(self.scrape_facility_page(county))

        self.screenshot()

        pagination_links = self.web_driver.find_elements_by_xpath("//tr[@class='iC_DataListPager']/td/a")
        if len(pagination_links) > 0 and pagination_links[-1].text == "Next":
            pagination_links[-1].click()
            self.screenshot()
            scraping_results = scraping_results + self.scrape_search_results(county)
        else:
            perform_new_search_button = self.web_driver.find_element_by_xpath("//a[@id='MainContent_GenericPageCtrl1_ctl05_LinkNewSearch']")
            perform_new_search_button.click()
            self.screenshot()

        return scraping_results


    def scrape_facility_page(self, county):
        self.screenshot()

        info = get_blank_information()
        info["country"] = "USA"
        info["county"] = county

        contact_info_text = self.web_driver.find_element_by_xpath("//div[@id='MainContent_GenericPageCtrl1_DivProviderContactInformation']").text.split('\n')
        additional_provider_info_text = [element.text for element in self.web_driver.find_elements_by_xpath("//td[@class='wpiCellValueView']")]

        if len(contact_info_text) > 0:
            name_and_type_match = name_and_type_regex.search(contact_info_text[0])
            info["name"] = name_and_type_match.group(1)
            info["facility_type"] = name_and_type_match.group(2)

        if len(contact_info_text) > 1:
            info["street_address"] = contact_info_text[1]

        if len(contact_info_text) > 2:
            info = {**info, **parse_city_province_zip_code(contact_info_text[2], province_required=True)}

        if len(contact_info_text) > 6:
            info["contact"] = contact_info_text[6][len(contact_label):]
        
        if len(contact_info_text) > 7:
            info["phone"] = contact_info_text[7][len(phone_label):]

        if len(additional_provider_info_text) > 0:
            info["licensure_status"] = additional_provider_info_text[0]

        if len(additional_provider_info_text) > 1:
            info["ownership_type"] = additional_provider_info_text[1]

        if len(additional_provider_info_text) > 2:
            info["owner"] = additional_provider_info_text[2]

        if len(additional_provider_info_text) > 3:
            info["number_of_beds"] = additional_provider_info_text[3]

        if len(additional_provider_info_text) > 4:
            info["specialty_programs"] = additional_provider_info_text[4].replace(',', ';')

        info["source"] = self.web_driver.current_url

        back_to_search_results_element = self.web_driver.find_element_by_xpath("//a[@id='MainContent_GenericPageCtrl1_LinkReturnToSearchTop']")
        back_to_search_results_element.click()
        self.screenshot()

        return info


DQAScraper().scrape()