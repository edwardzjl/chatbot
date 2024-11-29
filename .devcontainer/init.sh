#!/bin/zsh -i

# install python dependencies
python -m pip install pipenv --user
cd api
PIPENV_VENV_IN_PROJECT=1 pipenv sync -d
cd ..

# install node dependencies
nvm install --lts
cd web
yarn
