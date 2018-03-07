from subprocess import call
import sys
import os

path_to_script = sys.argv[0][:-18]
old_dir = os.getcwd()

os.chdir(path_to_script + "../../../../pqcq_scrapy")
call(["scrapy", "crawl", "13-NursingHomes", "-o", "../" + path_to_script + "../output/13-NursingHomes.csv"])
os.chdir(old_dir)
