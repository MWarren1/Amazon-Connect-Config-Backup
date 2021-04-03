# Amazon_Connect_Config_Backup
Python script to backup the config of a single or all amazon connect instances on an aws account

## What Currently works
- Config Backup
    - Basic Instance config
    - Users - only for SSO for identity management
    - routing profiles - currently exported a seperate files 
    - security profiles
## Still to Add
- cli switches
    - single instance backup 
- Config Backup
    - users - allow user back up for all instances what ever identity management is used
    - routing profiles - make it so all routing profiles export as a single config file
    - instance storage
    - quick connects
    - hours of operation
    - queues
    - external services
        - lambda associations
        - lex associations
        - origins
- Config Restore - Not Started