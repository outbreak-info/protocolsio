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
        for i,rec in enumerate(data['items']):
            logging.info("progress {} of {} docs".format(i,totalDocs))
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
            protocol["_id"] = f"protocolsio{rec['id']}"
            protocol["doi"] = rec.get("doi", None)
            uri = rec.get("uri", None)
            if uri:
                protocol["url"] = "https://www.protocols.io/view/"+uri
                add_info = getAdditionalInfoAbout(uri)
                desc = add_info.get("description", None)
                if desc:
                    d = json.loads(desc)
                    desc_text=''
                    if d['blocks']:
                        for item in d['blocks']:
                            desc_text += item['text']
                    protocol["description"] = desc_text

                if add_info.get("fork_info", None):
                    forkProtocol= mapForkedProtocol(add_info.get("fork_info"))
                    protocol["isBasedOn"].append(forkProtocol)

            website = {"@type":"schema:WebSite"}

            name = "Protocols.io"
            website['name'] = name
            website['url'] = "https://www.protocols.io/"
            website['curationDate'] = datetime.date.today().strftime("%Y-%m-%d")

            protocol["curatedBy"] = website

            protocol["name"] = rec.get("title", None)
            protocol["identifier"] = rec['doi'].split('/', 1)[-1]

            dp = rec.get("published_on", None)
            if dp:
                d = time.strftime("%Y-%m-%d", time.localtime(dp))
                protocol["datePublished"] = d

            authors = rec.get("authors", [])
            if len(authors):
                for auth in authors:
                    author = {"@type":"outbreak:Person"}

                    full_name = auth.get("name", None)
                    if full_name is not None:
                        author["name"] = full_name
                        author["givenName"] = full_name.split(' ', 1)[0]
                        author["familyName"] = full_name.split(' ', 1)[-1]

                    institutions = auth.get("affiliation", None)
                    if institutions is not None:
                        organization = {"@type":"outbreak:Organization"}
                        author["affiliation"] =[]
                        organization["name"] = auth["affiliation"]
                        if organization["name"] is not None:
                            author["affiliation"].append(organization)
                    for key in author:
                        if author[key] is None: del author[key]
                    protocol["author"].append(author)

            #cleanup doc of empty vals
            for key in list(protocol):
                if not protocol.get(key):del protocol[key]
            logging.info(f"doc processed with id {rec['id']}")
            # yield protocol
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
