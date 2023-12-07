
import asyncio
from json_folder_util import gen_db, datetime_from_filename
import datetime
import matplotlib.pyplot as plt
import numpy as np
import random

DAY_OFFSET = 0
NUMBER_OF_DAYS = 365
BINS = 50
AMOUNT_SHOWN_IN_TOP = 15

# Filling a set of unique songs ids
res = asyncio.run(gen_db("Week3_4/youtube_top100"))
song_ids = set()
for i in res:
    song_ids.add(i.json[random.randrange(len(i.json))]["id"])

def get_all_song_data_points(song_id):
    """
    Loops through every json file in folder and searches for the given song_id. Lastly returning the array of the matching entries.
    """
    song_data_point_list = {}
    for data_point in res:
        for song in data_point.json:
            if (song["id"] == song_id):
                song_data_point_list[datetime_from_filename(data_point.filename)] = song
    return song_data_point_list

figure, axis = plt.subplots(2, 2)
total_song_data = []

for song_id in song_ids:
    song_data = get_all_song_data_points(song_id)
    # single usage function for mapping
    def map_song_views(sorted_song):
        view_count = int(sorted_song[1]["statistics"]["viewCount"])
        name = sorted_song[1]["snippet"]["title"]
        return (sorted_song[0], view_count, name)

    mapped_song_data = list(map(map_song_views, song_data.items()))
    # data_points, views = list(zip(*mapped_song_data))
    total_song_data.append(mapped_song_data[DAY_OFFSET:NUMBER_OF_DAYS-1])

total_song_data_squashed = []
for song in total_song_data:
    for data_point in song:
        date = data_point[0]
        views = data_point[1]
        total_song_data_squashed.append((date,views))

data_points, views = list(zip(*total_song_data_squashed))
hist, edges = np.histogram(views, bins=BINS)
axis[0,0].scatter(edges[:-1], hist)
axis[0,0].set_title('Amount of view over period {} days starting from baseline'.format(NUMBER_OF_DAYS))
axis[0,0].set_xlabel('Views')
axis[0,0].set_ylabel('Amount of songs')

# Get the centers of the bins for the scatter plot
bin_centers = (edges[:-1] + edges[1:]) / 2.0
# Create a log-log scatter plot
axis[0,1].loglog(bin_centers, hist, 'o')
axis[0,1].set_title('Same data but logarithmic view')
axis[0,1].set_xlabel('Rank')
axis[0,1].set_ylabel('Log views')

# First sort the data points chronologically
sorted_total_song_data = []
for song_data in total_song_data:
    sorted_total_song_data.append(sorted(song_data, key=lambda x: x[0]))

# Then sort based on the last data point the amount of views
sorted_total_song_data = sorted(sorted_total_song_data, key=lambda x: x[-1][1], reverse=True)
i = 0
# Plotting top songs
for song_data in sorted_total_song_data:
    data_points, views, name = list(zip(*song_data))
    axis[1,0].plot(data_points, views, label = name[0])
    i += 1;
    if i == AMOUNT_SHOWN_IN_TOP: break
axis[1,0].set_title('Top {} songs sorted by views'.format(AMOUNT_SHOWN_IN_TOP))
axis[1,0].set_xlabel('Date')
axis[1,0].set_ylabel('Views')
axis[1,0].legend()

# Getting spotify data
res2 = asyncio.run(gen_db("Week3_4/spotify_top100"))
spotify_data = {}
for data_point in res2:
    spotify_data[datetime_from_filename(data_point.filename)] = data_point.json['tracks']['items']

# Getting spotify data from last data point
rank_data_point = sorted_total_song_data[0][-1][0]
ranking_data = spotify_data[rank_data_point]
print(rank_data_point)
# Printing the top 10
for i in range(AMOUNT_SHOWN_IN_TOP):
    artist_names = list(map(lambda artist: artist['name'],ranking_data[i]['track']['artists']))
    print(artist_names, "-", ranking_data[i]['track']['name'])
plt.show()