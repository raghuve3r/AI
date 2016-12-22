# B551 Elements of Artificial Intelligence, Fall 2016
# Assignment 1: Searching
# Charlene Tay (ctay), Junjie Lu (junjlu), and Raghuveer Kanchibail (rkanchib)
#
# This program implements algorithms that find good driving directions between pairs of cities
# given by the user.
#
# Instructions
# command:
#     python route.py [start-city] [end-city] [routing-option] [routing-algorithm]
# where:
#     start-city and end-city are the cities we need a route between.
#     routing-option: segments, distance, time or scenic
#         segments finds a route with the fewest number of turns (i.e. edges of the graph)
#         distance finds a route with the shortest total distance
#         time finds the fastest route, for a car that always travels at the speed limit
#         scenic finds the route having the least possible distance spent on highways
#         (highways = roads with speed limits >= 55 mph)
#      routing-algorithm: bfs, dfs, ids or astar
#  output: directions, including travel times, distances, intermediate cities and highway names
#     [total-distance-in-miles] [total-time-in-hours] [start-city] [end-city] [city-1] [city-2] ... [end-city]
#
# Notes: cleaned up the file by skipping over roads with missing values. Use greedy approach by sorting
# successors by cost before exploring successors.
# 1) Which search algorithm seems to work best for each of the routing options?

    # For segments, BFS and Astar are on par - they both find the paths with the smallest number of segments.
    #  BFS and DFS find the same path regardless of routing option. BFS and IDS usually is better at finding the shortest
    # path than DFS, and Astar does better at finding paths with the shortest distance and shortest time and the most
    # scenic routes than the other algorithms.

# 2) Which algorithm is fastest in terms of the amount of computation time required by your program,
# and by how much, according to your experiments? (To measure time accurately, you may want to temporarily include a
# loop in the program that runs the routing a few hundred or thousand times.

    # Astar is the fastest in terms of the amount of computation time required by the program.

# 3) Which algorithm requires the least memory, and by how much, according to your experiments?

    # IDS requires the least memory (shortest fringe)

# 4) Which heuristic function did you use, how good is it, and how might you make it better?

    # For the AStar algorithm, we used distance (calculated from gps coordinates) between two cities as a heuristic to
    # find a path with the shortest distance. To find a path with the shortest time, we used time = distance/average speed
    # of the highways as a heuristic. It works reasonably well, but we did not have gps coordinates for many cities.

# 5) Supposing that you start in Bloomington, which city should you travel to if you want to take the longest possible
# drive (in miles) that is still the shortest path to that city? (In other words, which city is furthest from
# Bloomington?

import sys
import operator
import Queue as Q
import time
from math import radians, cos, sin, asin, sqrt


