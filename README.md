# Nginx access log viewer

I have written this app when stumbled upon the challenge to get some insights from Nginx logs.
This one is simple yet efficient.

## What it does
It just takes one access log file (text format, uncompressed), parses it and saves an Excel file.

On initial load, a 84 MB file (~250 000 excel rows) took around 2 minutes.
On subsequent runs the file is cached until file changed.

TODO: Optimize for speed and get all logs from a directory.

## Prerequisites
- Create virtual environment
```shell
python3 -m venv venv
source env/bin/activate
pip install -r requirements.txt
```
## How to use
```shell
python run.py {{ nginx_log_file_path }}
```
Example: python run.py ~/Downloads/access.log