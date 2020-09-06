#!/usr/bin/env python3
import json as jsonlib
from urllib.parse import urljoin
import requests
from pathlib import Path
from sys import argv
from time import sleep


import pgark.archivers.wayback as wb
from pgark import mylogger

def main():
    """hack routine that does wayback.save the manual way, while saving each
        response by wayback into the dest_dir

        TO BE DEPRECATED
    """
    target_url = argv[1]
    dest_dir = Path(argv[2])
    dest_dir.mkdir(exist_ok=True, parents=True)

    user_agent = 'Mozilla'

    answer, meta = wb.snapshot(target_url, user_agent=user_agent, debug_path=dest_dir)

if __name__ == '__main__':
    main()
