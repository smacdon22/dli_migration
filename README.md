# dli_migration
Python import of DLI Training to DLI-IDD dataverse. As part of DLI presentation at IASSIST 2022 in Gothenburg, Sweden on June 8th, 2022 
Conference website: https://iassist2022.org/ 
Presentation information: https://dli-training.github.io/dli-tr/

Takes CSV input, reformats into dataverse's JSON format and uploads datasets as drafts. Then uploads files to each dataset, updates their metadata, and publishes everything once uploaded as draft.

Change the API header to you API token.
Test file is included but you can move this script to a directory with a different file and change the name of the file accessed.
Also, add a folder with all the files to add in their respective folders, labeled by the old CUDO id ex: *directory*/files/2338/ecosoc.pdf etc.

<p class=MsoToc1><span class=MsoHyperlink><a href="#dli-idd-documentation">DLI-IDD
Documentation</a></span></p>

<p class=MsoToc2><span class=MsoHyperlink><a href="#imports">Imports</a></span></p>

<p class=MsoToc2><span class=MsoHyperlink><a href="#csv-legend">CSV Legend</a></span></p>

<p class=MsoToc2><span class=MsoHyperlink><a href="#variables">Variables</a></span></p>

<p class=MsoToc2><span class=MsoHyperlink><a href="#functions">Functions</a></span></p>

<p class=MsoToc2><span class=MsoHyperlink><a href="#main">Main</a></span></p>


<h1><a name="_Toc112072919">DLI-IDD Documentation</a></h1>

<p class=MsoNormal>&nbsp;</p>

<h2><a name="_Toc112072920">Imports</a></h2>

<p class=MsoNormal><a name="_Toc112072921"><span class=Heading3Char>csv</span></a>
for intaking file</p>

<p class=MsoNormal><a name="_Toc112072922"><span class=Heading3Char>os</span></a>
to get directory</p>

<p class=MsoNormal><a name="_Toc112072923"><span class=Heading3Char>requests</span></a>
and <span class=Heading3Char><a
href="https://guides.dataverse.org/en/latest/api/sword.html"><span
style='color:#1F3763;text-decoration:none'>sword2</span></a> </span>for <a
href="https://guides.dataverse.org/en/latest/api/native-api.html">API</a> calls</p>

<p class=MsoNormal><a name="_Toc112072924"><span class=Heading3Char>json</span></a>
for metadata and API responses</p>

<p class=MsoNormal>&nbsp;</p>

<h2><a name="_Toc112072925">CSV Legend</a></h2>

<p class=MsoNormal>Current index of metadata CSV file.</p>

<p class=MsoNormal>0 - UID</p>

<p class=MsoNormal>1 - title</p>

<p class=MsoNormal>2 - Type</p>

<p class=MsoNormal>3 - Presented At</p>

<p class=MsoNormal>4-12 - authorName1,authorAffiliation1,authorORCID1,</p>

<p class=MsoNormal>authorName2,authorAffiliation2,authorORCID2,</p>

<p class=MsoNormal>authorName3,authorAffiliation3,authorORCID3</p>

<p class=MsoNormal>13 - productionDate</p>

<p class=MsoNormal>14 - dsDescriptionValue</p>

<p class=MsoNormal>15-24 - subject1,subject2,subject3,subject4,subject5,</p>

<p class=MsoNormal>subject6,subject7,subject8,subject9,subject10</p>

<p class=MsoNormal>25 - language</p>

<p class=MsoNormal>26 - dcIdentifier</p>

<p class=MsoNormal>27 - dcRelation</p>

<p class=MsoNormal>28 - Extension</p>

<p class=MsoNormal>29 - Name</p>

<p class=MsoNormal>30 - Size</p>

<p class=MsoNormal>31 – Path</p>

<p class=MsoNormal>&nbsp;</p>

<h2><a name="_Toc112072926">Variables</a></h2>

