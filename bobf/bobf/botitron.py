import requests
import time
import random
import math

api_url = "https://bots-of-black-friday-helsinki.azurewebsites.net"
#api_url = "http://localhost:8080"
bot_name = "Raaka-Bot"
visited_coords = []
MIN_HEALTH = 30
HIGH_SCORE = 6000
current_health = 100


def register():
    response = requests.post(f"{api_url}/register", json={"playerName": bot_name})
    return response.json()


def gamestate():
    return requests.get(f"{api_url}/gamestate").json()


def act(playerId, direction):
    requests.put(f"{api_url}/{playerId}/move", json=direction)


def get_my_bot(bot_name, gamestate_response):
    my_bot = [
        player for player in gamestate_response["players"] if player["name"] == bot_name
    ]
    if len(my_bot) != 1:
        return None
    else:
        return my_bot[0]


def calculate_valid_moves(pos, map):
    x = pos["x"]
    y = pos["y"]
    mapstate_zero = map["tiles"][y][x]
    mapstate_up = map["tiles"][y - 1][x]
    mapstate_down = map["tiles"][y + 1][x]
    mapstate_left = map["tiles"][y][x - 1]
    mapstate_right = map["tiles"][y][x + 1]
    # print(f'Mapstate is {mapstate_zero}')
    # for iy in range(y - 1, y + 1):
    #     for ix in range(x - 1, x + 1):
    #         print(map["tiles"][iy][ix])
    valid_directions = []
    #print(mapstate_up, mapstate_down, mapstate_left, mapstate_right)
    valid_destinations = ["_", "o"]
    if mapstate_up in valid_destinations:  # and (x,y-1) not in visited_coords:
        valid_directions.append("UP")
    if mapstate_down in valid_destinations:  # and (x,y+1) not in visited_coords:
        valid_directions.append("DOWN")
    if mapstate_left in valid_destinations:  # and (x-1,y) not in visited_coords:
        valid_directions.append("LEFT")
    if mapstate_right in valid_destinations:  # and (x+1,y) not in visited_coords:
        valid_directions.append("RIGHT")
    return valid_directions


def calculate_destination_coords(origin, direction):
    x = origin[0]
    y = origin[1]
    if direction == "UP":
        y = y - 1
    if direction == "DOWN":
        y = y + 1
    if direction == "LEFT":
        x = x - 1
    if direction == "RIGHT":
        x = x + 1
    return (x, y)


def calculate_exit_tile_coords(map):
    map_tiles = map["tiles"]
    for y in range(0, len(map_tiles)):
        for x in range(0, len(map_tiles[0])):
            if map_tiles[y][x] == "o":
                return (x, y)


destination = None


def tick(id, map):
    print(f"TICK:", end=" ")
    global destination
    global current_health
    gamestate_response = gamestate()
    #print(f"gamestate response:\n{gamestate_response}")
    my_bot = get_my_bot(bot_name, gamestate_response)
    if my_bot == None:
        print("\tBot is gone, run is done.")
        exit(0)
    if my_bot["state"] == "PICK":
        print("\tPicking up, no new commands")
        return
    # if my_bot['health'] != current_health:
    #     # print(f"*** Health changed from {current_health} to {my_bot['health']}!")
    #     current_health = my_bot['health']
    destination = decide_destination(gamestate_response)
    # if my_bot['health'] < MIN_HEALTH:
    #     destination = decide_destination(gamestate_response)
    if len(my_bot["usableItems"]) > 0:
        if len(gamestate_response["players"]) > 1:
            item = my_bot["usableItems"][0]
            print(f"\tSHOOT {item}")
            act(id, "USE")
            return
    #    if destination == None:
    pos = (my_bot["position"]["x"], my_bot["position"]["y"])
    # print(f'Player position is {pos}, moving towards {destination}')
    if pos == destination and my_bot["state"] != "PICK":
        print('**** On top of item, and not picking it up yet, so let''s pick it up')
        # print('On top of something, and not yet picking it, let''s see if we can pick it')
        destination_items = [
            item
            for item in gamestate_response["items"]
            if item["position"]["x"] == destination[0]
            and item["position"]["y"] == destination[1]
        ]
        # if len(destination_items) == 1:
        #     print(f'Found 1 item we can try to pick: {destination_items}')
        #     price = destination_items[0]['price']*destination_items[0]['discountPercent']/100
        #     # TODO: This does not work right, bot tries to pickup item and does not have enough money, so gets killed
        discount = destination_items[0]["discountPercent"]
        value = destination_items[0]["price"]
        discount_price = value * (1-discount/100)
        print(
            f"Item is {destination_items[0]} with discounted price of {discount_price} and true value of {value}"
        )
        if my_bot["money"] >= discount_price:
            print(f"\tPICK UP ITEM {destination_items[0]}")
            act(id, "PICK")
            destination = None
            return
        else:
            print(f'My bot did not have enough money! Bot money {my_bot["money"]} vs {discount_price}')
            destination = decide_destination(gamestate_response)
    direction = ""
    if pos[0] > destination[0]:
        direction = "LEFT"
    elif pos[0] < destination[0]:
        direction = "RIGHT"
    elif pos[1] > destination[1]:
        direction = "UP"
    elif pos[1] < destination[1]:
        direction = "DOWN"
    else:
        print("Reached the goal! Let" "s pickup next round")
        return  # Possibly beneficial bug to register empty move?
    destination_coords = calculate_destination_coords(pos, direction)
    # print(f'Want to move to direction {direction} to coords {destination_coords}')
    # TODO: Theoretically could hit the outer border too, should take care of the invalid moves in more clever fashion
    # TODO: We should always have at least one valid move to take
    if (map["tiles"][destination_coords[1]][destination_coords[0]]) == "x":
        print(f"\tInvalid move to {direction}, would move to wall, so let" "s move up/down")
        if pos[1] < 28/2:
            act(id, "UP")
        else:
            act(id, "DOWN")                        
    else:
        print(f"\t MOVE TO {direction}")
        act(id, direction)

    # TODO
    # Decide destination. In this case, 9, 4
    # gamestate_response['items']
    # make one move towards it, filter out any invalid moves
    # need some routing to go around the wall


