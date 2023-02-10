import requests
import time
import random

api_url = "https://bots-of-black-friday-helsinki.azurewebsites.net"
bot_name = 'Raaka-Bot'
visited_coords = []

def register():
    response = requests.post(f"{api_url}/register",
                             json={
                                 "playerName": bot_name
                             }
                             )
    return response.json()


def gamestate():
    return requests.get(f"{api_url}/gamestate").json()


def move(playerId, direction):
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
    print(f'Mapstate is {mapstate_zero}')
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
    x = origin['x']
    y = origin ['y']
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

if __name__ == '__main__':
    register_response = register()
    id = register_response['id']
    player = register_response['player']
    map = register_response['map']
    map_width = len(map['tiles'][0])
    map_height = len(map['tiles'])
    print(f'Map size: {map_width} X {map_height}')
    exit_tile = calculate_exit_tile_coords(map)
    exit_tile_char = map['tiles'][exit_tile[1]][exit_tile[0]]
    print(f'Exit tile at {exit_tile} with value {exit_tile_char}')

    while True:
        time.sleep(0.5)
        gamestate_response = gamestate()
        my_bot = get_my_bot(bot_name, gamestate_response)
        pos = my_bot['position']
        print(f'Player position is {pos}')
        #my_bot['money'] > 0 and my_bot['health'] > 50
        gather_mode = True if my_bot['score'] == 0 else False
        print(f'Gather mode: {gather_mode}')
        if gather_mode:
            valid_directions = calculate_valid_moves(pos, map)
            print(f'valid moves: {valid_directions}')
            if len(valid_directions) == 0:
                print('Ran out of valid directions, need to finetune the exit rulez :)')
                exit(-1)
            random_move_index = random.randint(0, len(valid_directions)-1)
            selected_dir = valid_directions[random_move_index]
            destination_coords = calculate_destination_coords(pos, selected_dir)
            visited_coords.append(destination_coords)        
            print(f'Moving player {id} to {selected_dir} from {pos} to {destination_coords}')
            # Calculate possible ways to move
            # Move to possible way
            move(id, selected_dir)
            time.sleep(0.5)
        else:
            print('Go to exit mode, not implemented yet, but go to o')
            # Map is 92 X 28
            # Cashier is 9,4
            if pos['y'] > 2:
                move(id, 'UP')
            elif pos['x'] > 4:
                move(id, 'LEFT')
            elif pos['x'] < 4:
                move(id, 'RIGHT')
            else:
                move(id, 'DOWN')
            time.sleep(0.5)                
            # if pos['x'] >                 

            # Need pathfinding, how to move closer to o, while dodging the walls
            # Can hardcode this, if not in middle, move up/down whichever is closer, then move to same col as o, then move up/down to it
         