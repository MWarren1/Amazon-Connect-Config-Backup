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



azn_connect = boto3.client('connect')
instances_raw = azn_connect.list_instances()
# creates a variables that just contains the Instance list
instances = instances_raw['InstanceSummaryList']

### TEMP used for troubleshooting
pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(instances)

instances_num = len(instances)
print("\nNumber of Connect Instances : " + str(instances_num))

for instance in instances:
    print("\nConnect Instance Alias : " + instance['InstanceAlias'])
    print("Connect Instance ARN : " + instance['Arn'])
    # Writes basic instance config to file
    json_convert_write_file(instance, instance['InstanceAlias']+".instance.config", "w")

### Start of backing up routing profiles
#### Still to be complete ####
    routing_profiles_raw = azn_connect.list_routing_profiles(InstanceId=instance['Id'])
    routing_profiles = routing_profiles_raw['RoutingProfileSummaryList']
    #pp.pprint(routing_profiles)
### Start of backing up routing profiles

### Start of backing up Users
    # get list of users in instance
    users_raw = azn_connect.list_users(InstanceId=instance['Id'])
    users = users_raw['UserSummaryList']

    # go through each of the users
    user_num = 1
    # create csv file and add columns
    user_f = open(instance['InstanceAlias']+".users.csv", "w")
    user_f.write("first name,last name,user login,routing profile name,security_profile_name_1|security_profile_name_2,phone type (soft/desk),phone number,soft phone auto accept (yes/no),ACW timeout (seconds)\n")

    for user in users:
        # get details of user config
        user_raw = azn_connect.describe_user(UserId=user['Id'], InstanceId=instance['Id'])
        user = user_raw['User']
        # write json user config to file
        json_convert_write_file(user, instance['InstanceAlias']+".user" + str(user_num) +".config", "w")
        user_num = user_num + 1
        ## prepare user details for CSV
        user_indentity = user['IdentityInfo']
        user_phone_config = user['PhoneConfig']
        # convert ID's to names for CSV file
        for routing_profile in routing_profiles:
            if routing_profile['Id'] == user['RoutingProfileId']:
                user.update({'RoutingProfileId': routing_profile['Name']}) 
        
        # write to csv file
        #pp.pprint(user)
        user_f.write( user_indentity['FirstName']+","+ \
                      user_indentity['LastName']+","+ \
                      user['Username']+","+ \
                      user['RoutingProfileId']+","+ \
                      #### NEED TO SORT OUT Security profile causes error due to list ####
                      user['SecurityProfileIds']+","+ \
                      user_phone_config['PhoneType']+","+ \
                      user_phone_config['DeskPhoneNumber']+","+ \
                      str(user_phone_config['AutoAccept'])+","+ \
                      str(user_phone_config['AfterContactWorkTimeLimit'])+"\n")
    print("Number of users backed up : "+ str(user_num-1))
    user_f.close()

### End of backing up Users