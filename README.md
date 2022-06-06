# dli_migration
Python import of DLI Training to DLI-IDD dataverse. As part of DLI presentation at IASSIST 2022 in Gothenburg, Sweden on June 8th, 2022 https://iassist2022.org/ https://dli-training.github.io/dli-tr/

Takes CSV input, reformats into dataverse's JSON format and uploads datasets as drafts. Then uploads files to each dataset, updates their metadata, and publishes everything once uploaded as draft.

Change the API header to you API token.
Test file is included but you can move this script to a directory with a different file and change the name of the file accessed.
Also, add a folder with all the files to add in their respective folders, labeled by the old CUDO id ex: *directory*/files/2338/ecosoc.pdf etc.
