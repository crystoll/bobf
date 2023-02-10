from game_client import GameClient
import time

class Bot:

    STRATEGY_TERMINATOR='TERMINATOR'
    STRATEGY_GO_TO_EXIT='GO_TO_EXIT'
    STRATEGY_PICKUP_CLOSEST='PICKUP_CLOSEST'
    STRATEGY_HEAL='HEAL'

    def __init__(self:object, name: str, strategy: str):
        self.name = name
        self.strategy = strategy
        self.map = map
        self.game_client = GameClient()
        bot_response = self.game_client.register_bot(name)        
        # print(bot_response)
        self.id = bot_response['id']
        self.player = bot_response['player']
        self.map = bot_response['map']

    
    def tick(self):
        print('TICK!')
        gamestate_response = self.game_client.gamestate()
        print(gamestate_response)


if __name__ == '__main__':
    #api_url = "https://bots-of-black-friday-helsinki.azurewebsites.net"
    bot1 = Bot('T1000',Bot.STRATEGY_PICKUP_CLOSEST)
    while True:
        time.sleep(0.5)
        bot1.tick()
