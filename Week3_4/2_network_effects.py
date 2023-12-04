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


def get_all_song_derivatives(timelines: Dict[str, Dict[datetime, Any]]) -> Dict[str, Dict[datetime, float | None]]: 
    derivatives = {}  
    for id, timeline in timelines.items(): 
        derivatives[id] = {} 
        prev = 0 
        prev_date: datetime | None = None 
        for t, d in timeline.items(): 
            if d is not None: 
                vc = int( d["statistics"]["viewCount"])
                if prev_date == None : 
                    derivatives[id][t] = None 
                else: 
                    days = (t - prev_date).total_seconds() / 3600.0 / 24.0
                    # print(f"{t} - {prev_date} = {t-prev_date} : {days}")
                    derivatives[id][t] = (vc - prev) / days 

                prev_date = t; 
                prev = vc
            else:
                derivatives[id][t] = None 

    return derivatives 


def max_viewcounts(timeline: Dict[datetime, Any]) -> int: 
    return max([int(x["statistics"]["viewCount"]) if x is not None else 0 for x in timeline.values()])

def average_daily(derivative: Dict[datetime, float | None]) -> float: 
    N = 0
    sum = 0

    for d in derivative.values(): 
        if d is not None: 
            N += 1
            sum += d 

    return sum / N  

def median_daily(derivative: Dict[datetime, float | None]) -> np.floating[Any]:
    valid_nums: List[float] = [] 
    
    for d in derivative.values(): 
        if d is not None: 
            valid_nums.append(d)

    return np.median(valid_nums)


def extract_timeline_viewcounts(timeline: Dict[datetime,Any]) -> Dict[datetime,int]:  
    """
    Extracts the viewcount out of the timeline 
    Returns a Dict of the same structure, but with only the viewcount instead of the whole JSON object 
    """
    return dict([(x,y["statistics"]["viewCount"]) if y is not None else (x,None) for x,y in timeline.items()])

def extract_all_viewcounts(timelines: Dict[str,Dict[datetime,Any]]) -> Dict[str,Dict[datetime,int]]:
    """
    Call the extract_timeline_viewcounts on a whole collection of timelines 
    Returns a Dict of the same structure, but with only the viewcount instead of the whole JSON object 
    """
    out = {} 
    for id, timeline in timelines.items():
        out[id] = extract_timeline_viewcounts(timeline)
    return out 


def normalize_all():
    pass 
    # To be implemented

def normalize(inp: Dict[Any,Any]) -> Dict[Any,float | None]:
    """
    Normalize a dictionary of id's and values so that all of the values sum up to one 
    """ 
    total = sum([x if x is not None else 0 for x in inp.values()])
    return dict([(k, v/total) if v is not None else (k,None) for k,v in inp.items()])


def normalize_arr(inp: List[float]) -> List[float]:
    s = sum(inp)
    return [x/s for x in inp]
    

if __name__ == "__main__": 
    print("Week 3/4 Assignment 2")
    data = asyncio.run(gen_db("Week3_4/youtube_top100"))
    print(f"[INFO] First file: {data[0].filename}")
    print(f"[INFO] date: {data[0].parse_filename()}")
    
    fig, (ax_daily, ax_scatter) = plt.subplots(2)

    plot_limitsD = [999999, -999999]
    plot_limitsV = [999999, -999999]
    # for song in data_sorted: 
    #     id = song["id"]
    #     timeline = get_song_timeline(data,id)
    #     title = song["snippet"]["title"]
    #     

    timelines,titles,dates = get_all_song_timelines(data)
    timelines = dict(sorted(list(timelines.items()), key=lambda x: max_viewcounts(x[1]))) # Sort by total view count 
    derivatives = get_all_song_derivatives(timelines)

    EXCL_BOT = 0
    EXCL_TOP = 20 

    graph_median_change_per_day = [float(median_daily(derivative)) for derivative in derivatives.values()]
    graph_max_viewcount = normalize_arr([max_viewcounts(timeline) for timeline in timelines.values()])
    ax_scatter.scatter(graph_median_change_per_day,graph_max_viewcount)

    for id,derivative in list(derivatives.items())[EXCL_BOT:len(derivatives) - EXCL_TOP]: 
        graph_date = []
        graph_change_per_day = []
        graph_viewcounts  = [] 
        title = titles[id]
        for t, d in derivative.items(): 
            if t is not None and d is not None:
                graph_date.append(t) 
                graph_change_per_day.append(d)
                graph_viewcounts.append(int(timelines[id][t]["statistics"]["viewCount"]))

                #graph_viewcounts_log10.append(np.log10(viewcount))
        

        
        plot_limitsD[0] = min(plot_limitsD[0], min(graph_change_per_day))
        plot_limitsD[1] = max(plot_limitsD[1], max(graph_change_per_day)) 
        plot_limitsV[0] = min(plot_limitsV[0], min(graph_viewcounts))
        plot_limitsV[1] = max(plot_limitsV[1], max(graph_viewcounts)) 

        ax_daily.plot(graph_date, graph_change_per_day, label=title)

        ax_daily.set_yticks(np.arange(plot_limitsD[0], plot_limitsD[1]+1, plot_limitsD[1]/20)) 
        #ax_log10.set_yticks(np.arange(np.log10(plot_limits[0]), 
        #                        np.log10(plot_limits[1]+1), 
        #                        (np.log10(plot_limits[1]) - np.log10(plot_limits[0]))/5)) 
   
    # plt.legend()
    # ax_daily.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plt.show()


        




    

    

