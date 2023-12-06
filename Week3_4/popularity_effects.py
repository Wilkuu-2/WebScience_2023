
import asyncio
from json_folder_util import gen_db, datetime_from_filename
import datetime
import matplotlib.pyplot as plt
import numpy as np
import random

DAY_OFFSET = 0;
NUMBER_OF_DAYS = 7;
BINS = 100;


# Get first songs ids of first entry
res = asyncio.run(gen_db("Week3_4/youtube_top100"))
song_ids = set()
for i in res:
    song_ids.add(i.json[random.randrange(len(i.json))]["id"])

# loops through every json file in folder and searches for the given song_id. Lastly returning the array of the matching entries.
def get_all_song_data_points(song_id):
    song_data_point_list = {}
    for data_point in res:
        for song in data_point.json:
            if (song["id"] == song_id):
                song_data_point_list[datetime_from_filename(data_point.filename)] = song
    return song_data_point_list

figure, axis = plt.subplots(1, 2)
total_views = []

for song_id in song_ids:
    song_data = get_all_song_data_points(song_id)
    # single usage of function for mapping
    def map_song_views(sorted_song):
        view_count = int(sorted_song[1]["statistics"]["viewCount"])
        return (sorted_song[0], view_count)

    mapped_song_data = list(map(map_song_views, song_data.items()))
    data_points, views = list(zip(*mapped_song_data))
    
    total_views.extend(views[DAY_OFFSET:NUMBER_OF_DAYS-1])

hist, edges = np.histogram(total_views, bins=BINS)
axis[0].scatter(edges[:-1], hist)

axis[0].set_title('Amount of view over period 7 days starting from baseline')
axis[0].set_xlabel('Views')
axis[0].set_ylabel('Amount of songs')

# Get the centers of the bins for the scatter plot
bin_centers = (edges[:-1] + edges[1:]) / 2.0

# Create a log-log scatter plot
axis[1].loglog(bin_centers, hist, 'o')

axis[1].set_title('Same data but logarithmic view')
axis[1].set_xlabel('Rank')
axis[1].set_ylabel('Log views')
plt.show()