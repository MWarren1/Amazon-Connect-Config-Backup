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
def connect_backup_agent_statuses(instance):
    statuses_raw = azn_connect.list_agent_statuses(InstanceId=instance['Id'])
    print(statuses_raw)
    statuses = statuses_raw['AgentStatusSummaryList']
    #set some variables for later use
    status_num = 1
    statuses_output = {}
    # got through quick connects
    for status in statuses:
        status_name = status['Name']
        status_arn = status['Arn']       
        # add queue to queue json output        
        status_output = {status_name : status_arn}
        statuses_output.update(status_output)
        status_num = status_num + 1
    # Write json queue config to file
    json_convert_write_file(statuses_output, instance['InstanceAlias']+".agent-statuses.config", "w")
    print("Number of Quick connects backed up : "+ str(status_num-1))
    ### end of backing up Quick connects

azn_connect = boto3.client('connect')
instances_raw = azn_connect.list_instances()
# creates a variables that just contains the Instance list
instances = instances_raw['InstanceSummaryList']

instances_num = len(instances)
print("\nNumber of Connect Instances : " + str(instances_num))

for instance in instances:
    connect_backup_agent_statuses(instance)