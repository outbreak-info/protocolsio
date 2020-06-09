import biothings.hub.dataload.uploader
import os

import requests
import biothings
import config
biothings.config_for_app(config)

MAP_URL = "https://raw.githubusercontent.com/SuLab/outbreak.info-resources/master/outbreak_resources_es_mapping.json"
MAP_VARS = ["@type", "author", "citedBy", "correction", "curatedBy", "dateModified", "datePublished", "description", "doi", "duration", "funding", "identifier", "inComplianceWith", "instrument", "isBasedOn", "keywords", "license", "material", "measurementTechnique", "name", "protocolCategory", "relatedTo", "topicCategory", "url", "usedToGenerate"]

# when code is exported, import becomes relative
try:
    from protocolsio.parser import load_annotations as parser_func
except ImportError:
    from .parser import load_annotations as parser_func


class PUploader(biothings.hub.dataload.uploader.BaseSourceUploader):

    main_source="protocolsio"
    name = "protocolsio"
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
            "license": "https://www.protocols.io/terms#tos1"
        }
    }
    idconverter = None
    storage_class = biothings.hub.dataload.storage.BasicStorage

    def load_data(self, data_folder):
        if not data_folder:
            self.logger.info("No data file for protocolsio")
        return parser_func()

    @classmethod
    def get_mapping(klass):
        r = requests.get(MAP_URL)
        if(r.status_code == 200):
            mapping = r.json()
            mapping_dict = { key: mapping[key] for key in MAP_VARS }
            return mapping_dict
