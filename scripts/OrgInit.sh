#! /bin/bash
#1=alias
#2=md_flag
#3=metadata


echo "creating a new project"
mkdir -p output/copiedTriggers
mkdir -p output/copiedDuplicateRules
mkdir -p output/json
cd output
sfdx force:project:create -n sf-automation-switch-org --manifest
echo "Done"
exit 0
# cd sf-automation-switch-org
# echo "retriving $3 from $1"
# sfdx force:source:retrieve -$2 $3 -u $1 --json > output.json
# exit 1