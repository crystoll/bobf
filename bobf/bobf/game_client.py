import requests
import os
from dotenv import dotenv_values

config = dotenv_values(".env")

class GameClient:

    API_URL = config['API_URL']

    def register_bot(self, bot_name):
        response = requests.post(f"{self.API_URL}/register",
                                json={
                                    "playerName": bot_name
                                }
                                )
        return response.json()

    def gamestate(self):
        return requests.get(f"{self.API_URL}/gamestate").json()


    def act(self, playerId, direction):
        requests.put(f"{self.API_URL}/{playerId}/move",
                    json=direction
                    )


