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

def connect_backup_users(instance):
    print("\nConnect Instance Alias : " + instance['InstanceAlias'])
    print("Connect Instance ARN : " + instance['Arn'])
    # created variable used for user backup
    instance_id_management = instance['IdentityManagementType']
### End of backing up Instance basics


### Start of getting routing profiles
    routing_profiles_raw = azn_connect.list_routing_profiles(InstanceId=instance['Id'])
    routing_profiles = routing_profiles_raw['RoutingProfileSummaryList']
### Start of getting routing profiles

### Start of getting security profiles
    security_profiles_raw = azn_connect.list_security_profiles(InstanceId=instance['Id'])
    security_profiles = security_profiles_raw['SecurityProfileSummaryList']
### End of getting security profiles

### Start of backing up Users
    # get list of users in instance
    users_raw = azn_connect.list_users(InstanceId=instance['Id'])
    users = users_raw['UserSummaryList']

    #set some variables for later use
    user_num = 1
    users_output = {}
    # create csv file and add columns
    user_f = open(instance['InstanceAlias']+".users.csv", "w")
    # setup csv output depending on the id management
    if instance_id_management == 'SAML':
        user_f.write("first name,last name,user login,routing profile name,security_profile_name_1|security_profile_name_2,phone type (soft/desk),phone number,soft phone auto accept (yes/no),ACW timeout (seconds)\n")
    if instance_id_management == 'CONNECT_MANAGED':
        user_f.write("first name,last name,email address,password,user login,routing profile name,security_profile_name_1|security_profile_name_2,phone type (soft/desk),phone number,soft phone auto accept (yes/no),ACW timeout (seconds)\n")
    ##### need to add the other connect id management at a later date #####
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
        # converting phone type for csv
        if user_phone_config['PhoneType'] == 'SOFT_PHONE':
            user_phone_type = 'soft'
        else:
            user_phone_type = 'desk'
        # converting auto accept for csv
        if str(user_phone_config['AutoAccept']) == 'FALSE':
            user_auto_accept = 'no'
        else:
            user_auto_accept = 'yes'   

        # write csv output to file depending on the id management
        if instance_id_management == 'SAML':
            user_f.write( user_indentity['FirstName']+","+ \
                          user_indentity['LastName']+","+ \
                          user['Username']+","+ \
                          user['RoutingProfileId']+","+ \
                          user_security_profile_output+","+ \
                          user_phone_type +","+ \
                          user_phone_config['DeskPhoneNumber']+","+ \
                          user_auto_accept+","+ \
                          str(user_phone_config['AfterContactWorkTimeLimit'])+"\n")
        if instance_id_management == 'CONNECT_MANAGED':
            user_f.write( user_indentity['FirstName']+","+ \
                          user_indentity['LastName']+","+ \
                          user_indentity['Email']+","+ \
                          ","+ \
                          user['Username']+","+ \
                          user['RoutingProfileId']+","+ \
                          user_security_profile_output+","+ \
                          user_phone_type +","+ \
                          user_phone_config['DeskPhoneNumber']+","+ \
                          user_auto_accept+","+ \
                          str(user_phone_config['AfterContactWorkTimeLimit'])+"\n")
    # Write json user config to file
    json_convert_write_file(users_output, instance['InstanceAlias']+".users.config", "w")
    print("Number of users backed up : "+ str(user_num-1))
    user_f.close()
    print("users also backed up to csv template")

### End of backing up Users




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
    connect_backup_users(instance)
