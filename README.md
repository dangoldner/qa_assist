# Updating Quality Documents from Emails

I am part of a medical device startup. We make progress in every arena (manufacturing, clinical, ...) primarily by emailing with contractors. There are two types of artifacts I need to maintain:

* A set of *detailed logs*, one for each function.
* Aset of informal but foundational *quality documents*: risk register, decision log, design i/o matrix. 

This library

* Reads emails copies them to the appropriate log based on the gmail label. 
* Reads logs and proposes new entries to the quality documents for review and approval.

Main functionality is in core.py. Support for running on cron as a google cloud function in cloud.py and gcloud.md. 
