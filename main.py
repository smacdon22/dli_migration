import json
import csv
import wget
import os
import requests
from sword2 import Connection

# change this to your API token
apitoken = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
apiHeader = {"X-Dataverse-key": apitoken}
con = Connection("https://demodv.scholarsportal.info/dvn/api/", user_name=apitoken)
requestURL = "https://demodv.scholarsportal.info/api/dataverses/DLI-IDD/datasets"
fileURL = "https://demodv.scholarsportal.info/dvn/api/data-deposit/v1.1/swordv2/edit-media/study/"
# list of persistentIds to publish datasets after uploading
PIDs = []

false = bool(0)
true = bool(1)


# gets the common info that all imports should have
# title, date, description, language, production place, subject (Social Sciences)
def getTDDLKSS(p):
    # title
    title_metadata = {"typeName": "title", "multiple": false,
                      "value": p[1].replace("\xa0", " "), "typeClass": "primitive"}
    # date
    publication_date_metadata = {"typeName": "publicationDate", "multiple": false, "value": p[13].replace("\xa0", " "),
                                 "typeClass": "primitive"}
    # description
    description_metadata = {"typeName": "dsDescription", "multiple": true,
                            "value": [
                                {
                                    "dsDescriptionValue": {
                                        "value": p[14].replace("\xa0", " "), "multiple": false,
                                        "typeClass": "primitive", "typeName": "dsDescriptionValue"
                                    }
                                },
                            ], "typeClass": "compound"}
    # language
    language_metadata = {"typeName": "language", "multiple": true, "typeClass": "controlledVocabulary",
                         "value": [p[25].replace("\xa0", " ")]}
    # series
    series_metadata = {"typeName": "series", "multiple": false, "typeClass": "compound", "value": {
        "seriesName": {"typeName": "seriesName", "multiple": false, "typeClass": "primitive",
                       "value": p[3].replace("\xa0", " ")}}}
    # subject
    subject_metadata = {"typeName": "subject", "multiple": true, "value": ["Social Sciences"],
                        "typeClass": "controlledVocabulary"}
    return title_metadata, publication_date_metadata, description_metadata, language_metadata, series_metadata, subject_metadata


# gets author(s)
# includes author name, affiliation, and ORCID (optional)
def getAuthor(p):
    # checks if more than one author
    if p[7] != "":
        # initialize list of authors
        authors_metadata = []
        # max three authors
        for i in range(3):
            pl = i * 3
            # if there's another author
            if p[4 + pl] != "":
                # affiliation
                author_affiliation = {"typeName": "authorAffiliation", "multiple": false,
                                      "value": p[5 + pl].replace("\xa0", " "),
                                      "typeClass": "primitive"}
                # name
                author_name = {"typeName": "authorName", "multiple": false, "value": p[4 + pl].replace("\xa0", " "),
                               "typeClass": "primitive"}
                # if there's an ORCID
                if p[6 + pl] != "":
                    # scheme (ORCID)
                    author_id_scheme = {"typeName": "authorIdentifierScheme", "multiple": false,
                                        "typeClass": "controlledVocabulary", "value": "ORCID"}
                    # id
                    author_id = {"typeName": "authorIdentifier", "multiple": false,
                                 "value": p[6 + pl].replace("\xa0", " "),
                                 "typeClass": "primitive"}
                    authors_metadata.append({"authorAffiliation": author_affiliation, "authorName": author_name,
                                             "authorIdentifierScheme": author_id_scheme,
                                             "authorIdentifier": author_id})
                else:
                    authors_metadata.append({"authorAffiliation": author_affiliation, "authorName": author_name})
    else:
        # only author name
        author_affiliation = {"typeName": "authorAffiliation", "multiple": false, "value": p[5].replace("\xa0", " "),
                              "typeClass": "primitive"}
        # only author affiliation
        author_name = {"typeName": "authorName", "multiple": false, "value": p[4].replace("\xa0", " "),
                       "typeClass": "primitive"}
        # if there's an ORCID
        if p[6] != "":
            author_id_scheme = {"typeName": "authorIdentifierScheme", "multiple": false,
                                "typeClass": "controlledVocabulary",
                                "value": "ORCID"}
            author_id = {"typeName": "authorIdentifier", "multiple": false, "value": p[6].replace("\xa0", " "),
                         "typeClass": "primitive"}
            authors_metadata = [{"authorAffiliation": author_affiliation, "authorName": author_name,
                                 "authorIdentifierScheme": author_id_scheme, "authorIdentifier": author_id}]
        else:
            authors_metadata = [{"authorAffiliation": author_affiliation, "authorName": author_name}]
    # return author metadata
    author_metadata = {"typeName": "author", "multiple": true, "value": authors_metadata, "typeClass": "compound"}
    return author_metadata


# returns contact info
# could be authors, or DLI
def getContact():
    contact_metadata = {
        "value": [
            {
                "datasetContactEmail": {"typeClass": "primitive", "multiple": false,
                                        "typeName": "datasetContactEmail",
                                        "value": "statcan.maddli-damidd.statcan@statcan.gc.ca"},
                "datasetContactName": {"typeClass": "primitive", "multiple": false,
                                       "typeName": "datasetContactName",
                                       "value": "Professional Development Committee."},
                "datasetContactAffiliation": {"typeClass": "primitive", "multiple": false,
                                              "typeName": "datasetContactAffiliation",
                                              "value": "Statistics Canada. Data Liberation Initiative (DLI)"}
            }
        ],
        "typeClass": "compound", "multiple": true,
        "typeName": "datasetContact"
    }
    return contact_metadata


