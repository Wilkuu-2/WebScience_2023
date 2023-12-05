
import asyncio
from json_folder_util import gen_db, datetime_from_filename
import datetime
import matplotlib.pyplot as plt
import random

TEST_COUNT = 10

# Get first songs ids of first entry
res = asyncio.run(gen_db("Week3_4/youtube_top100"))
random_song_ids = set()
for i in range(TEST_COUNT):
    random_song_ids.add(res[0].json[random.randrange(len(res[0].json))]["id"])

res2 = asyncio.run(gen_db("Week3_4/radio3fm_megahit"))
res3 = asyncio.run(gen_db("Week3_4/radio538_alarmschijf"))
random_song_ids_filtered = set()
while len(random_song_ids_filtered) < TEST_COUNT:
    random_id = res[0].json[random.randrange(len(res[0].json))]["id"]
    if random_id not in map(lambda song: song["id"], res2[0].json):
        if random_id not in map(lambda song: song["id"], res3[0].json):
            random_song_ids_filtered.add(random_id)

print("done with lists")

# loops through every json file in folder and searches for the given song_id. Lastly returning the array of the matching entries.
def get_all_song_data_points(song_id):
    song_data_point_list = {}
    for data_point in res:
        for song in data_point.json:
            if (song["id"] == song_id):
                song_data_point_list[datetime_from_filename(data_point.filename)] = song
    return song_data_point_list

def subplot_song_ids(song_ids, axis, plot):
    plot_likeabilities = []
    for song_id in song_ids:
        song_data = get_all_song_data_points(song_id)
        sorted_song_data = sorted(song_data.items())
        base_likeability = int(sorted_song_data[0][1]["statistics"]["likeCount"]) - int(sorted_song_data[0][1]["statistics"]["dislikeCount"])

        # single usage of function for mapping
        def map_song_likability(sorted_song):
            like_count = int(sorted_song[1]["statistics"]["likeCount"])
            dislike_count = int(sorted_song[1]["statistics"]["dislikeCount"])
            return (sorted_song[0], like_count - dislike_count - base_likeability)

        mapped_song_data = list(map(map_song_likability, sorted_song_data))
        data_points, likeabilities = list(zip(*mapped_song_data))
        plot_likeabilities.extend(likeabilities);

        axis[plot].plot(
            data_points[0:6], 
            likeabilities[0:6],
            label = sorted_song_data[0][1]["snippet"]["title"]
        )
        axis[plot].legend()
    print(plot, "avg:", sum(plot_likeabilities) / len(plot_likeabilities))

figure, axis = plt.subplots(1, 2)
subplot_song_ids(random_song_ids, axis, 0)
axis[0].set_title('Difference likes and dislikes over period 7 days starting from baseline')
axis[0].set_xlabel('Date')
axis[0].set_ylabel('Likeability')
subplot_song_ids(random_song_ids_filtered, axis, 1)
axis[1].set_title('Same data but its filtered out the songs that are in the 538 top100 and 3fm top100')
axis[1].set_xlabel('Date')
axis[1].set_ylabel('Likeability')
plt.show()

print(datetime_from_filename(res[0].filename), "Test working:", datetime_from_filename(res[0].filename) == datetime.datetime(2016,11,18,18,00,00))