import json
import csv
import requests

# change this to your API token
apitoken = ""
apiHeader = {"X-Dataverse-key": apitoken}
requestURL = "https://demodv.scholarsportal.info/api/dataverses/DLI-IDD/datasets"
# list of persistenIds to publish datasets after uploading
PIDs = []

false = bool(0)
true = bool(1)


# gets the common info that all imports should have
# title, production date, description, language, production place, subject (Social Sciences)
def getTDDLKPS(p):
    # title
    title_metadata = {"typeName": "title", "multiple": false,
                      "value": p[1].replace("\xa0", " "), "typeClass": "primitive"}
    # date
    production_date_metadata = {"typeName": "productionDate", "multiple": false, "value": p[13].replace("\xa0", " "),
                                "typeClass": "primitive"}
    # description
    description_value = {"value": p[14].replace("\xa0", " "), "multiple": false, "typeClass": "primitive",
                         "typeName": "dsDescriptionValue"}
    description_metadata = {"typeName": "dsDescription", "multiple": true,
                            "value": [{"dsDescriptionValue": description_value}], "typeClass": "compound"}
    # language
    language_metadata = {"typeName": "language", "multiple": true, "typeClass": "controlledVocabulary",
                         "value": [p[25].replace("\xa0", " ")]}
    # place
    production_place_metadata = {"typeName": "productionPlace", "multiple": false, "typeClass": "primitive",
                                 "value": p[3].replace("\xa0", " ")}
    # subject
    subject_metadata = {"typeName": "subject", "multiple": true, "value": ["Social Sciences"],
                        "typeClass": "controlledVocabulary"}
    return title_metadata, production_date_metadata, description_metadata, \
           language_metadata, production_place_metadata, subject_metadata


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
            authors_metadata = {"authorAffiliation": author_affiliation, "authorName": author_name,
                                "authorIdentifierScheme": author_id_scheme, "authorIdentifier": author_id}
        else:
            authors_metadata = {"authorAffiliation": author_affiliation, "authorName": author_name}
    # return author metadata
    author_metadata = {"typeName": "author", "multiple": true, "value": [authors_metadata], "typeClass": "compound"}
    return author_metadata


# returns contact info
# could be authors, or DLI
def getContact(p):
    contact_email = {"typeClass": "primitive", "multiple": false, "typeName": "datasetContactEmail",
                     "value": "mvail@stfx.ca"}
    contact_name = {"typeClass": "primitive", "multiple": false, "typeName": "datasetContactName", "value": p[4]}
    # returns dataset contact name and email
    contact_metadata = {"value": [{"datasetContactEmail": contact_email, "datasetContactName": contact_name}],
                        "typeClass": "compound", "multiple": true,
                        "typeName": "datasetContact"}
    return contact_metadata


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
    # returns keywords_metadataeywords
    keyword_metadata = {"typeName": "keyword", "multiple": true, "typeClass": "compound", "value": keywords_metadata}
    return keyword_metadata


# main<3
if __name__ == '__main__':
    # open and read test .csv
    dli_info = open("ingest-test.csv", "r")
    reader = csv.reader(dli_info)
    # this is the already seen IDs
    # there may be multiple datasets with the same ID
    # as multiple files can be attributed to the same dataset
    prev_ids = []
    # this is all the metadata .json files
    datasets_metadata = []
    c = 0
    for i in reader:
        # retrieves the end of the identifier
        # starts after private://dli_training/
        # 23 characters
        dataset_id = i[31][23:27]
        if i[0] == "UID":
            pass
        # would normally add file info here
        # but not needed for just metadata upload
        elif prev_ids.count(dataset_id) > 0:
            pass
        else:
            # .json skeleton
            blank_json = {"datasetVersion":
                {
                    "license": {
                        "name": "CC0 1.0",
                        "uri": "http://creativecommons.org/publicdomain/zero/1.0"
                    },
                    "metadataBlocks":
                        {"citation":
                             {"fields":
                                  [],
                              "displayName": "Citation Metadata"
                              }
                         }
                }
            }
            # gets all the citation info
            title_md, date_md, desc_md, language_md, place_md, subject_md = getTDDLKPS(i)
            author_md = getAuthor(i)
            contact_md = getContact(i)
            keyword_md = getKeyword(i)
            # appends id to list
            prev_ids.append(dataset_id)
            # sets citation fields
            # required: title, description, subject, author, contact
            blank_json["datasetVersion"]["metadataBlocks"]["citation"]["fields"] = [title_md, date_md, desc_md,
                                                                                    subject_md, author_md, language_md,
                                                                                    place_md, contact_md, keyword_md]
            # add to list of all metadata
            datasets_metadata.append(blank_json)
    # for each metadata string (in json format)
    for i in datasets_metadata:
        # makes file
        # not needed if straight uploading
        # comment out file code below to, skip that stuff if you want
        # outfile = open("dli_migration_" + prev_ids[c] + ".json", "w")
        # json.dump(i, outfile, indent=4)
        # outfile.close()
        json.dumps(i)
        apiJSON = i
        # upload dataset as draft
        response = requests.post(requestURL, headers=apiHeader, json=apiJSON)
        PIDs.append(response.json()["data"]["persistentId"])
        c += 1
