#!/bin/bash
cp data/example_config.toml data/config.toml

sed -i "s|SECRET_KEY = \"\"|SECRET_KEY = \"$(openssl rand -hex 24)\"|" data/config.toml

read -p "Populate with test data? (y/n): " response

mkdir data/ssl 2>/dev/null
mkdir data/db 2>/dev/null

if [[ $response == "y" ]]; then
  python3 scripts/populate-users.py
  openssl req -x509 -nodes -newkey rsa:2048 -keyout key.pem -out cert.pem -sha256 -days 365 -subj "/C=GB/ST=London/L=London/O=Alros/OU=IT Department/CN=localhost"
  mv key.pem data/ssl/
  mv cert.pem data/ssl/
  git clone https://github.com/StudSec/Challenges-Examples.git
  #mkdir data/challenges/
  mv Challenges-Examples data/challenges/Challenges
  echo "Test data populated!"
else
  echo "Make sure to put your data in the following directories:"
  echo "- data/ssl              -> ssl certificates (cert.pem & key.pem)"
  echo "- data/challenges       -> challenges git repository"
  echo "- data/.git-credentials -> git credentials to update challenge repository (if its private)"
fi
