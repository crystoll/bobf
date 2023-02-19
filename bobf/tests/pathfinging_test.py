from copy import deepcopy
import json
from bobf.pathfinder import PathFinder


def print_route_on_map(map, start, end, route):
    """
    Here we make a nice copy of the map tiles, and route,
    we remove last element from route (because it should be the end pos),
    and plot route bits as *, start position as @, and end position as $
    on the map tiles, so we can visualize how the route went.

    :param map:     the response map from the game
    :param start:   starting position as a tuple of (x, y)
    :param end:     ending position as a tuple of (x, y)
    :param route:   deque of tuple routepoints excluding start pos but including end pos
    """
    route = deepcopy(list(route))[:-1]
    tiles = deepcopy(map["tiles"])
    for i, item in enumerate(tiles):
        tiles[i] = list(tiles[i])
    tiles[start[1]][start[0]] = "@"
    for item in route:
        tiles[item[1]][item[0]] = "*"
    tiles[end[1]][end[0]] = "$"
    for row in tiles:
        for col in row:
            print(col, end="")
        print()


def test_helsinki_map_pathfinding():
    with open("../samples/register_response_sample.json") as f:
        response_sample = json.load(f)
    map = response_sample["map"]
    pathfinder = PathFinder(map)
    pos1, pos2 = [(2, 2), (5, 5)]
    route = pathfinder.find_route(pos1, pos2)
    print_route_on_map(map, pos1, pos2, route)
    assert list(route) == [(3, 2), (4, 2), (5, 2), (5, 3), (5, 4), (5, 5)]

