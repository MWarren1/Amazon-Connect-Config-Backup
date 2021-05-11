import boto3
import argparse
import csv

def create_quick_connect(instance_id, name, description,type, phone_number):
    response = azn_connect.create_quick_connect(
        InstanceId=instance_id,
        Name=name,
        Description=description,
        QuickConnectConfig={
            'QuickConnectType': 'PHONE_NUMBER',
            'PhoneConfig': {
                'PhoneNumber': phone_number
            }
        },
    )
    return response

def list_instances():
    ##### get list of connect instances ######
    azn_connect = boto3.client('connect')
    instances_raw = azn_connect.list_instances()
    # creates a variables that just contains the Instance list
    instances = instances_raw['InstanceSummaryList']

    instances_num = len(instances)
    print("\nNumber of Connect Instances : " + str(instances_num))

    for instance in instances:
        print("\nConnect Instance Alias : " + instance['InstanceAlias'])
        print("Connect Instance ID : " + instance['Id'])

def get_quick_connects(instance_id):
    ### start of backing up Quick connects
    azn_connect = boto3.client('connect')
    q_connects_raw = azn_connect.list_quick_connects(InstanceId=instance_id)
    q_connects = q_connects_raw['QuickConnectSummaryList']
    #set some variables for later use
    q_connects_output = {}
    q_connect_num = 1
    # got through quick connects
    for q_connect in q_connects:
        q_connect_raw = azn_connect.describe_quick_connect(InstanceId=instance_id, QuickConnectId=q_connect['Id'])
        q_connect = q_connect_raw['QuickConnect']             
        # add queue to queue json output        
        q_connect_output = {'q_connect'+str(q_connect_num) : q_connect}
        q_connects_output.update(q_connect_output)
        q_connect_num = q_connect_num + 1
        #print(q_connects_output)
    return q_connects_output



## CLI switches
parser = argparse.ArgumentParser(prog='Phone_Number_Reporter.py', description='imports quick connect in to amazon connect instance')
parser.add_argument('--instance_id', required=False, help='Instance ID of amamzon instance')
parser.add_argument('--import_file', required=False, help='file input(must be csv)')
parser.add_argument('--update', required=False, help='used so quick connects will be updated if that already exist needs to be yes')

args = parser.parse_args()
instance_id = args.instance_id
import_file = args.import_file
update_q_connects = args.update

if update_q_connects == 'yes':
    update_q_connects = True
else:
    update_q_connects = False

##### check for errors with import file and instance ID
is_error = False
error_message = ''
# check both switches are used
if instance_id == None or import_file == None:
    is_error = True
    error_message = '\n ***ERROR*** - you need to used both --instance_is and --import_file cli switches'
else:
    # check import file can be opened
    try:
        f = open(import_file, 'r')
        f.close()
    except:
        is_error = True
        error_message = '\n ***ERROR*** - Unable to open import file'
    if len(instance_id) != 36:
        is_error = True
        error_message = '\n***ERROR*** - Your instance ID is incorrect, Your instance ID is the 36-character alphanumeric string at the end of the instance ARN.' 


if is_error == True:    
    # error script stops here 
    list_instances()
    print(error_message)
else:
    # start to import quick connects
    azn_connect = boto3.client('connect')
    # get current quick connects
    quick_connect_list = get_quick_connects(instance_id)
    q_connect_num = len(quick_connect_list)
    # opening import file as csv and go through row by row
    with open(import_file, 'r') as f:
        parserreader = csv.reader(f)
        # skip row that contains the colunms
        # column title and what number they:
        # Name - 0
        # Description - 1
        # Type - 2
        # Phone Number - 3
        # Queue to attach to - 4
        next(parserreader, None) 
        for row in parserreader:
            # check if quick connect already exsists
            exists = False
            current_q_connect_num = 1
            while current_q_connect_num <= q_connect_num:
                current_q_connect = quick_connect_list['q_connect'+str(current_q_connect_num)]
                #print(current_q_connect['Name'])
                if current_q_connect['Name'] == row[0]:
                    exists = True
                current_q_connect_num = current_q_connect_num + 1
            
            # check if quick connect exists
            if exists == True:
                # If update quick connects is set to false go print Error and go to next row
                if update_q_connects == True:
                    print(row[0] + ' - Already Exists and will be deleted')
                    # workout what to do, just delete quick connect? what happens with queues its attached to
                    print('function to delete quick contact')
            
            if update_q_connects == False and exists == True:
                print(row[0] + ' - Already Exists')
            else:
                # check type of quick connect    
                if row[2] == 'EXTERNAL':
                    quick_connect_details = create_quick_connect(instance_id, row[0], row[1], row[2], row[3])
                    print(row[0] + ' - Has been created!')
                #print(row)
                print(quick_connect_details)



