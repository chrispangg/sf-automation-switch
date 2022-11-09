# $1=Org Alias
# $2=Metadata flag
# $3=Metadata type

cd output/sf-automation-switch-org
echo "retriving $3 from $1"
echo "running...sfdx force:source:retrieve -$2 $3 -u $1"
sfdx force:source:retrieve -$2 $3 -u $1
echo 'Done'
exit 1