class Node(object):
    # A node (city) on a map of many cities.
    # Each city is connected to other cities by roads/highways, which each have
    # attributes like length, speed limit and road name.
    # Each city also has associated gps coordinates.
    def __init__(self, name, location):
        # store properties for each city.
        self.city = name
        self.latitude = location[0]
        self.longitude = location[1]
        self.distance_to_neighbor = {}
        self.time_to_neighbor = {}
        self.road_name = {}
        self.is_highway = {}
        self.neighbor = []
        self.successors = []
        self.priority = 0  # initialize priority to 0, meaning they are equal/no priority to self or other
        self.route_cost = 0
        self.route = []  # initialize route that we're going to return
        self.explored = False  # to check if node has been visited

    # Return negative integer if self is less than other, zero if they are equal,
    # and positive integer if self is greater
    def __cmp__(self, other):
        return cmp(self.priority, other.priority)

    # takes information about a road and associates it with a city (self),
    # the neighboring city that the road connects it to,
    # road length, speed_limit, and name of the road.
    def store_road_information(self, next_city, road_length, speed, highway_name):
        self.distance_to_neighbor[next_city] = road_length
        self.time_to_neighbor[next_city] = road_length / float(speed)  # time = distance/speed
        self.road_name[next_city] = highway_name
        self.neighbor.append(next_city)
        if speed >= 55:
            self.is_highway[next_city] = 1
        else:
            self.is_highway[next_city] = 0

    # Stores the total cost of the current path, based on routing option
    def update_cost(self, city1, cost, option):
        if option == 'segments':
            self.route_cost = cost + 1
        elif option == 'distance':
            self.route_cost = self.distance_to_neighbor[city1] + float(cost)
        elif option == 'time':
            self.route_cost = self.time_to_neighbor[city1] + float(cost)
        elif option == 'scenic':
            self.route_cost = self.is_highway[city1] + cost

    # Updates path of cities in route
    def add_to_route(self, existing_route):
        self.route = existing_route + [self.city]

    # Updates the cost using gps distance heuristic
    def update_heuristic(self, city1, city2, coords, cost, option, avg_speed_limit):
        if option == 'segments':
            self.route_cost = cost + 1
        elif option == 'distance':
            if self.latitude == '' or self.longitude == '':
                new_cost = float(cost)
            elif coords[city2].latitude == '' or coords[city2].longitude == '':
                new_cost = float(cost)
            else:
                new_cost = calculate_distance(self.latitude, self.longitude, coords[city2].latitude,
                                              coords[city2].longitude)
            self.priority = self.distance_to_neighbor[city1] + new_cost + float(cost)
            self.route_cost = self.distance_to_neighbor[city1] + float(cost)
        elif option == 'time':
            if self.latitude == '' or self.longitude == '':
                new_cost = float(cost)
            elif coords[city2].latitude == '' or coords[city2].longitude == '':
                new_cost = float(cost)
            else:
                new_cost = calculate_distance(self.latitude, self.longitude, coords[city2].latitude,
                                              coords[city2].longitude) / avg_speed_limit
            self.priority = self.time_to_neighbor[city1] + new_cost + float(cost)
            self.route_cost = self.time_to_neighbor[city1] + float(cost)
        elif option == 'scenic':
            self.route_cost = self.is_highway[city1] + cost


##########################################################
# Miscellaneous Functions
##########################################################

# Haversine implementation for Python, as discussed on StackOverflow
# http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
# Calculates the great circle distance in km between two points on the earth (specified in decimal degrees)
def calculate_distance(lat1, lon1, lat2, lon2):

    # converts decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    miles = km / 1.609344
    return miles

# Calculates average speed limit across all roads, ignoring those with missing data
def calculate_average_speed_limit(road_file):
    total_speed_limit = 0
    count = 0
    for y in road_file:
        if y[3] != '0' or y[3] != '':
            total_speed_limit += int(y[3])
            count += 1
    mean_speed_limit = float(total_speed_limit) / count
    return mean_speed_limit

def generate_successors2(city_name, road_directory):
    city_node = road_directory[city_name]
    return [z for z in city_node.neighbor]

##########################################################
# Routing Algorithms
##########################################################


# Breadth-First Search
# Finds the shortest path in terms of graph depth by using a queue to explore succcessors
def bfs(start_city, end_city, routing_option, directory):
    # Initialize Queue
    fringe = Q.Queue()
    # Put first node into queue
    fringe.put(start_city)

    directory[start_city].route.append(start_city)
    while not fringe.empty():
        # Explore first element in fringe
        current_city = fringe.get()

        # Each successor is a node corresponding to each neighbor
        current_successors = generate_successors2(current_city, directory)

        # Check if current city is goal city. If it is, return cost and route
        if current_city == end_city:
            directory[current_city].route.append(current_city)
            final_route = [start_city]
            final_route.extend(directory[current_city].route)
            return final_route

        # Check if we have explored this option before
        elif not directory[current_city].explored:
            directory[current_city].explored = True

            # Generate cost of each successor
            for s in current_successors:
                directory[s].update_cost(current_city, directory[current_city].route_cost, routing_option)

            cur_successors_costs = {}
            for k in current_successors:
                cur_successors_costs[k] = directory[k].route_cost

            # Sort successors based on cost from smallest to largest using sorted() function, then add each successor
            # to fringe and add to route
            # http://stackoverflow.com/questions/12791923/using-sorted-in-python
            sorted_successors = sorted(cur_successors_costs.items(), key=operator.itemgetter(1), reverse=False)
            for t in sorted_successors:
                fringe.put(t[0])
                directory[t[0]].route.append(current_city)


