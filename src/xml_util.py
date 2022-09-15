class XmlUtil:

    def generate_trigger_package(dst, sfapi):
        with open("output/sf-automation-switch-org/manifest/package.xml", "w+") as package_xml:
            package_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            package_xml.write('<Package xmlns="http://soap.sforce.com/2006/04/metadata">\n')
            package_xml.write(
                "    <types>\n        <members>*</members>\n        <name>ApexTrigger</name>\n    </types>\n"
            )
            package_xml.write("    <version>" + str(sfapi) + "</version>\n")
            package_xml.write("</Package>")
