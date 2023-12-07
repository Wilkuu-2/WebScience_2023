#!/bin/env python
from typing import List, Self, Any
import yt_api_crawler as api 
import json 
import dataclasses
import matplotlib.pyplot as plt 

FILENAME="export.json"

@dataclasses.dataclass
class Song: 
    """
    A dataclass for a song based on the youtube top 100 dataset
    """
    title: str = ""
    viewcount: int = 0

    def __lt__(self, other: Self) -> bool:
        return self.viewcount < other.viewcount 

    def __gt__(self, other: Self) -> bool:
        return self.viewcount > other.viewcount 

def get_song_from_json(data: Any, print_dot=False) -> Song:
    """
    Accepts json for a single video resource item from the Youtube API V3 and returns a song object based on the json
    """
    if print_dot:
        print('.', end='')
    return Song(data["snippet"]["title"], int(data["statistics"]["viewCount"]))

def parse_songs(data: Any, show_progress=False) -> List[Song]:
    """
    Accepts a JSON list of video resource items and return a list of songs using `get_song_from_json`
    """
    return [get_song_from_json(d, print_dot=show_progress) for d in data]
        
if __name__ == "__main__": 
    data = {} 
    try:
        f = open(FILENAME,"r") 
        data = json.load(f) 
    except FileNotFoundError: 
        # Try to resolve the lack of proper dataset by asking to fetch it 
        print("[ERR]: {FILENAME} not found ")
        while True: 
            ans = input("Re-Fetch dataset? This will require your own YT Api token. [Yy/Nn] ")
            if "n" in ans.lower(): 
                "[INFO]: No valid dataset, exiting."
                exit(1) 
            elif "y" in ans.lower():
                token = input("Input API token: ")
                data = api.get_yt_data(token, 
                                        batchsize=50,
                                        number=400,
                                        region="US",
                                        language="en",
                                       interval=2.0)

                print(f"Saving data in {FILENAME}")
                api.write_yt_data(FILENAME, data)

    except json.JSONDecodeError: 
        # If the JSON is invalid, just bail 
        print("[ERR]: Invalid JSON, exiting.")
        exit(1)

    finally: 
        try:
            f.close() # type: ignore 
        except: 
            pass # Don't do anything if the file was not found
        
    # Parsing and ordering the data
    print("[INFO]: Loaded dataset. Parsing:")
    sorted_songs = sorted(parse_songs(data,show_progress=True),reverse=True);
    rank = list(range(1,len(sorted_songs)+1))
    viewcounts = [s.viewcount for s in sorted_songs]
    max_vc = max(viewcounts)
    print("\n[INFO]: Parsing, done")
    
    # Plotting 
    plt.plot(rank, viewcounts)
    plt.title(f"View count distribution of top {len(sorted_songs)} youtube music videos")
    # plt.xlim((0,rank[-1]))
    # plt.ylim((0,viewcounts[0] + 100_000))
    plt.xlabel("Ranking of the video")
    plt.ylabel("Views")
    plt.show()