<p class=MsoNormal>Global variables to be customized. </p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072927"><span class=Heading3Char>file_name</span></a>
- csv file with record info</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072928"><span class=Heading3Char>serverHost</span></a>
- dataverse url ex: &quot;https://borealisdata.ca&quot;</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072929"><span class=Heading3Char>apitoken</span></a>
- your <a
href="https://demo.borealisdata.ca/dataverseuser.xhtml?selectTab=apiTokenTab">API
token</a> for the header</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072930"><span class=Heading3Char>apiHeader</span></a>
- header for the API call, contains only API token</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072931"><span class=Heading3Char>dvID</span></a>
- id of dataverse to add content to</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072932"><span class=Heading3Char>requestURL</span></a>
- <a
href="https://guides.dataverse.org/en/latest/api/native-api.html#create-a-dataset-in-a-dataverse-collection">API</a>
call to upload a dataset</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072933"><span class=Heading3Char>fileURL</span></a>
- <a
href="https://guides.dataverse.org/en/latest/api/sword.html#add-files-to-a-dataset-with-a-zip-file">API</a>
call to add a file using swordv2 API</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072934"><span class=Heading3Char>mdURL</span></a>
- <a
href="https://guides.dataverse.org/en/latest/api/native-api.html#get-json-representation-of-a-dataset">API</a>
call that gives us dataset metadata to get new ID</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072935"><span class=Heading3Char>nURL</span></a>
- <a
href="https://guides.dataverse.org/en/latest/api/native-api.html#updating-file-metadata">API</a>
call to update metadata to file</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072936"><span class=Heading3Char>pubURL</span></a>
- <a
href="https://guides.dataverse.org/en/latest/api/native-api.html#publish-a-dataset">API</a>
call to publish dataset</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072937"><span class=Heading3Char>citURL</span></a>
- <a
href="https://guides.dataverse.org/en/latest/api/native-api.html#set-citation-date-field-type-for-a-dataset">API</a>
call to set citation date type so correct year is cited</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072938"><span class=Heading3Char>true, false</span></a>
- booleans so the json format is correct</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal>&nbsp;</p>

<h2><a name="_Toc112072939"></a><a name="_Functions"></a>Functions</h2>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072940"><span class=Heading3Char>getTDDLKSS</span></a>
- takes line of file with dataset info and returns citation metadata</p>

<p class=MsoNormal>for the title, date, description, language, series, subject</p>

<p class=MsoNormal>each metadata field is in the form:</p>

<p class=MsoNormal>{&quot;typeName&quot;: &quot;&quot;, &quot;multiple&quot;:
true, &quot;value&quot;: [],&quot;typeClass&quot;: &quot;&quot;}</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072941"><span class=Heading3Char>getAuthor</span></a>
- takes line of file with dataset info and returns citation metadata</p>

<p class=MsoNormal>for the authors in the form</p>

<p class=MsoNormal>{&quot;authorName&quot;: {}, &quot;authorAffiliation&quot;:
{}, &quot;authorIdentifierScheme&quot;: ,</p>

<p class=MsoNormal>&quot;authorIdentifier&quot;: {}}</p>

<p class=MsoNormal>with {&quot;typeName&quot;:
&quot;authorName&quot;/&quot;authorAffiliation&quot;/&quot;authorIdentifier&quot;/&quot;authorIdentifierScheme&quot;,</p>

<p class=MsoNormal>&quot;multiple&quot;: false, &quot;value&quot;: *from
input*/ORCID, &quot;typeClass&quot;: &quot;primitive&quot;}</p>

<p class=MsoNormal>for each author in the line of the file.</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072942"><span class=Heading3Char>getContact</span></a>
- returns contact information for DLI Professional Development Committee</p>

<p class=MsoNormal>with Statistics Canada. Name, email, and affiliation</p>

