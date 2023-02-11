import requests
import time
import random
import math

api_url = "https://bots-of-black-friday-helsinki.azurewebsites.net"
bot_name = 'Raaka-Bot'
visited_coords = []
MIN_HEALTH=30
HIGH_SCORE=6000
current_health = 100

def register():
    response = requests.post(f"{api_url}/register",
                             json={
                                 "playerName": bot_name
                             }
                             )
    return response.json()


def gamestate():
    return requests.get(f"{api_url}/gamestate").json()


def act(playerId, direction):
    requests.put(f"{api_url}/{playerId}/move",
                 json=direction
                 )


def get_my_bot(bot_name, gamestate_response):
    my_bot = [player for player in gamestate_response['players']
              if player['name'] == bot_name]
    print(my_bot)
    if len(my_bot) != 1:
        print('My bot not visible anymore! We are done! (Or it has split personality)')
        exit(0)
    return my_bot[0]


def calculate_valid_moves(pos, map):
    x = pos['x']
    y = pos['y']
    mapstate_zero = map['tiles'][y][x]
    mapstate_up = map['tiles'][y-1][x]
    mapstate_down = map['tiles'][y+1][x]
    mapstate_left = map['tiles'][y][x-1]
    mapstate_right = map['tiles'][y][x+1]
    # print(f'Mapstate is {mapstate_zero}')
    for iy in range(y-1,y+1):
        for ix in range(x-1,x+1):
            print(map['tiles'][iy][ix])
    valid_directions = []
    print(mapstate_up, mapstate_down, mapstate_left, mapstate_right)
    valid_destinations = ['_','o']
    if mapstate_up in valid_destinations:# and (x,y-1) not in visited_coords:
        valid_directions.append('UP')
    if mapstate_down in valid_destinations:# and (x,y+1) not in visited_coords:
        valid_directions.append('DOWN')
    if mapstate_left in valid_destinations:# and (x-1,y) not in visited_coords:
        valid_directions.append('LEFT')
    if mapstate_right in valid_destinations:# and (x+1,y) not in visited_coords:
        valid_directions.append('RIGHT')
    return valid_directions

def calculate_destination_coords(origin, direction):
    x = origin[0]
    y = origin [1]
    if direction == 'UP':
        y = y -1
    if direction == 'DOWN':
        y = y +1
    if direction == 'LEFT':
        x = x -1
    if direction == 'RIGHT':
        x = x +1
    return (x,y)

def calculate_exit_tile_coords(map):
    map_tiles = map['tiles']
    for y in range(0,len(map_tiles)):
        for x in range(0,len(map_tiles[0])):
            if map_tiles[y][x] == 'o':
                return (x,y)


destination = None

def tick(id,map):
    global destination
    global current_health
    gamestate_response = gamestate()
    my_bot = get_my_bot(bot_name, gamestate_response)
    if my_bot['health'] != current_health:
        print(f"*** Health changed from {current_health} to {my_bot['health']}!")
        current_health = my_bot['health']
    destination = decide_destination(gamestate_response)
    # if my_bot['health'] < MIN_HEALTH:
    #     destination = decide_destination(gamestate_response)
    if len(my_bot['usableItems']) > 0:
        if len(gamestate_response['players']) > 1:
            item = my_bot['usableItems'][0]
            print(f'Got a gun, and there''s another player on board, let''s shoot! {item}')        
            act(id, 'USE')
            return
#    if destination == None:
    pos = (my_bot['position']['x'],my_bot['position']['y'])
    #print(f'Player position is {pos}, moving towards {destination}')
    if pos == destination and my_bot['state'] != 'PICK':
        destination_items = [item for item in gamestate_response['items'] if item['position']['x'] == destination[0] and item['position']['y'] == destination[1]]
        if len(destination_items) == 1:
            price = destination_items[0]['price']*destination_items[0]['discountPercent']/100
            if my_bot['money'] >= price:
                #print(f'**** Gamestate just before picking up item {gamestate_response}')
                act(id, 'PICK')
                destination = None
                return
    direction = ''
    if pos[0] > destination[0]:
        direction = 'LEFT'
    elif pos[0] < destination[0]:
        direction = 'RIGHT'
    elif pos[1] > destination[1]:
        direction = 'UP'
    elif pos[1] < destination[1]:
        direction = 'DOWN'
    else:
        print('Reached the goal! Let''s pickup next round')
    destination_coords = calculate_destination_coords(pos, direction)
    #print(f'Want to move to direction {direction} to coords {destination_coords}')
    if (map['tiles'][destination_coords[1]][destination_coords[0]]) == 'x':
        print('Invalid move, would move to wall, so let''s move up')
        act (id, 'UP')
    else:
        act(id, direction)
    

    # TODO
    # Decide destination. In this case, 9, 4
    # gamestate_response['items']
    # make one move towards it, filter out any invalid moves
    # need some routing to go around the wall

def get_ordered_list(points, x, y):
    # print(f'sorting points {points}')
    points.sort(key = lambda p: (p['position']['x'] - x)**2 + (p['position']['y'] - y)**2)
    return points

def decide_destination(gamestate):
    # TODO: Could dynamically try to figure out best items to pick
    # TODO: Could fetch closest item from list
    # if gamestate['']
    my_bot = get_my_bot(bot_name, gamestate)
    if my_bot['health'] < MIN_HEALTH or my_bot['money'] < 200:
        print('No money, or low health, going for exit')
        return (9,4) # Exit

    #print(f"Items before filtering by money: {gamestate['items']}")
    items = [item for item in gamestate['items'] if item['price']*item['discountPercent']/100 <= my_bot['money']]
    #print(f'Items after filtering by money: {items}')

    # if my_bot['health'] < 50:
    #     print('Health below 50, pick up only potions')
    #     potions = [item for item in gamestate['items'] if item['type'] == 'POTION']
    #     if len(potions) > 0:
    #         print('Health less than 50, and potions exist, pick up potions')
    #         items = potions
    # else:
    #     valuables = [item for item in gamestate['items'] if item['type'] != 'POTION']
    #     if len(valuables) > 0:
    #         print('Health more than 50, and valuables exist, pick up valuables')
    #         items = valuables
    
    if len(items) == 0:
        print('No items, going for exit')
        return (9,4) # Exit
    else:        
        weapons = [item for item in items if item['type'] == 'WEAPON']
        #print(f'Weapons after filtering by type: {weapons}')
        if len(weapons) > 0:
            #print('Found at least one weapon, so let''s go for closest weapon!')
            items = weapons
        else:
            print('No weapons on board, so let''s go for nearest other item')
            #print(f'Items that we checked: {items}')
        items = get_ordered_list(items,my_bot['position']['x'],my_bot['position']['y'])
        item = items[0]
        # print(f'Yes items, going for {item}')
        return (item['position']['x'],item['position']['y'])


if __name__ == '__main__':
    register_response = register()
    id = register_response['id']
    player = register_response['player']
    map = register_response['map']
    while True:
        time.sleep(0.5)
        tick(id, map)
    