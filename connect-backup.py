import boto3
import json
import pprint
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
pp = pprint.PrettyPrinter(indent=4)


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

### Start of backing up routing profiles
#### need routing profiles to backup users to csv ####
    routing_profiles_raw = azn_connect.list_routing_profiles(InstanceId=instance['Id'])
    routing_profiles = routing_profiles_raw['RoutingProfileSummaryList']
    routing_profile_num = 1
    for routing_profile in routing_profiles:
        # get details of routing profile
        routing_profile_raw = azn_connect.describe_routing_profile(InstanceId=instance['Id'], RoutingProfileId=routing_profile['Id'])
        # strip all non routing profile data from reply
        routing_profile_output = routing_profile_raw['RoutingProfile']
        # write routing profile config to file
        json_convert_write_file(routing_profile_output, instance['InstanceAlias']+".routing_profile." + routing_profile_output['Name'] +".config", "w")
        routing_profile_num = routing_profile_num + 1 
    print("Number of Routing Profiles Backed up : "+ str(routing_profile_num-1))
### Start of backing up routing profiles

### Start of backing up security profiles
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