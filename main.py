import heapq
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
    graph = defaultdict(set)
    tube_lines = defaultdict(set)
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
                tube_lines[lines[i].strip()].add(line_name)
                if i != 0:
                    station1 = stations[-2]
                    station2 = stations[-1]

                    graph[(station1, line_name)].add(station2)
                    graph[(station2, line_name)].add(station1)

    return graph, list(set(stations)), tube_lines


if __name__ == "__main__":
    graph, station_set, tube_lines = build_graph()

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
    fail = False
    while curr_node != destination:
        next_station = input(f"You are at {curr_node}. Type the next station: ")
        if next_station == "q":
            fail = True
            break
        if next_station == curr_node:
            print(f"You're already at {next_station}, go somewhere else.")
        if next_station not in station_set:
            print("Such a station does not exist. Try again.")
            invalid_stations.append(next_station)
            continue

        places_to_go_from_current_node = set()
        for line in tube_lines[curr_node]:
            for v in graph[curr_node, line]:
                places_to_go_from_current_node.add(v)
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

    if not fail:
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
    else:
        print("You failed!")

    distance_graphs = []
    for line in tube_lines[start]:
        distances = defaultdict(lambda: (float('inf'), float('inf'), None))
        pq = []  # distance, num_changes, current_node, curr_line, previous node
        heapq.heappush(pq, (0, 0, (start, line), None))
        distances[start, line] = (0, 0, None)
        i = 0
        while pq:
            distance, num_changes, curr_node, previous_node = heapq.heappop(pq)
            # work from here
            neighbours = []
            for next_line in tube_lines[curr_node[0]]:
                if next_line == curr_node[1]:
                    continue
                if (distances[curr_node[0], next_line][0], distances[curr_node[0], next_line][1]) > (distance, num_changes + 1):
                    distances[curr_node[0], next_line] = (distance, num_changes+1, curr_node)
                    heapq.heappush(pq, (distance, num_changes + 1, (curr_node[0], next_line), curr_node))

            for station in graph[curr_node]:
                if (distances[station, curr_node[1]][0], distances[station, curr_node[1]][1]) > (distance+1, num_changes):
                    distances[station, curr_node[1]] = (distance+1, num_changes, curr_node)
                    heapq.heappush(pq, (distance + 1, num_changes, (station, curr_node[1]), curr_node))

        distance_graphs.append(distances)

    best_graph = -1
    best_distance = (10000000, 100000000, None)
    solution = best_distance
    for i in range(len(distance_graphs)):
        distances = distance_graphs[i]
        total = min([distances[destination, k] for k in tube_lines[destination]])
        if total < best_distance:
            best_distance = total
            best_graph = i

    distances = distance_graphs[best_graph]
    solution = min(distances[destination, i] for i in tube_lines[destination])
    print(f"The optimal solution had length {solution[0]}.")
    path = []
    current_node = solution
    while True:
        path.append(current_node)
        current_node = distances[current_node[2]]
        if not current_node[2]:
            break

    print(
        f"Start at {colours[path[-1][2][1]]}{start}{Style.reset} on the {colours[path[-1][2][1]]}{path[-1][2][1]}{Style.reset} line.")
    last_station = start
    for _, _, (station, line) in path[::-1][1:]:
        if last_station == station:
            print(f"Change to the {colours[line]}{line}{Style.reset} line.")
            curr_line = line
        else:
            print(f"Proceed to {colours[line]}{station}{Style.reset}.")

        last_station = station

    print(f"Finally, proceed to {colours[line]}{destination}{Style.reset}.")