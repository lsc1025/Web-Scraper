import sys
import os

from subprocess import call
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

path_to_script = sys.argv[0][:-18]
old_dir = os.getcwd()
module_name = "20-LongTermCare"

sys.path.insert(0, os.path.abspath(sys.argv[0][:-len(module_name + ".py")] + "../../../../.."))

from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.MBLongTermCareSpider import MBLongTermCare

path_to_script = sys.argv[0][:-len(module_name + ".py")]
output_filename = path_to_script + "../output/" + module_name + ".csv"

settings = get_project_settings()
settings.set('FEED_FORMAT', 'csv', priority='cmdline')
settings.set('FEED_URI', output_filename, priority='cmdline')

with open(output_filename, 'w') as f:
	f.write('')
	f.close()

process = CrawlerProcess(settings)
process.crawl(MBLongTermCare)
process.start()