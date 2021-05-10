# Amazon_Connect_Config_Backup
Python scripts to backup the config of a single or all amazon connect instances on an aws account:
- connect-backup.py - backs up all instance config
- connect-backup-users.py - only backs up users to JSON and CSV output
- connect-backup-users-lambda.py - aws lambda function backs up users to CSV and uploads to s3 bucket
- connect-backup-quick-connects.py - only backs up quick connects to JSON output 

## What Currently works
- Config Backup
    - Basic Instance config
    - Users - JSON and CSV output, but only for SAML and connect managed identity management
    - routing profiles
    - security profiles
    - queues
    - hours of operation
    - instance storage
    - quick connects
## Still to Add
- cli switches
    - single instance backup 
- Config Backup
    - users - allow user back up for all instances what ever identity management is used
    - phone numbers
    - external services
        - app integrations 
        - lambda associations
        - lex associations
        - origins
    - data streaming
- Config Restore - Not Started