def sort_by_distance(items, x, y):
    items.sort(
        key=lambda p: (p["position"]["x"] - x) ** 2 + (p["position"]["y"] - y) ** 2
    )
    return items


def sort_by_discount(items):
    items.sort(key=lambda p: (p["discountPercent"]), reverse=True)
    return items


def decide_destination(gamestate):
    my_bot = get_my_bot(bot_name, gamestate)
    if my_bot["health"] < MIN_HEALTH or my_bot["money"] < 400:
        print("No money, or low health, going for exit")
        return (9, 4)  # Exit
    
    # TODO: Perhaps add another end condition:
    # TODO: If none of the items on map can be picked up with the money you have
    # TODO: Set a timer, count for 10 rounds, and then head for exit
    # TODO: Alternatively, dabble a bit with the threshold, for example can you buy stuff if you have $400? Probably not easily. 
    # TODO: But yes it is random generated, discounts could be up to 82%, so a cheap weapon could be bought for low moneys



    # Filter out items that are too expensive to pickup anyways
    items = [item for item in gamestate["items"] if item["price"]*(1-item["discountPercent"]/100) <= my_bot["money"]]

    # Filter out items with lousy discount %
    items = [item for item in gamestate["items"] if item["discountPercent"] == 0 or item["discountPercent"] > 40]

    # Alternative: Filter out items that are not potions or weapons - note: requires other players on map, this is TERMINATOR MODE
    #items = [item for item in gamestate["items"] if item["type"] in ['POTION','WEAPON']]

    potions = [item for item in gamestate["items"] if item["type"] == "POTION"]
    valuables = [item for item in gamestate["items"] if item["type"] != "POTION"]

    # TODO: Somehow seems as if the distance algorithm is not working quite right, at least with potions it may pick one farther/farthest away
    # TODO: Distance should be calculated including the obstacles, this require path-finding algo. 
    # TODO: Path-finding algo would also let up play on more complex maps

    # If health is lower then 70, drain those beers to keep on going and reveal more items
    if my_bot["health"] < 60:
        # Health is low, pickup potions
        items = sort_by_distance(potions, my_bot["position"]["x"], my_bot["position"]["y"])
    elif len(valuables) > 0:
        # There are valuables, so sort them by discount and pickup closest
        items = sort_by_discount(items)
    else:
        # Just pick up the closest item, it's probably a potion
        items = sort_by_distance(items, my_bot["position"]["x"], my_bot["position"]["y"]) 

    # Hoover mode: Just pickup items by proximity to cleanup board
    # items = sort_by_distance(items, my_bot["position"]["x"], my_bot["position"]["y"])

    if len(items) == 0:
        print("No suitable items to pick, going for exit")
        return (9, 4)  # Exit

    # # TODO: Let's sort items by their discount % and instead of picking up closest, pick up cheapest?
    # # This would automatically prefer weapons too, and would maximize the results
    # weapons = [item for item in items if item["type"] == "WEAPON"]
    # # print(f'Weapons after filtering by type: {weapons}')
    # if len(weapons) > 0:
    #     # print('Found at least one weapon, so let''s go for closest weapon!')
    #     items = weapons
    # else:
    #     # print('No weapons on board, so let''s go for nearest other item')
    #     # print(f'Items that we checked: {items}')
    #     pass
    
    item = items[0]
    print(f'Destination is item {item}')
    return (item["position"]["x"], item["position"]["y"])


if __name__ == "__main__":
    register_response = register()
    id = register_response["id"]
    player = register_response["player"]
    map = register_response["map"]
    moves = calculate_valid_moves(player["position"], map)
    print(f"First move from {player['position']} to {moves[0]}")
    act(id, moves[0])  # Try to register empty move to avoid penalties
    gamestate_response = gamestate()
    my_bot = get_my_bot(bot_name, gamestate_response)
    while my_bot == None:
        gamestate_response = gamestate()
        my_bot = get_my_bot(bot_name, gamestate_response)
        time.sleep(0.1)
    print("Found my bot! Let" "s go!")

    while True:
        tick(id, map)
        time.sleep(0.3)
