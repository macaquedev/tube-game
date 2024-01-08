import os
from collections import defaultdict, deque
import random
from colored import Fore, Style


colours = {
    "Bakerloo": Fore.RGB(0x84, 0x39, 0),
    "Central": Fore.RGB(0xD3, 0x35, 0x2C),
    "Circle": Fore.RGB(0xEB, 0xD2, 0x37),
    "District": Fore.green,
    "Hammersmith&City": Fore.RGB(0xDA, 0x84, 0x9D),
    "Jubilee": Fore.RGB(0x9B, 0x99, 0xA3),
    "Metropolitan": Fore.RGB(0x9B, 0x04, 0x5E),
    "Northern": Fore.RGB(0xFF, 0xFF, 0xFF),
    "Piccadilly": Fore.RGB(0x10, 0x31, 0x74),
    "Victoria": Fore.RGB(0x1C, 0x9C, 0xD0),
    "Waterloo&City": Fore.RGB(0x7D, 0xC6, 0xB3)
}

def build_graph():
    stations = []
    graph = defaultdict(lambda: defaultdict(set))
    for path in os.listdir("lines"):
        if not path.endswith(".txt"):
            continue
        line_name = path.removesuffix(".txt").split("-")[0].title()
        branch_name = " ".join(i.title() for i in path.removesuffix(".txt").split("-")[1:])
        if len(branch_name) == 0:
            branch_name = "main"
        with open(os.path.join("lines", path)) as f:
            lines = f.readlines()
            for i in range(len(lines)):
                stations.append(lines[i].strip())
                if i != 0:
                    station1 = stations[-2]
                    station2 = stations[-1]

                    graph[station1][(line_name, branch_name)].add(station2)
                    graph[station2][(line_name, branch_name)].add(station1)

    return graph, list(set(stations))


if __name__ == "__main__":
    graph, station_set = build_graph()

    start = random.choice(station_set)
    destination = random.choice(station_set)
    while start == destination:
        destination = random.choice(station_set)
    print(f"Your starting point is: {start}.")
    print(f"Your finishing point is: {destination}.")

    curr_node = start
    user_path = [start]
    invalid_stations = []
    already_seen_stations = []
    wrong_moves = []
    seen = set()
    while curr_node != destination:
        next_station = input(f"You are at {curr_node}. Type the next station: ")
        if next_station == curr_node:
            print(f"You're already at {next_station}, go somewhere else.")
        if next_station not in station_set:
            print("Such a station does not exist. Try again.")
            invalid_stations.append(next_station)
            continue

        places_to_go_from_current_node = set()
        for v in graph[curr_node].values():
            places_to_go_from_current_node = places_to_go_from_current_node.union(v)

        if next_station not in places_to_go_from_current_node:
            print("You cannot go there from this station. Try again.")
            wrong_moves.append((curr_node, next_station))
            continue

        if next_station in seen:
            print("You have already visited this station.")
            already_seen_stations.append(next_station)

        seen.add(next_station)
        user_path.append(next_station)
        curr_node = next_station
    
    print("Well done! You have reached your destination!")
    print(f"This took you {len(user_path)-1} steps.\n")
    if invalid_stations:
        print("Invalid stations tested:")
        for station in invalid_stations:
            print(station)
        print()
    if already_seen_stations:
        print("You visited these stations multiple times: ")
        for station in already_seen_stations:
            print(station)

    start = "Moorgate"
    destination = "East Putney"
    distances = {start: (1, 1, None, None)}
    bfs = deque([(0, 0, start, None, None)])  # distance, num_changes, current_node, curr_line, previous node

    while bfs:
        distance, num_changes, curr_node, curr_line, previous_node = bfs.popleft()

        if curr_node in distances and (distance >= distances[curr_node][0] or num_changes >= distances[curr_node][1]):
            continue
        distances[curr_node] = (distance, num_changes, previous_node, curr_line)

        neighbours = []
        for line_info, station_set in graph[curr_node].items():
            for station in station_set:
                neighbours.append((line_info[0], station))

        immediate_neighbours = set()
        for key in graph[curr_node]:
            if key[0] == curr_line or curr_line is None:
                immediate_neighbours = immediate_neighbours.union(graph[curr_node][key])

        for line, neighbour in neighbours:
            if neighbour in immediate_neighbours:
                bfs.append((distance+1, num_changes, neighbour, curr_line or line, curr_node))
            else:
                bfs.append((distance+1, num_changes+1, neighbour, line, curr_node))

    print(f"The optimal solution had length {distances[destination][0]}.")
    path = []
    current_node = destination
    while current_node != start:
        path.append((current_node, distances[current_node][3]))
        current_node = distances[current_node][2]
        if current_node == start:
            path.append((start, path[-1][1]))

    print(f"Start at {colours[path[-1][1]]}{start}{Style.reset} on the {colours[path[-1][1]]}{path[-1][1]}{Style.reset} line.")
    curr_line = path[-1][1]
    for station, line in path[::-1][1:]:
        if line != curr_line:
            print(f"Change to the {colours[line]}{line}{Style.reset} line.\n"
                  f"Proceed to {colours[line]}{station}{Style.reset}.")
            curr_line = line
        else:
            print(f"Proceed to {colours[line]}{station}{Style.reset}.")

