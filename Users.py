import os
from geopy.distance import geodesic 
volunteers_directory = os.path.join(os.getcwd(), "Volunteers")

class User:

    def __init__(name, number, adress, order):
        self.name = name
        self.number = number
        geolocator = Nominatim()
        location = geolocator.geocode(adress)
        self.lat, self.long = location.latitude, location.longitude
        self.order = order
        self.order = []
        for file_name in os.listdir(volunteers_directory):
            with open(file_name, 'r') as file:
                lines = file.readlines()
                line = lines[0].strip().split(",")
                name, lat, long = line[0], line[1], line[2]
                distance = geodesic((lat, long), (self.lat, self.long)).miles
                order.append([name, file_name, distance])
        self.order.sort(key = lambda arr:arr[2])

    def get_current_item(self):
        return self.order[0]

    def move_to_next(self):
        self.order = self.order[1:]

if __name__ == "__main__":
    #file.read().splitlines()
    print("User Class")
