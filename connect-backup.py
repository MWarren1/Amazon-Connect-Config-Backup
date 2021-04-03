import boto3
import json
#import pprint
import datetime

# Function that is used when converting to json to sterlise if value is datetime
def json_datetime_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

# Function that converts data to json and saves to file
def json_convert_write_file(data_to_write, filename, open_option):
    data_to_write_json = json.dumps(data_to_write, indent = 4, default = json_datetime_converter)
    # write json to file
    f = open(filename, open_option)
    f.write(data_to_write_json)
    f.close()

### TEMP used for troubleshooting
#pp = pprint.PrettyPrinter(indent=4)

### Start of backing up Instance basics
azn_connect = boto3.client('connect')
instances_raw = azn_connect.list_instances()
# creates a variables that just contains the Instance list
instances = instances_raw['InstanceSummaryList']

instances_num = len(instances)
print("\nNumber of Connect Instances : " + str(instances_num))

for instance in instances:
    print("\nConnect Instance Alias : " + instance['InstanceAlias'])
    print("Connect Instance ARN : " + instance['Arn'])
    # Writes basic instance config to file
    json_convert_write_file(instance, instance['InstanceAlias']+".instance.config", "w")
### End of backing up Instance basics

### Start of backing up Instance Storage
    storage_types = ['CHAT_TRANSCRIPTS','CALL_RECORDINGS','SCHEDULED_REPORTS','MEDIA_STREAMS','CONTACT_TRACE_RECORDS','AGENT_EVENTS']
    #set some variables for later use
    storage_num = 0
    main_storages_output = {}
    # go through each storage type
    for storage_type in storage_types:
        storages_raw = azn_connect.list_instance_storage_configs(InstanceId=instance['Id'],ResourceType=storage_type)
        storages = storages_raw['StorageConfigs']
        storage_type_output = {storage_type : storages}
        main_storages_output.update(storage_type_output)
        storage_num = storage_num + len(storages)
    # Write json instance storage config to file
    json_convert_write_file(main_storages_output, instance['InstanceAlias']+".instance_storage.config", "w")
    print("Number of Instance Storage config backed up : "+ str(storage_num))
### end of backing up Instance Storage

### start of backing up Quick connects
    q_connects_raw = azn_connect.list_quick_connects(InstanceId=instance['Id'])
    q_connects = q_connects_raw['QuickConnectSummaryList']
    #set some variables for later use
    q_connect_num = 1
    q_connects_output = {}
    # got through quick connects
    for q_connect in q_connects:
        q_connect_raw = azn_connect.describe_quick_connect(InstanceId=instance['Id'], QuickConnectId=q_connect['Id'])
        q_connect = q_connect_raw['QuickConnect']        
        # add queue to queue json output        
        q_connect_output = {'q_connect'+str(q_connect_num) : q_connect}
        q_connects_output.update(q_connect_output)
        q_connect_num = q_connect_num + 1
    
    # Write json queue config to file
    json_convert_write_file(q_connects_output, instance['InstanceAlias']+".quick_connects.config", "w")
    print("Number of Quick connects backed up : "+ str(q_connect_num-1))

### end of backing up Quick connects

### Start of backing up Queues
    queues_raw = azn_connect.list_queues(InstanceId=instance['Id'])
    queues = queues_raw['QueueSummaryList']
    #set some variables for later use
    queue_num = 1
    queues_output = {}
    # go through queues and only back up standard queues
    for queue in queues:
        if queue['QueueType'] == 'STANDARD':
            queue_raw = azn_connect.describe_queue(InstanceId=instance['Id'], QueueId=queue['Id'])
            queue = queue_raw['Queue']
            # add queue to queue json output        
            queue_output = {'queue'+str(queue_num) : queue}
            queues_output.update(queue_output)
            queue_num = queue_num + 1
    
    # Write json queue config to file
    json_convert_write_file(queues_output, instance['InstanceAlias']+".queues.config", "w")
    print("Number of Queues backed up : "+ str(queue_num-1))
### End of backing up Queues

### Start of backing up Hours of Operations
    hoos_raw = azn_connect.list_hours_of_operations(InstanceId=instance['Id'])
    hoos = hoos_raw['HoursOfOperationSummaryList']
    #set some variables for later use
    hoo_num = 1
    hoos_output = {}

    # go through hours of operations
    for hoo in hoos:
        hoo_raw = azn_connect.describe_hours_of_operation(InstanceId=instance['Id'], HoursOfOperationId=hoo['Id'])
        hoo = hoo_raw['HoursOfOperation']
        # add hours of operations to hours of operations json output        
        hoo_output = {'HoO'+str(hoo_num) : hoo}
        hoos_output.update(hoo_output)
        hoo_num = hoo_num + 1
    
    # Write json queue config to file
    json_convert_write_file(hoos_output, instance['InstanceAlias']+".hours_of_operation.config", "w")
    print("Number of Hours of Operations backed up : "+ str(hoo_num-1))

