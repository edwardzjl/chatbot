#!/bin/bash -i

# install python dependencies
python -m pip install uv --user
cd api
uv sync
cd ..

# install node dependencies
nvm install --lts
cd web
corepack enable
yarn install --immutable
