import argparse
import time

from parser import Parser

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process log file.')
    parser.add_argument('log_file', type=str, help='The path to the log file')

    args = parser.parse_args()

    start = time.time()
    parser = Parser()

    LOG_FILE = args.log_file

    EXCEL_FILE = 'access.log.xlsx'

    try:
        data = parser.read_parse_file(LOG_FILE)
    except Exception as e:
        print(f"An error occurred while reading and parsing the file: {e}")
        exit(1)

    parser.save_file(data)

    end = time.time()

    time_elapsed = time.strftime('%H:%M:%S', time.gmtime(end - start))
    print(f"Execution time: {time_elapsed}")

    parser.open_file(EXCEL_FILE)