<p class=MsoNormal>value: [{&quot;datasetContactName&quot;: {},
&quot;datasetContactEmail&quot;: {},</p>

<p class=MsoNormal>&quot;datasetContactAffiliation&quot;:
{}}],&quot;typeClass&quot;: &quot;compound&quot;, &quot;multiple&quot;: true,</p>

<p class=MsoNormal>&quot;typeName&quot;: &quot;datasetContact&quot;}</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072943"><span class=Heading3Char>getLicense</span></a>
- takes line of file with dataset info and returns citation metadata</p>

<p class=MsoNormal>for the license, either creative commons 4.0 or the
statistics canada open</p>

<p class=MsoNormal>license, depending on whether the author or affiliation is
statistics canada or not.</p>

<p class=MsoNormal>{&quot;name&quot;: &quot;Statistics Canada Open
License&quot;, &quot;uri&quot;:
&quot;https://www.statcan.gc.ca/en/reference/licence&quot;,</p>

<p class=MsoNormal>&quot;active&quot;: true,&quot;shortDescription&quot;:
&quot;This work is licensed under the Statistics</p>

<p class=MsoNormal>Canada Open License.&quot;, &quot;iconURL&quot;:
&quot;https://i.imgur.com/kikchVK.jpg&quot;} or</p>

<p class=MsoNormal>{&quot;name&quot;: &quot;CC BY 4.0&quot;, &quot;uri&quot;:
&quot;http://creativecommons.org/licenses/by/4.0&quot;,</p>

<p class=MsoNormal>&quot;iconURL&quot;:
&quot;https://licensebuttons.net/l/by/4.0/88x31.png&quot;,
&quot;shortDescription&quot;:</p>

<p class=MsoNormal>&quot;This work is licensed under a Creative Commons
Attribution 4.0 International</p>

<p class=MsoNormal>License.&quot;,&quot;active&quot;: true}</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072944"><span class=Heading3Char>getKeywords</span></a>
- takes line of file with dataset info and returns citation metadata</p>

<p class=MsoNormal>for the keywords from the subjects</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072945"><span class=Heading3Char>getMimeType</span></a>
- takes line of file with dataset info and returns the mimetype for</p>

<p class=MsoNormal>whichever file type is in the input</p>

<p class=MsoNormal>&nbsp;</p>

<p class=MsoNormal><a name="_Toc112072946"><span class=Heading3Char>getFile</span></a>
- takes line of file with dataset info and returns the file name and</p>

<p class=MsoNormal>file info for input. later used to upload files.</p>

<p class=MsoNormal>&nbsp;</p>

<h2><a name="_Toc112072947">Main</a></h2>

<p class=MsoNormal><a name="_Toc112072948"><span class=Heading3Char>Open and
read ingest file</span></a>, make empty arrays for previously seen identifiers
and the metadata and files for each dataset. </p>

<p class=MsoNormal><a name="_Toc112072949"><span class=Heading3Char>For each
line in the ingest file</span></a>; get the old dataset identifier. </p>

<p class=MsoNormal><span class=Heading4Char>If this dataset hasn't been
processed yet,</span> create blank .json string for citation information and
fill by calling <span class=MsoBookTitle><span style='font-weight:normal'><a
href="#_Functions"><span style='color:windowtext;text-decoration:none'>Functions
1-7</span></a></span></span>. Add new dataset metadata and (first) file to
list. </p>

<p class=MsoNormal><span class=Heading4Char>If this dataset has been processed</span>,
find existing dataset and add file.</p>

<p class=MsoNormal><a name="_Toc112072950"><span class=Heading3Char>For dataset
in datasets metadata list</span></a>; upload dataset metadata and get
persistent ID using API. <span class=Heading4Char>For files in dataset file
list</span>; upload files to datasets and then upload metadata to each file.</p>

<p class=MsoNormal><span class=Heading5Char>Set the citation date type</span> to
production date (default but still need to do this).</p>

<p class=MsoNormal><span class=Heading4Char>Publish </span>dataset.</p>
