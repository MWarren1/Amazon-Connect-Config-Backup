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

### start of back up quick connects function
def connect_backup_quick_connects(instance):
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

azn_connect = boto3.client('connect')
instances_raw = azn_connect.list_instances()
# creates a variables that just contains the Instance list
instances = instances_raw['InstanceSummaryList']

instances_num = len(instances)
print("\nNumber of Connect Instances : " + str(instances_num))

for instance in instances:
    connect_backup_quick_connects(instance)