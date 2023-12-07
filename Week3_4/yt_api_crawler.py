#!/bin/env python 
import argparse 


import os
import googleapiclient.discovery
import googleapiclient.errors
import json 
import time 
from datetime import datetime, timedelta 

api_service_name = "youtube"
api_version = "v3"

def youtube_authenticate(token):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    # Get credentials and create an API client
    return googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=token)

def query(yt,batchsize=25,page_token = None, regionCode="US",language="en"):
    request = yt.search().list(
        part="id",
        maxResults=batchsize,
        q="music",
        regionCode=regionCode,
        relevanceLanguage=language,
        type="video",
        order="viewCount",
        videoCategoryId="10",
        videoDuration="short",
        videoType="any",
        pageToken="" if page_token is None else page_token,
    )
    
    ids = request.execute()
    
    idlist = [id["id"]["videoId"] for id in ids["items"]]
    
    page_token = None 
    try: 
        page_token = ids["nextPageToken"]
    except: 
        pass
    
    items = []
    
    for id in idlist:  
        request = yt.videos().list(
            part="id,statistics,snippet",
            id=id,
            maxResults=1,
        )
        items.extend(request.execute()["items"])

    return items, page_token


def get_yt_data(token, batchsize=5, number=20, interval=2.0, region="US", language="en"):
    yt = youtube_authenticate(token)

    dataset = []
    before = datetime.utcnow()
    after = before - timedelta(365,0,0)

    page_token = None
    before = after 
    after  = before - timedelta(365,0,0) 
    while len(dataset) < int(number):
        print(f"Pulling from api with page_token={page_token}")
        q, page_token = query(yt,
                              batchsize=min(batchsize, 50),
                              page_token=page_token,
                              regionCode=region,
                              language=language)

        print(f"Fetched {len(q)} items")
        dataset.extend(q)
        print(f"Total: {len(dataset)}")


        if page_token is None: 
            print("Could not get the next page token, stopping")
            break 

        time.sleep(interval)

    return dataset

def write_yt_data(filename, data):
    with open(filename, "w") as f: 
        f.write(json.dumps(data)) 
    f.close()

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(
                        prog='YT_API_Crawler',
                        description='Crawls the Youtube recommends',
                        epilog='"Huhg huh" -Minecraft Villager') # Idk what to put there... 

    parser.add_argument("YT_API_TOKEN", help="The Youtube API Token")
    parser.add_argument("filename", help="Output filename")
    parser.add_argument("-b", "--batchsize",default=5, help="Amount of videos per query")
    parser.add_argument("-n", "--number",default=20, help="Amount of videos to pull")
    parser.add_argument("-i", "--interval",default=2, help="Amount of seconds to wait between requests")
    parser.add_argument("-r", "--region",default="US", help="Region of the videos")
    parser.add_argument("-l", "--language",default="en", help="Language of the videos")
    
    args = parser.parse_args()
    
    data = get_yt_data(args.YT_API_TOKEN, batchsize=int(args.batchsize), number=int(args.number), interval=float(args.interval), region=args.region, language=args.language)
    write_yt_data(args.filename, data)




