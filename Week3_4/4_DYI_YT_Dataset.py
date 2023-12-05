#!/bin/env python 
import argparse 


import os
import googleapiclient.discovery
import googleapiclient.errors
import json 
import time 
from datetime import datetime, timedelta, timezone 

api_service_name = "youtube"
api_version = "v3"

def youtube_authenticate(token):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    # Get credentials and create an API client
    return googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=token)

now = datetime.utcnow()
last_year = now - timedelta(365,0,0)

def query(yt,batchsize=25,page_token = None, regionCode="US",language="en", after=last_year,before=now):
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
        publishedBefore=before.isoformat('T') + 'Z', 
        publishedAfter=after.isoformat('T') + 'Z' 
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
    
    yt = youtube_authenticate(args.YT_API_TOKEN)
     
    dataset = []
    before = datetime.utcnow()
    after = before - timedelta(365,0,0)

    for l in range(0,int(args.number),int(args.batchsize)): 
        print(f"Getting video #{max(0,l-int(args.batchsize))} to #{l}")
        page_token = None
        before = after 
        after  = before - timedelta(365,0,0) 
        while len(dataset) < l:
            print(f"Pulling from api with page_token={page_token}")
            q, page_token = query(yt,
                                  batchsize=min(int(args.batchsize), 50),
                                  page_token=page_token,
                                  regionCode=args.region,
                                  before=before,
                                  after=after)
            print(f"Fetched {len(q)} items")
            dataset.extend(q)
            print(f"Total: {len(dataset)}")

            
            if page_token is None: 
                print("Could not get the next page token, stopping")
                break 

            time.sleep(float(args.interval))

    with open(args.filename, "w") as f: 
        f.write(json.dumps(dataset)) 
        f.close()