### End of backing up Hours of Operations

### Start of backing up routing profiles
#### need routing profiles to backup users to csv ####
    routing_profiles_raw = azn_connect.list_routing_profiles(InstanceId=instance['Id'])
    routing_profiles = routing_profiles_raw['RoutingProfileSummaryList']
    #set some variables for later use
    routing_profile_num = 1
    routing_profiles_output = {} 

    for routing_profile in routing_profiles:
        # get details of routing profile
        routing_profile_raw = azn_connect.describe_routing_profile(InstanceId=instance['Id'], RoutingProfileId=routing_profile['Id'])
        # strip all non routing profile data from reply
        routing_profile = routing_profile_raw['RoutingProfile']
        # add routing profile to json output
        routing_profile_output = {'routing_profile'+str(routing_profile_num) : routing_profile}
        routing_profiles_output.update(routing_profile_output)
        # write routing profile config to file
        routing_profile_num = routing_profile_num + 1
    # Write json routing profile to file        
    json_convert_write_file(routing_profiles_output, instance['InstanceAlias']+".routing_profiles.config", "w") 
    print("Number of Routing Profiles Backed up : "+ str(routing_profile_num-1))
### Start of backing up routing profiles

### Start of backing up security profiles
#### need security profiles to backup users to csv ####
    # get list of security profiles
    security_profiles_raw = azn_connect.list_security_profiles(InstanceId=instance['Id'])
    security_profiles = security_profiles_raw['SecurityProfileSummaryList']
    security_profile_num = 1
    # write security profiles to file
    json_convert_write_file(security_profiles, instance['InstanceAlias']+".security_profiles.config", "w")
    print("Number of Security Profiles Backed up : "+ str(len(security_profiles)))
### End of backing up security profiles

### Start of backing up Users
    # get list of users in instance
    users_raw = azn_connect.list_users(InstanceId=instance['Id'])
    users = users_raw['UserSummaryList']

    #set some variables for later use
    user_num = 1
    users_output = {}
    # create csv file and add columns
    user_f = open(instance['InstanceAlias']+".users.csv", "w")
    user_f.write("first name,last name,user login,routing profile name,security_profile_name_1|security_profile_name_2,phone type (soft/desk),phone number,soft phone auto accept (yes/no),ACW timeout (seconds)\n")

    for user in users:
        # get details of user config
        user_raw = azn_connect.describe_user(UserId=user['Id'], InstanceId=instance['Id'])
        user = user_raw['User']
        ## prepare user details for CSV
        user_indentity = user['IdentityInfo']
        user_phone_config = user['PhoneConfig']
        # convert ID's to names for CSV file
        for routing_profile in routing_profiles:
            if routing_profile['Id'] == user['RoutingProfileId']:
                user.update({'RoutingProfileId': routing_profile['Name']}) 

        # add user to user json output        
        user_output = {'user'+str(user_num) : user}
        users_output.update(user_output)
        user_num = user_num + 1
        # converting security profiles for csv file
        sec_profile_dectected = 0
        user_security_profile_output = ""
        for security_profile in security_profiles:
            if security_profile['Id'] in user['SecurityProfileIds']:
                if sec_profile_dectected != 0:
                   user_security_profile_output = user_security_profile_output + "|" 
                user_security_profile_output =  user_security_profile_output + security_profile['Name']
                sec_profile_dectected = sec_profile_dectected + 1    
        # write to csv file
        user_f.write( user_indentity['FirstName']+","+ \
                      user_indentity['LastName']+","+ \
                      user['Username']+","+ \
                      user['RoutingProfileId']+","+ \
                      user_security_profile_output+","+ \
                      user_phone_config['PhoneType']+","+ \
                      user_phone_config['DeskPhoneNumber']+","+ \
                      str(user_phone_config['AutoAccept'])+","+ \
                      str(user_phone_config['AfterContactWorkTimeLimit'])+"\n")
    # Write json user config to file
    json_convert_write_file(users_output, instance['InstanceAlias']+".users.config", "w")
    print("Number of users backed up : "+ str(user_num-1))
    user_f.close()
    print("users also backed up to csv template")

### End of backing up Users