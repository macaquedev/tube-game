import os
from collections import defaultdict

from Levenshtein import distance
import requests
from bs4 import BeautifulSoup


if __name__ == "__main__":
    stations = []
    graph = defaultdict(set)
    for path in os.listdir("lines"):
        if not path.endswith(".txt"):
            continue

        with open(os.path.join("lines", path)) as f:
            lines = f.readlines()

            for i in range(len(lines)):
                stations.append(lines[i].strip())
                if i != 0:
                    graph[lines[i].strip()].add(lines[i-1].strip())
                    graph[lines[i-1].strip()].add(lines[i].strip())

    stations = list(set(stations))
    for i in range(len(stations)):
        for j in range(i+1, len(stations)):
            if (x:=distance(stations[i], stations[j])) < 3:
                print(stations[i], stations[j], x)

    s = set()
    r = requests.get("https://en.wikipedia.org/wiki/List_of_London_Underground_stations")
    soup = BeautifulSoup(r.content, 'html5lib')
    for row in soup.findAll("th", attrs={"scope": "row"}):
        s.add(row.a.text)

    dfs = [(0, "Amersham")]
    visited = set()

    while dfs:
        distance, node = dfs.pop()
        if node in visited:
            continue

        visited.add(node)
        for child in graph[node]:
            dfs.append((distance+1, child))

    print(len(stations), len(s), len(visited))  # should all be equal - no disconnected components
    print(graph["Baker Street"])
