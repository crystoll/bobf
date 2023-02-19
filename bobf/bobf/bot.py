from game_client import GameClient
from pathfinder import PathFinder
import time
import random 
import json

class Bot:

    STRATEGY_TERMINATOR='TERMINATOR'
    STRATEGY_GO_TO_EXIT='GO_TO_EXIT'
    STRATEGY_PICKUP_CLOSEST='PICKUP_CLOSEST'
    STRATEGY_HEAL='HEAL'

    def __init__(self:object, name: str, strategy: str):
        self.name = name
        self.strategy = strategy
        self.game_client = GameClient()
        bot_response = self.game_client.register_bot(self.name)
        # print(json.dumps(bot_response))        
        self.id = bot_response['id']
        self.player = bot_response['player']
        self.map = bot_response['map']
        self.pathfinder = PathFinder(self.map)
        self.make_random_move(self.player['position'])
        my_bot = None
        while my_bot == None:
            gamestate_response = self.game_client.gamestate()
            my_bot = self.get_my_bot(self.name, gamestate_response)
            # self.make_random_move(my_bot['position'])
            time.sleep(0.1)


    def calculate_valid_moves(self, pos):
        x = pos["x"]
        y = pos["y"]
        mapstate_up = self.map["tiles"][y - 1][x]
        mapstate_down = self.map["tiles"][y + 1][x]
        mapstate_left = self.map["tiles"][y][x - 1]
        mapstate_right = self.map["tiles"][y][x + 1]
        valid_directions = []
        if mapstate_up == '_': 
            valid_directions.append("UP")
        if mapstate_down == '_':
            valid_directions.append("DOWN")
        if mapstate_left == '_': 
            valid_directions.append("LEFT")
        if mapstate_right == '_':  
            valid_directions.append("RIGHT")
        return valid_directions

    def make_random_move(self, pos):
        valid_moves = self.calculate_valid_moves(pos)
        random_move = random.choice(valid_moves)
        self.game_client.act(self.id, random_move)


    def get_my_bot(self, bot_name, gamestate_response):
        my_bot = [
            player for player in gamestate_response["players"] if player["name"] == bot_name
        ]
        if len(my_bot) != 1:
            return None
        else:
            return my_bot[0]
        
    def calculate_discounted_price(self, item):
        return item["price"] * (100 - item["discountPercent"]) / 100
    
    def go_home(self, player):
        self.destination_item = None
        exit_pos = (self.map['exit']['x'],self.map['exit']['y'])
        print(f'Out of money or life, heading for exit at {exit_pos}')
        pos1 = (player['position']['x'],player['position']['y'])
        route = self.pathfinder.find_route(pos1, exit_pos)
        self.destination_route = route


    def find_next_destination_and_route(self, gamestate_response):
        player = self.get_my_bot(self.name, gamestate_response)
        if player == None:
            print('No player in gamestate, I suppose we are done.')
            exit(-1)
        if player['money'] < 500 or player['health'] < 30:
            self.go_home(player)
            return
        def sort_by_distance(items, x, y):
            items.sort(
                key=lambda p: (p["position"]["x"] - x) ** 2 + (p["position"]["y"] - y) ** 2
            )
            return items
        def sort_by_discount(items):
            items.sort(key=lambda p: (p["discountPercent"]), reverse=True)
            return items
        affordable_items = [item for item in gamestate_response['items'] if self.calculate_discounted_price(item) <= player['money'] ]
        weapons = [item for item in affordable_items if item['type'] == 'WEAPON']
        potions = [item for item in affordable_items if item['type'] == 'POTION']
        if len(weapons) > 0:
            available_weapons = sort_by_discount(weapons) 
            if len(available_weapons) > 0:
                destination_item = available_weapons[0]
            elif len(affordable_items) > 0:
                destination_item = sort_by_discount(affordable_items)[0]
            else:
                self.go_home(player)
                return
        else:            
            available_potions =  sort_by_distance(potions, player['position']['x'],player['position']['y'])
            if len(available_potions) > 0:
                destination_item = available_potions[0]
            elif len(affordable_items) > 0:
                destination_item = sort_by_discount(affordable_items)[0]                
            else:
                self.go_home(player)
                return
        if not hasattr(self, 'destination_item') or destination_item != self.destination_item:
            self.destination_item = destination_item
            print(f'Destination changed to: {self.destination_item}')
            pos1 = (player['position']['x'],player['position']['y'])
            pos2 = ( destination_item['position']['x'], destination_item['position']['y'])
            route = self.pathfinder.find_route(pos1, pos2)
            # print(f'Found a route! {route}')
            self.destination_route = route

    
    def calculate_move_direction(self, player, route):
        def manhattan_distance(pos1, pos2):
            return abs((pos1[0] - pos2[0])) + abs((pos1[1] - pos2[1]))            

        current_pos = (player['position']['x'],player['position']['y'])
        destinations = [destination for destination in route if manhattan_distance(current_pos, destination) <= 1]
        if len(destinations) == 0:
            print(f'Route has no points that are distance 1 from here, need to find a new route') 
            return None
        destination = destinations[-1]
        # print(f'Selected point {destination} as my goal for this move')
        if player['position']['y'] == destination[1]:
            if player['position']['x'] < destination[0]:
                return 'RIGHT'
            elif player['position']['x'] > destination[0]:
                return 'LEFT'
        elif player['position']['x'] == destination[0]:
            if player['position']['y'] < destination[1]:
                return 'DOWN'
            elif player['position']['y'] > destination[1]:
                return 'UP'
        return None
        

    def tick(self):
        # print('TICK!')
        gamestate_response = self.game_client.gamestate()
        self.find_next_destination_and_route(gamestate_response)
        player = self.get_my_bot(self.name, gamestate_response)
        if player == None:
            print("\tBot is gone, run is done.")
            exit(0)
        self.player = player
        if self.player["state"] == "PICK":
            print("\tPicking up, no new commands")
            self.destination_item = None
            self.destination_route = None
            return
        if len(self.player["usableItems"]) > 0:
            if len(gamestate_response["players"]) > 1:
                item = self.player["usableItems"][0]
                print(f"\tSHOOT {item}")
                self.game_client.act(self.id, "USE")
                return
        
        if self.destination_item != None:
            items_matching_destination = [item for item in gamestate_response['items'] if item == self.destination_item]
            if len(items_matching_destination) == 0:
                print(f'Oops! Our destination item is no longer in gamestate, lets find a new destination')
                self.destination_item == None
                self.destination_route == None
                return
        # TODO: Perhaps limit pickup to chosen destinations, otherwise we could accidentally pickup secondary stuff?            
        items_at_me = [item for item in gamestate_response['items'] if item['position'] == self.player['position']]
        if len(items_at_me) == 1 and items_at_me[0] == self.destination_item:
            item_to_pickup = items_at_me[0]
            discount_price = item_to_pickup["price"] * (100 - item_to_pickup["discountPercent"]) / 100
            if self.player["money"] >= discount_price:
                print(f"\tPICK UP ITEM {item_to_pickup}")
                self.game_client.act(self.id, "PICK")                    
                return
        # TODO: Verify that destination item still exists in gamestate
        # TODO: Verify if we are on top of the desired item, in that case, reset route, and item, get a new destination
        if self.destination_route:
            # print(f'Move towards destination item {self.destination_item} using route {self.destination_route} from origin {self.player["position"]}')
            new_move = self.calculate_move_direction(self.player,self.destination_route) # TODO: hmm due to timing it is possible that we shoot over, and having removed the destination spot are in trouble... Hmm if we cannot reach the tail in one move, recalculate route?
            #print(f'Received move command to move {new_move} to go from {self.player["position"]} to {next_destination}')
            if new_move:
                # print(f'Got a new move to move to {new_move}')
                # self.destination_route.popleft()
                self.game_client.act(self.id, new_move)
            # TODO: Some issue here, we can almost reach the target, but before we pick it up, we start moving randomly                
        # else:
        #     # TODO: Yes, it may be that route pops to empty, and in that case we go here
        #     # TODO: Some issue here, we can almost reach the target, but before we pick it up, we start moving randomly
        #     print(f"\tNo destination nor route: {self.destination_route} -> Move randomly")
        #     self.make_random_move(self.player['position'])



if __name__ == '__main__':
    bot1 = Bot('T1000',Bot.STRATEGY_PICKUP_CLOSEST)
    while True:
        bot1.tick()
        time.sleep(0.2)
