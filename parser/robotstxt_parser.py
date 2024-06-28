import re
import requests


class RobotsTxtProcessor:

    def check_disallowed_agents(self, url):
        robots_txt = self._get_robots_txt(url)
        if not robots_txt:
            return None
        disallowed_agents = self._get_disallowed_agents(robots_txt)
        return url, disallowed_agents

    @staticmethod
    def _get_disallowed_agents(robots_txt):
        disallowed_agents = []
        agent_pattern = re.compile(r'^User-agent: (.*)', re.IGNORECASE)
        disallow_pattern = re.compile(r'^Disallow: (.*)', re.IGNORECASE)

        current_agent = None
        for line in robots_txt.splitlines():
            line = line.strip()
            agent_match = agent_pattern.match(line)
            if agent_match:
                current_agent = agent_match.group(1).strip()
            disallow_match = disallow_pattern.match(line)
            if disallow_match and current_agent and current_agent != '*':
                disallowed_agents.append(current_agent)
                current_agent = None

        return list(set(disallowed_agents))

    @staticmethod
    def _get_robots_txt(url):
        if not url.endswith('/'):
            url += '/'
        robots_url = url + 'robots.txt'
        response = requests.get(robots_url)
        if response.status_code == 200:
            return response.text
        else:
            return None
