#! /bin/bash

echo "creating a new project"
mkdir -p output/copiedTriggers
cd output
sfdx force:project:create -n sf-automation-switch-org --manifest
cd sf-automation-switch-org
echo "retriving triggers from $1"
sfdx force:source:retrieve -m 'ApexTrigger' -u $1 --json > output.json

# echo "move triggers from org to output/OriginalTriggers"
# mv force-app/main/default/triggers/* ../originalTriggers
# cd ../../