import argparse
import os
import time

import settings
from parser.log_parser import Parser

if __name__ == '__main__':
    start = time.time()

    if not os.path.exists(settings.OUTPUT_DIR):
        os.makedirs(settings.OUTPUT_DIR)

    arg_parser = argparse.ArgumentParser(description='Process log file.')
    arg_parser.add_argument('log_file', type=str, help='The path to the log file')
    arg_parser.add_argument('website_url', nargs='?', type=str, help='The path to the log file')
    args = arg_parser.parse_args()

    parser = Parser()

    try:
        data = parser.read_parse_file(args.log_file, args.website_url)
    except Exception as e:
        print(f"An error occurred while reading and parsing the file: {e}")
        exit(1)

    parser.save_file(data)

    end = time.time()

    time_elapsed = time.strftime('%H:%M:%S', time.gmtime(end - start))
    print(f"Execution time: {time_elapsed}")

    parser.open_file(settings.EXCEL_FILE)
