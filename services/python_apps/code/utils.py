import math
import random

def generate_random_coordinates(num_points, min_coord=-180, max_coord=180):
    coordinates = {}
    for i in range(num_points):
        x = random.uniform(min_coord, max_coord)
        y = random.uniform(min_coord, max_coord)
        coordinates[f"Point_{i+1}"] = (x, y)
    return coordinates

def change_location(coordinates, point, max_range):
    lat, long = coordinates[point]
    
    # Generate random offsets for latitude and longitude within the specified range
    delta_lat = random.uniform(-max_range / 111.32, max_range / 111.32)  # Convert km to degrees latitude
    delta_long = random.uniform(-max_range / (111.32 * math.cos(lat * (math.pi / 180))), max_range / (111.32 * math.cos(lat * (math.pi / 180))))  # Convert km to degrees longitude
    
    # Update latitude and longitude
    new_lat = lat + delta_lat
    new_long = long + delta_long
    
    coordinates[point] = (new_lat, new_long)
    
    print("prev:", lat, long)
    print("new:", new_lat, new_long)

    return {"id": point, "lat": new_lat, "long": new_long}
