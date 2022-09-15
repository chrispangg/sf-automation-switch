echo "Deploying to Org $1"
cd output/sf-automation-switch-org
sfdx force:source:deploy -x "manifest/package.xml" -u $1 --json > TriggerDeactivationResults.json
echo 'Done'
exit 1