# gets copyright license
def getLicense(p):
    # checks if Statistics Canada content or not
    if p[5].replace("\xa0", " ") == "Statistics Canada" or p[4].replace("\xa0", " ") == "Statistics Canada":
        # either their open license
        license_metadata = {"name": "Statistics Candada Open License",
                            "uri": "https://www.statcan.gc.ca/en/reference/licence"}
    else:
        # or CC BY 4.0
        license_metadata = {"name": "CC BY 4.0", "uri": "http://creativecommons.org/licenses/by/4.0",
                            "iconURL": "https://licensebuttons.net/l/by/4.0/88x31.png"}
    return license_metadata


# adds subjects 1-8 as keywords
# Subjects can only be one of a preselected few (Social Sciences)
# but keywords can be anything
def getKeyword(p):
    keywords_metadata = []
    # for each subject
    for i in p[15:24]:
        # if there's another
        if i != "":
            keywords_metadata.append(
                {"keywordValue": {"typeName": "keywordValue", "multiple": false, "typeClass": "primitive",
                                  "value": i.replace("\xa0", " ")}})
    # returns keywords
    keyword_metadata = {"typeName": "keyword", "multiple": true, "typeClass": "compound", "value": keywords_metadata}
    return keyword_metadata


def getMimeType(p):
    if p == "pdf":
        return "application/pdf"
    elif p == "doc":
        return "application/msword"
    elif p == "docx":
        return "application/vnd.openxmlformatsofficedocument.wordprocessingml.document"
    elif p == "ppt":
        return "application/vnd.ms-powerpoint"
    elif p == "pptx":
        return "application/vnd.openxmlformatsofficedocument.presentationml.presentation"
    elif p == "jpg" or p == "jpeg":
        return "image/jpeg"
    elif p == "png":
        return "image/png"
    elif p == "mp3":
        return "audio/mpeg"
    elif p == "mp4":
        return "video/mp4"
    else:
        return "text/plain"


def getFile(p):
    fName = p[29]
    fInfo = {"filename": p[29], "description": p[1]+" "+(p[28].upper()), "categories": [p[2]], "restrict": false,
         "mimeType": getMimeType(p[28])}
    return [fName, fInfo]


# main
if __name__ == '__main__':
    # open and read test .csv
    with open("ingest-test.csv", "r") as dli_info:
        reader = csv.reader(dli_info)
        # this is the already seen IDs
        # there may be multiple datasets with the same ID
        # as multiple files can be attributed to the same dataset
        prev_ids = []
        # this is all the metadata .json files
        datasets_metadata = []
        c = 0
        for file_line in reader:
            # retrieves the end of the identifier
            # starts after private://dli_training/
            # 23 characters
            dataset_id = file_line[31][23:27]
            if file_line[0] == "UID":
                pass
            # would normally add file info here
            # but not needed for just metadata upload
            elif prev_ids.count(dataset_id) > 0:
                d = prev_ids.index(file_line[31][23:27])
                datasets_metadata[d][1].append(getFile(file_line))
            else:
                # .json skeleton
                blank_json = {
                    "datasetVersion": {
                        "license":
                            getLicense(file_line),
                        "metadataBlocks": {
                            "citation": {
                                "fields": [
                                ],
                                "displayName": "Citation Metadata"
                            }
                        }
                    }
                }
                # gets all the citation info
                title_md, date_md, desc_md, language_md, series_md, subject_md = getTDDLKSS(file_line)
                author_md = getAuthor(file_line)
                contact_md = getContact()
                keyword_md = getKeyword(file_line)
                fs = getFile(file_line)
                # appends id to list
                prev_ids.append(dataset_id)
                # sets citation fields
                # required: title, description, subject, author, contact
                blank_json["datasetVersion"]["metadataBlocks"]["citation"]["fields"] = [title_md, date_md, desc_md,
                                                                                        subject_md, author_md, language_md,
                                                                                        contact_md, keyword_md, series_md]
                # add to list of all metadata
                datasets_metadata.append([blank_json, [fs]])

                c += 1
    # for each metadata string (in json format)
    c = 0
    for r in datasets_metadata:
        json.dumps(r[0])
        apiJSON = r[0]
        # upload dataset as draft
        response = requests.post(requestURL, headers=apiHeader, json=apiJSON)
        ppp = response.json()["data"]["persistentId"]
        for i in r[1]:
            with open(os.getcwd() + "/files/" + prev_ids[c] + "/" + i[0], "rb") as data:
                receipt = con.add_file_to_resource(
                    edit_media_iri= fileURL + ppp,
                    payload=data,
                    mimetype="application/zip",
                    filename=i[0],
                    packaging="http://purl.org/net/sword/package/SimpleZip")
        mdURL = "https://demodv.scholarsportal.info/api/datasets/" + str(response.json()["data"]["id"]) + "/versions/:draft/files"
        res = requests.get(mdURL, headers=apiHeader)
        if res.json()["status"] != "ERROR":
            m = 0
            for v in res.json()["data"]:
                nURL = "https://demodv.scholarsportal.info/api/files/" + str(v["dataFile"]["id"]) + "/metadata"
                files = {'jsonData': (None, str(json.dumps(r[1][m][1]))),}
                rres = requests.post(nURL, headers=apiHeader, files=files)
                m += 1
                print(files)
                print(rres.text)
        # publish the dataset
        pubURL = "https://demodv.scholarsportal.info/api/datasets/:persistentId/actions/:publish?persistentId="+ppp+"&type=major"
        pResponse = requests.post(pubURL, headers=apiHeader)
        c += 1
