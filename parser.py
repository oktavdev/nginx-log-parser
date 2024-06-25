import json
import os
import platform
import re
import shelve
import shlex
import subprocess
from typing import Dict

import pandas as pd


class Parser:
    IP = 0
    TIME = 3
    TIME_ZONE = 4
    REQUESTED_URL = 5
    STATUS_CODE = 6
    USER_AGENT = 9

    def read_parse_file(self, file_name: str) -> Dict[str, pd.DataFrame]:

        file_time = os.path.getmtime(file_name)

        previous_time = self.get_save_previous_time(file_time)

        if file_time != previous_time or not os.path.isfile('shelve.db'):
            with open(file_name, "r") as f:
                print('Reading file...')
                log_entries = [self.parse_line(line) for line in f]

            with shelve.open('shelve.db', flag='c', protocol=None, writeback=False) as db:
                db['log_entries'] = log_entries

        with shelve.open('shelve.db', flag='c', protocol=None, writeback=False) as db:
            logs_df = pd.DataFrame(db['log_entries'])

        pivot_user_agents = logs_df.pivot_table(
            index=['user_agent'],
            values=['requested_url'],
            aggfunc='count'
        ).sort_values(by='requested_url', ascending=False)

        pivot_status_codes = logs_df.pivot_table(
            index=['status_code'],
            values=['requested_url'],
            aggfunc='count'
        ).sort_values(by='requested_url', ascending=False)

        error_urls_df = logs_df[logs_df['status_code'].str.startswith(('4', '5'))]
        return {

            'User agents': pivot_user_agents,
            'Status codes': pivot_status_codes,
            # 'Data': logs_df,
            'Errors': error_urls_df,
        }

    @staticmethod
    def get_save_previous_time(file_time):

        previous_time_file = 'file_modification.json'

        if not os.path.isfile(previous_time_file):
            with open(previous_time_file, 'w') as file:
                json.dump({'modification_time': file_time}, file)

        if os.path.isfile(previous_time_file):
            with open(previous_time_file, 'r') as file:
                data = json.load(file)
                previous_time = data.get('modification_time')
                if file_time != previous_time:
                    print('file changed')
                    data['modification_time'] = file_time

            with open(previous_time_file, 'w') as file:
                json.dump(data, file)

        return previous_time

    def parse_line(self, line):
        try:
            line = re.sub(r"[\[\]]", "", line)
            data = shlex.split(line)

            requested_url_parts = data[self.REQUESTED_URL].split()
            method = requested_url_parts[0] if requested_url_parts else ''
            url = requested_url_parts[1] if len(requested_url_parts) > 1 else ''

            result = {
                "ip": data[self.IP],
                "time": data[self.TIME],
                "status_code": data[self.STATUS_CODE],
                "method": method,
                "url": url,
                "requested_url": data[self.REQUESTED_URL],
                "user_agent": data[self.USER_AGENT],
            }
            return result
        except Exception as e:
            raise e

    @staticmethod
    def save_file(data: Dict[str, pd.DataFrame]):
        print('Saving file...\r')
        with pd.ExcelWriter('access.log.xlsx') as writer:
            for key, dataframe in data.items():
                dataframe.to_excel(writer, sheet_name=key)
        print('\rSaved file')

    @staticmethod
    def open_file(file_path):

        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", file_path])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:
            raise OSError("Unsupported operating system")
