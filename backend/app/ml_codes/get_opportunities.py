from grab_locations import grab_locations_opportunity

locations = grab_locations_opportunity(
    -6.174904869095269, 
    106.8271353670165
)

with open("data/oppor-20.json", "w") as f:
    f.write(locations)