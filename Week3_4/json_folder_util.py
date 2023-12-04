#!/bin/env python3 
""" Json folder util 
 
 An utility to parse entire folders full of json, asyncronously 
 
 Usage: 
 ``files = await gen_db("path1/path2/folder_with_json")``

Copyright 2023 Jakub Stachurski, Kalli van den Heuvel 
"""

from dataclasses import dataclass
import asyncio
from typing import Any
import aiofiles
import datetime
import json 
import os


def datetime_from_filename(fname):
    """
    Parses a filename of a youtube api query.
    Returns a datetime corresponding to the date of the query
    """
    return datetime.datetime.strptime(fname, '%Y%m%d_%H%M_data.json') 

@dataclass
class ParsedFile: 
    """
    A dataclass 
    """
    filename: str
    json: Any # json.loads() returns any 

    def parse_filename(self): 
        """Parses the filename using datetime_from_filename"""
        return datetime_from_filename(self.filename)
        
 
async def gen_json(json_folder,filename):
    """
    Parses the file with filename ``filename`` in the ``json_folder directory``
    Returns a ParsedFile object 
    """
    filepath = os.path.join(json_folder,filename)
    async with aiofiles.open(filepath) as f:
        contents = await f.read()
        # print(f"parsing {filepath}")
        try:
            return ParsedFile(filename,json.loads(contents))
        except:
            print(f"{filepath} is not valid json")
            return ParsedFile(filename,json.loads("{}"))

async def gen_db(json_folder):
    """
    Loads a folder of json files asyncronously
    Returns a list of ``ParsedFile objects``
    """
    # json_folder=input("Give the locacion of the extracted database folder:\n")
    outputs = [] 
    async with asyncio.TaskGroup() as tg: 
        for filename in os.listdir(json_folder):
            if filename.endswith('.json'):
                outputs.append(tg.create_task(gen_json(json_folder,filename)))
            else: 
                print(f"{filename} is not json")

    results = []
    for out in outputs:
        results.append(out.result())
    return results 

if __name__ == "__main__": 
    res = asyncio.run(gen_db("youtube_top100"))
    print(f"[TEST] This should be a date: {datetime_from_filename(res[0].filename)}")
