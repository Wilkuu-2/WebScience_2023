#!/bin/env python 
import argparse 


import os
import googleapiclient.discovery
import googleapiclient.errors
import json 
import time 

api_service_name = "youtube"
api_version = "v3"

def youtube_authenticate(token):
    """
    Creates a authenticated Youtube API handle 
    """
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    # Get credentials and create an API client
    return googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=token)

def query(yt,q,batchsize=25,page_token = None, regionCode="US",language="en"):
    """
    Pulls a batch of top videos from the youtube api, this is completed in `batchsize + 1` requests
    Returns a list of video resource items 
    """
    request = yt.search().list(
        part="id", # Only get the id, we'll get the rest in the next request 
        maxResults=batchsize, 
        q=q, # Query using the word music to ensure we only get music videos 
        regionCode=regionCode,
        relevanceLanguage=language,
        type="video", # Ensure that we get videos instead of channels 
        order="viewCount", # Get the top viewed videos 
        videoCategoryId="10", # Type: Music 
        videoDuration="short", # Avoid playlists/compilations 
        videoType="movie", # Avoid shorts  
        pageToken="" if page_token is None else page_token,
    )

    # Get all the id json and parse it  
    ids = request.execute()
    idlist = [id["id"]["videoId"] for id in ids["items"]]
   
    # See if we get the next page token  
    page_token = None 
    try: 
        page_token = ids["nextPageToken"]
    except: 
        pass
    

    # Fetch all the video info 
    items = []
    for id in idlist:  
        request = yt.videos().list(
            part="id,statistics,snippet",
            id=id,
            maxResults=1,
        )
        items.extend(request.execute()["items"])

    # Return the items and the token for the next page 
    return items, page_token


def get_yt_data(token, batchsize=5, number=20, interval=2.0, region="US", language="en", q="music"):
    """
    A method that gathers a top `number` of videos in the given regioni and in a given language. 
    Returns a list of json objects which are the video resource items 
    """
    yt = youtube_authenticate(token)
    
    # Repeadetly call query to get the desired amount of videos 
    dataset = []
    page_token = None
    while len(dataset) < int(number):
        print(f"Pulling from api with page_token={page_token}")
        q, page_token = query(yt,
                              q,
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
    """Writes the data from youtube in a file.""" 
    with open(filename, "w") as f: 
        f.write(json.dumps(data)) 
    f.close()

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(
                        prog='YT_API_Crawler',
                        description='Crawls the Youtube recommends',
                        epilog='All your base are belong to us.') # Idk what to put there... 

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




