#!/bin/env python3

from datetime import datetime
from typing import Dict, List, Any 
import matplotlib.pyplot as plt 
import asyncio
from json_folder_util import gen_db, ParsedFile

def get_song_timeline(data: List[ParsedFile], id: str) -> Dict[datetime, Any]:
    """
    """
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


def get_all_song_timelines(data: List[ParsedFile]):
    timelines: Dict[str, Dict[datetime,Any]]= {} 
    titles: Dict[str, str] = {} 
    dates = []
    for file in data: 
        date = file.parse_filename()
        for song in file.json: 
            id = song["id"]
            title = song["snippet"]["title"]
            if id not in titles: 
                titles[id] = title

            # Add song to the timelines and backfill all the dates  
            if id not in timelines: 
                timelines[id] = {} 
                for date in dates: 
                    timelines[id][date] = None

            timelines[id][date] = song 

        dates.append(date)
        # Fill any holes 
        for timeline in timelines.values():
            if date not in timeline:
                timeline[date] = None

    return (timelines,titles, dates) 

def max_viewcounts(timeline: Dict[datetime, Any]) -> int: 
    return max([int(x["statistics"]["viewCount"]) if x is not None else 0 for x in timeline.values()])

def extract_timeline_viewcounts(timeline: Dict[datetime,Any]) -> Dict[datetime,int]:  
    """
    Extracts the viewcount out of the timeline 
    Returns a Dict of the same structure, but with only the viewcount instead of the whole JSON object 
    """
    #
    return dict([
        (x,int(y["statistics"]["viewCount"])) 
        if y is not None else 
        (x,None) 
        for x,y in timeline.items()]) #type: ignore

def extract_all_viewcounts(timelines: Dict[str,Dict[datetime,Any]]) -> Dict[str,Dict[datetime,int]]:
    """
    Call the extract_timeline_viewcounts on a whole collection of timelines 
    Returns a Dict of the same structure, but with only the viewcount instead of the whole JSON object 
    """
    out = {} 
    for id, timeline in timelines.items():
        out[id] = extract_timeline_viewcounts(timeline)
    return out 

if __name__ == "__main__": 
    print("Week 3/4 Assignment 2")
    data = asyncio.run(gen_db("Week3_4/youtube_top100"))
    print(f"[INFO] First file: {data[0].filename}")
    print(f"[INFO] date: {data[0].parse_filename()}")
    
    fig, (ax_daily) = plt.subplots(1)

    plot_limitsD = [999999, -999999]
    plot_limitsV = [999999, -999999]

    timelines,titles,dates = get_all_song_timelines(data)
    timelines = dict(sorted(list(timelines.items()), key=lambda x: max_viewcounts(x[1]))) # Sort by total view count 
    viewcounts = extract_all_viewcounts(timelines)

    EXCL_BOT = 20 
    EXCL_TOP = 0 

    for id,vc in list(viewcounts.items())[EXCL_BOT:len(viewcounts) - EXCL_TOP]: 
        graph_date = []
        graph_viewcounts = []
        title = titles[id]
        for t, d in vc.items(): 
            if t is not None and d is not None:
                graph_date.append(t) 
                graph_viewcounts.append(d)
            
        plot_limitsD[0] = min(plot_limitsD[0], min(graph_viewcounts))
        plot_limitsD[1] = max(plot_limitsD[1], max(graph_viewcounts)) 

        ax_daily.plot(graph_date, graph_viewcounts, label=title)

    plt.show()


        




    

    

