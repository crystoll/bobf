# Bots of Black Friday client

## What is here?

basic_bot folder contains very basic bot, with not really much setup. It's based on bots of black friday python sample, but with minimal implementation to make it realize. It only depends on requests-lib so you will need to have Python 3.x, with requests library installed by however means you prefer, for example pip -r requests.txt

This is just a minimal demo for presentation on bots of black friday, could of course be used as basis for your own bot

We also have samples folder for json samples from server, and bobf folder that contains a Poetry-enabled full solution for a working bot. Code is not 100% cleaned up yet, so may require some assembly, and there's definitely some overlap.

## How to run it

You need to have a server up. You need to configure the server address in .env file. You need to have Python/Virtualenv up and all dependencies installed with Poetry.

To run the client you can go to bobf folder, and do:

```bash
poetry run python bobf/bot.py
```

To run unit tests:

```bash
poetry run pytest
```


## Using virtualenv and Poetry

### Here's how to setup initially

```bash
pyenv virtualenv 3.11.0 bobf
pyenv local bobf
curl -sSL https://install.python-poetry.org | python3 -
poetry --version
poetry self update
poetry new bobf
cd bobf
poetry add requests
```

### Here's how to add dependencies

```bash
cd bobf
poetry add requests
poetry add python-dotenv
```

### Here's how to install and run

```bash
cd bobf
poetry install
poetry run python bobf/bot.py
```

## Some notes, insights, and learnings

- When bot decides to pick up an item, it changes state to 'PICK', and it should check this to avoid trying to pick again, as otherwise it will drain the health
- When shooting, it's good to check there is another target on board, or it will drain your own health
- If another player has a weapon, might be a good idea to not be the one farthest away from them
- Manual override for target using keyboard control might be good, that would require to set some kind of goal and stick to it until reached or it disappears
- Easier to make money on an empty board, it gets much more interesting when there are others shooting and picking up things, health goes a lot more unstable
- Health slowly drains while you move so need to keep an eye on it and start journey back if it goes too low - theoretically this would depend also how far you are from exit, if you are far away, should start journey back when you still have plenty of health
- If you run low on money you can't pick up more anymore, so can set a threshold when to run for exit
- Weapons have biggest discounts so should always prioritize them - but kinda depends also on distance, especially with others on board
- Always picking up closest items is not too bad algorithm
- Health maxes out at 100, so perhaps if health is high, prioritize value items, and when health is low, prioritize beer

