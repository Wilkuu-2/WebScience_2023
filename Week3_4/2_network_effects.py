#!/bin/env python3

from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt 
import numpy as np 
import asyncio
from json_folder_util import gen_db, ParsedFile

def get_song_timeline(data: List[ParsedFile], id: str) -> Dict[datetime, Any]:
    timeline = {}
    for file in data: 
        date = file.parse_filename()
        for song in file.json: 
            if song["id"] == id: 
                timeline[date] = song
                break
        # If the song was not in the top 100 
        else: 
            timeline[date] = None
    return timeline

            

if __name__ == "__main__": 
    print("Week 3/4 Assignment 2")
    data = asyncio.run(gen_db("Week3_4/youtube_top100"))
    print(f"[INFO] First file: {data[0].filename}")
    print(f"[INFO] date: {data[0].parse_filename()}")
    data_sorted = sorted(data[0].json, key=lambda v: v["statistics"]["viewCount"])[0:15]
    print("[INFO] Top 10 songs initially (views)")
    for i in range(0,len(data_sorted)): 
        title = data_sorted[i]["snippet"]["title"]
        likeCount = data_sorted[i]["statistics"]["viewCount"]
        print(f"[{i+1}]: {title} - {likeCount}")

    
    ax = plt.axes()
    plot_limits = [999999, -999999]
    for song in data_sorted: 
        id = song["id"]
        timeline = get_song_timeline(data,id)
        title = song["snippet"]["title"]
        
        _vc: Dict[datetime, int] = {} 
        for t, d in timeline.items(): 
            _vc[t] = np.log10(int(d["statistics"]["viewCount"]))

        graph_date, graph_viewcounts = zip(*_vc.items())
        plot_limits[0] = min(plot_limits[0], min(graph_viewcounts))
        plot_limits[1] = max(plot_limits[1], max(graph_viewcounts)) 
        ax.plot(graph_date, graph_viewcounts, label=title)

    plt.legend()
    plt.yticks(np.arange(plot_limits[0], plot_limits[1]+1, plot_limits[1]/20)) 
    plt.show()


        




    

    

