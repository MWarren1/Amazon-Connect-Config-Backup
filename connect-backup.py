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


### Start of backing up Users

    # get list of users in instance
    users_raw = azn_connect.list_users(InstanceId=instance['Id'])
    users = users_raw['UserSummaryList']

    # go through each of the users
    user_num = 1
    for user in users:
        # get details of user config
        user_raw = azn_connect.describe_user(UserId=user['Id'], InstanceId=instance['Id'])
        user = user_raw['User']
        # write user config to file
        json_convert_write_file(user, instance['InstanceAlias']+".user" + str(user_num) +".config", "w")
        user_num = user_num + 1
    print("Number of users backed up : "+ str(user_num-1))

### End of backing up Users