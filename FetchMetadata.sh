cd output/sf-automation-switch-org
echo "retriving $3 from $1"
echo "running...sfdx force:source:retrieve -$2 $3 -u $1 --json > output.json"
sfdx force:source:retrieve -$2 $3 -u $1 --json > output.json
exit 1