import os

import biothings, config
biothings.config_for_app(config)
from config import DATA_ARCHIVE_ROOT

import biothings.hub.dataload.dumper


class PDumper(biothings.hub.dataload.dumper.DummyDumper):

    SRC_NAME = "protocolsio"
    __metadata__ = {
        "src_meta": {
            "author":{
                "name": "Marco Cano",
                "url": "https://github.com/marcodarko"
            },
            "code":{
                "branch": "master",
                "repo": "https://github.com/marcodarko/protocolsio.git"
            },
            "license": "https://www.protocols.io/terms#tos1",
            "url" : "https://www.protocols.io/groups/coronavirus-method-development-community/publications"
        }
    }
    # override in subclass accordingly
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    SCHEDULE = "20 13 * * *"
