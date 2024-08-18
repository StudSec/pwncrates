#!/bin/bash
# Run script from the pwncrates root directory
cd $(dirname $0)

git remote update >/dev/null 2>&1
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})

if [[ "$LOCAL" == "$REMOTE" ]]; then
  echo "No updates available."
  exit 0
fi

# Reset and fetch any updates
git checkout release
git pull origin release

# Execute the deployment command
docker-compose down --remove-orphans
docker-compose --profile "" build
docker-compose --profile "" up -d
