import json
import os
import platform
import re
import shelve
import shlex
import subprocess
from typing import Dict

import pandas as pd

import settings
from parser.robotstxt_parser import RobotsTxtProcessor


class Parser(RobotsTxtProcessor):
    IP = 0
    TIME = 3
    TIME_ZONE = 4
    REQUESTED_URL = 5
    STATUS_CODE = 6
    USER_AGENT = 9

    def read_parse_file(self, file_name: str, website_url: str = '') -> Dict[str, pd.DataFrame]:

        file_time = os.path.getmtime(file_name)

        previous_time = self.get_save_previous_time(file_time)

        if file_time != previous_time or not os.path.isfile('shelve.db'):
            with open(file_name, "r") as f:
                print('Reading file...')
                log_entries = [self.parse_line(line) for line in f]

            with shelve.open(settings.SHELVE_DB, flag='c', protocol=None, writeback=False) as db:
                db['log_entries'] = log_entries

        with shelve.open(settings.SHELVE_DB, flag='c', protocol=None, writeback=False) as db:
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

        bots_not_obeying = pd.DataFrame()
        if website_url:
            _, disallowed_bots = self.check_disallowed_agents(website_url)
            disallowed_bots_df = pd.DataFrame(disallowed_bots, columns=['bot'])

            def count_bot_in_user_agent(bot):
                pattern = re.escape(bot)
                return logs_df['user_agent'].str.contains(pattern, case=False, regex=True).sum()

            disallowed_bots_df['requests_number'] = disallowed_bots_df['bot'].apply(count_bot_in_user_agent)
            bots_not_obeying = disallowed_bots_df[disallowed_bots_df['requests_number'] > 0][
                ['bot', 'requests_number']].reset_index(drop=True)
            bots_not_obeying = bots_not_obeying.sort_values(by='requests_number', ascending=False)

        return {
            'User agents': pivot_user_agents,
            'Status codes': pivot_status_codes,
            # 'Data': logs_df,
            'Errors': error_urls_df,
            'Bots not obeying': bots_not_obeying,
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

    def parse_line(self, line):  # TODO: Adapt to read Apache log entry as well
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
        with pd.ExcelWriter(settings.EXCEL_FILE) as writer:
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
