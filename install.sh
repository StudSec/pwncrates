#!/bin/bash

echo '{'                             >> data/config.json
echo '  "hostname": "127.0.0.1",'    >> data/config.json
echo '  "oauth_client_id": "",'      >> data/config.json
echo '  "oauth_client_secret": "",'  >> data/config.json
echo '  "git_branch": "",'           >> data/config.json
echo '  "oauth_redirect_uri": "",'   >> data/config.json
echo '  "SMTP_HOST": "",'            >> data/config.json
echo '  "SMTP_PORT": 587,'           >> data/config.json
echo '  "SMTP_USER": "",'            >> data/config.json
echo '  "SMTP_PASS": "",'            >> data/config.json
echo '  "webhook_url": "",'          >> data/config.json
echo '  "secret_key": "'$(openssl rand -hex 24)'",' >> data/config.json
echo '  "instancer_url": ""'         >> data/config.json
echo '  "instancer_username": ""'    >> data/config.json
echo '  "instancer_password": ""'    >> data/config.json
echo '}'                             >> data/config.json

read -p "Populate with test data? (y/n): " response

mkdir data/ssl 2>/dev/null
mkdir data/db 2>/dev/null

if [[ $response == "y" ]]; then
  python3 scripts/test-users.py
  openssl req -x509 -nodes -newkey rsa:2048 -keyout key.pem -out cert.pem -sha256 -days 365 -subj "/C=GB/ST=London/L=London/O=Alros/OU=IT Department/CN=localhost"
  mv key.pem data/ssl/
  mv cert.pem data/ssl/
  git clone https://github.com/StudSec/Challenges-Examples.git
  mkdir data/challenges/
  mv Challenges-Examples data/challenges/Challenges
  echo "Test data populated!"
else
  echo "Make sure to put your data in the following directories:"
  echo "- data/ssl              -> ssl certificates (cert.pem & key.pem)"
  echo "- data/challenges       -> challenges git repository"
  echo "- data/config.json      -> pwncrates configuration"
  echo "- data/.git-credentials -> git credentials to update challenge repository (if its private)"
fi