# Depth-First Search
# Uses a farther path in terms of graph depth by exploring successors using a stack instead of queue
def dfs(start_city, end_city, routing_option, directory):
    # Initialize Queue
    fringe = []
    fringe.append(start_city)

    while len(fringe) > 0:
        # Explore first element in fringe
        current_city = fringe.pop()

        # Each successor is a node corresponding to each neighbor
        current_successors = generate_successors2(current_city, directory)

        # Check if current city is goal city. If it is, return cost and route
        if current_city == end_city:
            directory[current_city].route.append(current_city)
            final_route = [start_city]
            final_route.extend(directory[current_city].route)
            return final_route

        # Check if we have explored this option before
        elif not directory[current_city].explored:
            directory[current_city].explored = True

            # Generate cost of each successor
            for s in current_successors:
                directory[s].update_cost(current_city, directory[current_city].route_cost, routing_option)

            cur_successors_costs = {}
            for k in current_successors:
                cur_successors_costs[k] = directory[k].route_cost

            # Sort successors based on cost from smallest to largest using sorted() function, then add each successor
            # to fringe and add
            # http://stackoverflow.com/questions/12791923/using-sorted-in-python

            sorted_successors = sorted(cur_successors_costs.items(), key=operator.itemgetter(1), reverse=True)
            for t in sorted_successors:
                fringe.append(t[0])
                directory[t[0]].route.append(current_city)



# Iterative Deepening Search
# Same as Depth-First Search but searches by iteratively increasing depth
def ids(start_city, end_city, routing_option, directory):
    # Initialize Queue
    fringe = []
    fringe.append(start_city)
    n = 1

    while 1:
        for i in range(0,n):
            # Explore first element in fringe
            current_city = fringe.pop()

            # Each successor is a node corresponding to each neighbor
            current_successors = generate_successors2(current_city, directory)

            # Check if current city is goal city. If it is, return cost and route
            if current_city == end_city:
                directory[current_city].route.append(current_city)
                final_route = [start_city]
                final_route.extend(directory[current_city].route)
                return final_route

            # Check if we have explored this option before
            elif not directory[current_city].explored:
                directory[current_city].explored = True

                # Generate cost of each successor
                for s in current_successors:
                    directory[s].update_cost(current_city, directory[current_city].route_cost, routing_option)

                cur_successors_costs = {}
                for k in current_successors:
                    cur_successors_costs[k] = directory[k].route_cost

                # Sort successors based on cost from smallest to largest using sorted() function, then add each successor
                # to fringe and add
                # http://stackoverflow.com/questions/12791923/using-sorted-in-python

                sorted_successors = sorted(cur_successors_costs.items(), key=operator.itemgetter(1), reverse=True)
                for t in sorted_successors:
                    fringe.append(t[0])
                    directory[t[0]].route.append(current_city)
        n += 1



