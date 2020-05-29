import requests
import json
import time

from biothings import config
logging = config.logger

api_url = "https://www.protocols.io/api/v3/groups/coronavirus-method-development-community/protocols?page_id=1&page_size=1000&categories=0&filter=group_protocols&order_field=publish_date"

def getAdditionalInfoAbout(uri):
    second_url= f"""https://go.protocols.io/api/v1/protocols/{uri}?fields[]=authors&fields[]=is_owner&fields[]=in_trash&fields[]=is_bookmarked&fields[]=is_content_warning&fields[]=is_content_confidential&fields[]=doi&fields[]=type_id&fields[]=creator&fields[]=published_on&fields[]=description&fields[]=link&fields[]=manuscript_citation&fields[]=created_on&fields[]=last_modified&fields[]=fork_id&fields[]=fork_info&fields[]=public&fields[]=public_fork_note&fields[]=doi_status&fields[]=documents&fields[]=warning&fields[]=stats&fields[]=guidelines&fields[]=before_start&fields[]=protocol_name&fields[]=protocol_name_html&fields[]=protocol_img&fields[]=materials_text&fields[]=document&fields[]=version_id&fields[]=collection_items&fields[]=shared_access_id&fields[]=is_shared_directly&fields[]=can_claim_authorship&fields[]=can_accept_authorship&fields[]=is_contact_suspended&fields[]=is_retracted&fields[]=retraction_reason&fields[]=version_class&fields[]=has_versions&fields[]=is_unlisted&fields[]=versions&fields[]=groups&fields[]=status&fields[]=journal&fields[]=can_remove_fork&fields[]=keywords&fields[]=show_comparsion&fields[]=ownership_history&fields[]=parent_protocols&fields[]=parent_collections&fields[]=cited_protocols&fields[]=can_be_copied&fields[]=location&fields[]=units"""
    r = requests.get(second_url)
    if r.status_code == 200:
        data = json.loads(r.text)
        return data['protocol']

def mapForkedProtocol(prot):
    protocol={
            "@context": {
                "schema":"http://schema.org/",
                "outbreak":"https://discovery.biothings.io/view/outbreak/",
            },
            "@type":'Protocol',
            "keywords":[],
            "author":[],
            "funding":[],
            "isBasedOn":[]
        }
    protocol["_id"] = f"protocolsio{prot['id']}"
    protocol["name"] = prot.get("title", None)
    doi = prot.get("doi", None)
    if doi:
        protocol["doi"] = doi
        protocol["identifier"] = doi.split('/', 1)[-1]

    website = {"@type":"schema:WebSite"}
    name = "Protocols.io"
    website['name'] = name
    website['url'] = "https://www.protocols.io/"
    website['curationDate'] = datetime.date.today().strftime("%Y-%m-%d")

    protocol["curatedBy"] = website

    dp = prot.get("published_on", None)
    if dp:
        d = time.strftime("%Y-%m-%d", time.localtime(dp))
        protocol["datePublished"] = d
    uri = protocol.get("uri", None)
    if uri:
        protocol["url"] = "https://www.protocols.io/view/"+uri
    # cleanup
    for key in list(protocol):
            if not protocol.get(key):del protocol[key]

    return protocol


def getDocs():
    docs =[]
    r = requests.get(api_url)
    if r.status_code == 200:
        data = json.loads(r.text)
        totalDocs = len(data["items"])
    # if data["total"] == totalDocs:
    #     logging.info('Total docs matches total results')
    # else:
    #     logging.info('Parser for Protocols.io needs pagination')
        logging.info("Starting Loop...")
        records = data["items"]
        for i,rec in enumerate(records):
            logging.info("progress {} of {} docs".format(i,totalDocs))
            protocol = rec
            docs.append(protocol)

    logging.info(f"total docs processed {len(docs)}")
    return docs

def load_annotations():
    docs = getDocs()
    logging.info(f'Got {len(docs)} docs')
    if docs:
        for doc in docs:
            yield doc
    else:
        logging.info('Failed to load docs for Protocols.io')
