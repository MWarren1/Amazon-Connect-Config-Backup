# Amazon_Connect_Config_Backup
Python script to backup the config of a single or all amazon connect instances on an aws account

## What Currently works
- Config Backup
    - Basic Instance config
    - Users - only for SSO for identity management
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
- Config Restore - Not Started
