from subprocess import call
import sys
import os

path_to_script = sys.argv[0][:-8]
old_dir = os.getcwd()

os.chdir(path_to_script + "../../../../pqcq_scrapy")
call(["scrapy", "crawl", "6-PEI", "-o", "../" + path_to_script + "../output/6-PEI.csv"])
os.chdir(old_dir)