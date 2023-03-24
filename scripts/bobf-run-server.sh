#!/bin/bash

(cd bots-of-black-friday/server && npm install && npm run-script build && mvn spring-boot:run)


