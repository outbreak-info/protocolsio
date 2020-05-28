import requests
import json
import time

from biothings import config
logging = config.logger

api_url = "https://www.protocols.io/api/v3/groups/coronavirus-method-development-community/protocols?page_id=1&page_size=1000&categories=0&filter=group_protocols&order_field=publish_date"

def getAdditionalInfoAbout(uri):
    second_url= "https://go.protocols.io/api/v1/protocols/"+uri
    +"?fields[]=authors&fields[]=doi&fields[]=creator&fields[]=published_on&fields[]=description"
    +"&fields[]=link&fields[]=created_on&fields[]=last_modified&fields[]=fork_id&fields[]=fork_info&fields[]=protocol_name&fields[]=materials_text&fields[]=groups&fields[]=keywords"
    r = requests.get(second_url)
    if r.status_code == 200:
        data = json.loads(r.text)
        return data['protocol']

def mapForkedProtocol(protocol):
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
    protocol["_id"] = f"protocolsio{protocol['id']}"
    protocol["name"] = protocol.get("title", None)
    doi = protocol.get("doi", None)
    if doi:
        protocol["doi"] = doi
        protocol["identifier"] = doi.split('/', 1)[-1]

    website = {"@type":"schema:WebSite"}
    name = "Protocols.io"
    website['name'] = name
    website['url'] = "https://www.protocols.io/"
    website['curationDate'] = datetime.date.today().strftime("%Y-%m-%d")

    protocol["curatedBy"] = website

    dp = protocol.get("published_on", None)
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


def load_annotations():
    r = requests.get(api_url)
    if r.status_code == 200:
        data = json.loads(r.text)
    if data["total"] == len(data["items"]):
        logging.info('TOTAL OK')
    else:
        logging.info('NEEDS PAGINATION')
    for rec in data['items']:
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

        yield protocol
