#!/bin/bash -i

# install python dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
cd api
uv sync --locked
cd ..

# install node dependencies
nvm install --lts
cd web
corepack enable
yarn install --immutable
