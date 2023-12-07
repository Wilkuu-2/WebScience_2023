#!/bin/env python3

from datetime import datetime
from typing import Dict, List, Any 
import matplotlib.pyplot as plt 
import asyncio
from json_folder_util import gen_db, ParsedFile

def get_song_timeline(data: List[ParsedFile], id: str) -> Dict[datetime, Any]:
    """
    Gets a timeline of a particular song with a particular `id` 
    Returns a dict 
        with the date of the datapoint from the ParsedFile objects as key
        ,and the json data as value

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
    """
    Gets all timelines from the given list of ParsedFile object 
    Returns a double layered dict 
        with the id as the first key
        date of the data point in the second key
        and the json object of the song datapoint as value 
    """
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
    """
    Returns the highest viewcount of the given timeline
    """
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
    assert len(data) > 0, "No data parsed" 
    assert type(data[0]) == ParsedFile, "Invalid data format recieved"
    print(f"[INFO] Parsed files: {len(data)}")
    print(f"[INFO] First file: {data[0].filename}")
    print(f"[INFO] date: {data[0].parse_filename()}")
    print(f"[INFO] data: CORRECT")
    fig, (ax_daily) = plt.subplots(1)

    plot_limitsD = [999999, -999999]

    timelines,titles,dates = get_all_song_timelines(data)
    timelines = dict(sorted(list(timelines.items()), key=lambda x: max_viewcounts(x[1]))) # Sort by total view count 
    viewcounts = extract_all_viewcounts(timelines)

    # Get the data, filtered by the top 100 songs 
    EXCL_BOT = 20 
    EXCL_TOP = 0 
    
    plot_data = list(viewcounts.items())[EXCL_BOT:len(viewcounts) - EXCL_TOP]
    plot_len = len(plot_data)
    plot_progress =0

    print("[INFO]: Plotting: ")
    for id,vc in plot_data: 
        plot_progress +=1
        print(f"[PROGRESS]: {plot_progress}/{plot_len}", end='\r')
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

    ax_daily.set_xlabel("Date") 
    ax_daily.set_ylabel("Total views")
    ax_daily.set_title("Total views per day of the top 100 songs on youtube")

        
    print("[PROGRESS]: DONE             ")
    save_path = "./Figure_2_1.png"
    plt.savefig(save_path)
    print(f"[PLOT]: Saved plot in {save_path}")
    print("[PLOT]: Showing plot")

    plt.show()


        




    

    

