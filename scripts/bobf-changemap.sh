#!/bin/bash

# Maps in order of difficulty
# default.map
# split.map
# split_trap.map
# solita.map
# ikea.map

curl -X POST http://localhost:8080/changemap \
  -d '"ikea.map"' \
  -H "Content-Type: application/json"
