#!/bin/bash

cd bobf/bobf
#poetry install
poetry run python bobf/simplebot.py &
poetry run python bobf/hooverbot.py &
poetry run python bobf/bot.py &
poetry run python bobf/botitron.py &

