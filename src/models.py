class Attributes:
    type: str
    url: str

    def __init__(self, type: str, url: str) -> None:
        self.type = type
        self.url = url

class Version:
    attributes: Attributes
    version_number: int

    def __init__(self, attributes: Attributes, version_number: int) -> None:
        self.attributes = attributes
        self.version_number = version_number
    

class Flow:
    attributes: Attributes
    id: str
    active_version: Version
    latest_version: Version
    developer_name: str

    def __init__(self, attributes: Attributes, id: str, active_version: Version, latest_version: Version, developer_name: str) -> None:
        self.attributes = attributes
        self.id = id
        self.active_version = active_version
        self.latest_version = latest_version
        self.developer_name = developer_name

