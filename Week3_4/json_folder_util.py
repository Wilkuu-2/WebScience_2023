#!/bin/env python3 

import asyncio
import aiofiles
import datetime
import json 
import os


def datetime_from_filename(fname):
    return datetime.datetime.strptime(fname, '%Y%m%d_%H%M_data') 

class ParsedFile: 
    def __init__(self,filename,json):
        self.filename = filename.rsplit(".")[0]
        self.json = json


async def gen_json(json_folder,filename):
    filepath = os.path.join(json_folder,filename)
    async with aiofiles.open(filepath) as f:
        contents = await f.read()
        # print(f"parsing {filepath}")
        try:
            return ParsedFile(filename,json.loads(contents))
        except:
            print(f"{filepath} is not valid json")
            return ParsedFile(filename,json.loads("{}"))

async def gather_files(json_folder):
    # json_folder=input("Give the locacion of the extracted database folder:\n")
    json_folder = "youtube_top100" 
    outputs = [] 
    async with asyncio.TaskGroup() as tg: 
        for filename in os.listdir(json_folder):
            if filename.endswith('.json'):
                outputs.append(tg.create_task(gen_json(json_folder,filename)))
            else: 
                print(f"{f_path} is not json")

    return outputs

async def gen_db(folder): 
    outputs = await gather_files(folder) 
    results = []
    for out in outputs:
        results.append(out.result())
    return results 

if __name__ == "__main__": 
    res = asyncio.run(gen_db("youtube_top100"))
    print(datetime_from_filename(res[0].filename))