# AStar Search
# Extracts path by using a priority queue and uses a heuristic when calculating cost
def astar(start_city, end_city, routing_option, directory, coordinates, average_speed_limit):
    # Same as bfs but uses priority queue instead of queue
    # Initialize Queue
    fringe = Q.PriorityQueue()
    # Put first node into queue
    fringe.put(start_city)

    while not fringe.empty():
        # Explore first element in fringe
        current_city = fringe.get()

        # Each successor is a node corresponding to each neighbor
        current_successors = generate_successors2(current_city, directory)

        # Check if current city is goal city. If it is, return cost and route
        if current_city == end_city:
            directory[current_city].route.append(current_city)
            final_route = [start_city]
            final_route.extend(directory[current_city].route)
            return final_route

        # Check if we have explored this option before
        elif not directory[current_city].explored:
            directory[current_city].explored = True

            # Generate cost of each successor
            for s in current_successors:
                directory[s].update_heuristic(current_city, s, coordinates, directory[current_city].route_cost,
                                              routing_option, average_speed_limit)

            cur_successors_costs = {}
            for k in current_successors:
                cur_successors_costs[k] = directory[k].route_cost

            # Sort successors based on cost from smallest to largest using sorted() function, then add each successor
            # to fringe and add
            # http://stackoverflow.com/questions/12791923/using-sorted-in-python

            sorted_successors = sorted(cur_successors_costs.items(), key=operator.itemgetter(1), reverse=False)
            for t in sorted_successors:
                fringe.put(t[0])
                directory[t[0]].route.append(current_city)


##########################################################
# Main Function
##########################################################

if __name__ == '__main__':
    start = time.time()
    # read in city-gps file, append into list
    city_info = []
    with open('city-gps.txt') as f:
        for line in f:
            city = [r.strip() for r in line.split(' ')]
            city_info.append(city)

    # Create a dictionary containing all the cities and their corresponding GPS coordinates
    coordinates = {}
    for line in city_info:
        coordinates[line[0]] = [line[1]]
        coordinates[line[0]].append(line[2])

    # Read in road-segments file, append into list only the lines that don't have missing values
    road_info = []
    road_directory = {}
    input_row = [line.split(" ") for line in open("road-segments.txt", "r")]
    for road in input_row:
        if road[2] != '0' and road[2] != '' and road[3] != '0' and road[3] != '' and road[4] != '':
            road_info.append(road)
            # If the road is not in road_directory
            if road[0] not in road_directory:
                # if we don't have gps data for it, replace the gps information with blanks
                if road[0] not in coordinates:
                    coordinates[road[0]] = ['', '']
                x = Node(road[0], coordinates[road[0]])
                x.store_road_information(road[1], int(road[2]), int(road[3]), road[4])
                road_directory[road[0]] = x
            else:
                # if the city is in the road_directory, that means no need to initialize node
                road_directory[road[0]].store_road_information(road[1], int(road[2]), int(road[3]), road[4])
            if road[1] not in road_directory:
                if road[1] not in coordinates:
                    coordinates[road[1]] = ['', '']
                x = Node(road[0], coordinates[road[0]])
                x.store_road_information(road[0], int(road[2]), int(road[3]), road[4])
                road_directory[road[1]] = x
            else:
                road_directory[road[1]].store_road_information(road[0], int(road[2]), int(road[3]), road[4])
                

    # store arguments into variables
    start_city, end_city, routing_option, routing_algorithm = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]


    # find average speed limit (for time heuristic)
    average_speed_limit = calculate_average_speed_limit(road_info)

    # check to make sure user did not input invalid cities
    if start_city not in coordinates:
        print "Invalid start city! Please try again."
        sys.exit()
    if end_city not in coordinates:
        print "Invalid end city! Please try again."
        sys.exit()

    options = ['segments', 'distance', 'time', 'scenic']
    if routing_option not in options:
        print 'Invalid routing option! Please try again.'

    # Choose routing algorithm
    if routing_algorithm == 'bfs':
        route = bfs(start_city, end_city, routing_option, road_directory)
    elif routing_algorithm == 'dfs':
        route = dfs(start_city, end_city, routing_option, road_directory)
    elif routing_algorithm == 'ids':
        route = ids(start_city, end_city, routing_option, road_directory)
    elif routing_algorithm == 'astar':
        route = astar(start_city, end_city, routing_option, road_directory, coordinates, average_speed_limit)
    else:
        print 'Invalid routing algorithm! Please try again.'

    # Print cost and path
    print ' '.join(route)  # print route
    end = time.time()
    print 'runtime: ' + str(end-start)

