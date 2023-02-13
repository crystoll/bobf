from game_client import GameClient
import time
import random 

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
        self.id = bot_response['id']
        self.player = bot_response['player']
        self.map = bot_response['map']
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

    
    def tick(self):
        print('TICK!', end=" ")
        gamestate_response = self.game_client.gamestate()
        self.player = self.get_my_bot(self.name, gamestate_response)
        if self.player == None:
            print("\tBot is gone, run is done.")
            exit(0)
        if self.player["state"] == "PICK":
            print("\tPicking up, no new commands")
            return
        if len(self.player["usableItems"]) > 0:
            if len(gamestate_response["players"]) > 1:
                item = self.player["usableItems"][0]
                print(f"\tSHOOT {item}")
                self.game_client.act(id, "USE")
                return
        item_at_me = [item for item in gamestate_response['items'] if item['position'] == self.player['position']]
        if len(item_at_me) == 1:
            item_to_pickup = item_at_me[0]
            discount_price = item_to_pickup["price"] * (100 - item_to_pickup["discountPercent"]) / 100
            if self.player["money"] >= discount_price:
                print(f"\tPICK UP ITEM {item_to_pickup}")
                self.game_client.act(id, "PICK")
                return
        # TODO: Replace random function with goal oriented movement: Choose new destinations as needed, and use A* pathfinding algo to find shortest route to them
        # TODO: Could we use a strategy pattern here to implement different strategies like hoover, random, jason bourne, pacifist, greedy, etc?
        print("\tMove randomly")
        self.make_random_move(self.player['position'])



if __name__ == '__main__':
    bot1 = Bot('T1000',Bot.STRATEGY_PICKUP_CLOSEST)
    while True:
        bot1.tick()
        time.sleep(0.5)
