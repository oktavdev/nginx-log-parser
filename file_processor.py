import re


class FileProcessor:

    @staticmethod
    def parse_robots_txt_file(file_path):
        disallowed_agents = []
        agent_pattern = re.compile(r'^User-agent: (.*)', re.IGNORECASE)
        disallow_pattern = re.compile(r'^Disallow: (.*)', re.IGNORECASE)

        current_agent = None
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                agent_match = agent_pattern.match(line)
                if agent_match:
                    current_agent = agent_match.group(1).strip()
                disallow_match = disallow_pattern.match(line)
                if disallow_match and current_agent:
                    disallowed_agents.append(current_agent)
                    current_agent = None

        return list(set(disallowed_agents))
