import boto3
import json
import datetime
import os
from botocore.config import Config

# Function that is used when converting to json to sterlise if value is datetime
def json_datetime_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

# Function that converts data to json and saves to file
def json_convert_write_file(data_to_write, filename, open_option):
    data_to_write_json = json.dumps(data_to_write, indent = 4,
                                    default = json_datetime_converter)
    # write json to file
    f = open(filename, open_option)
    f.write(data_to_write_json)
    f.close()

# Fucntion that uploads config file to s3 bucket
def s3_upload(filename, backup_type, s3_bucket, boto_s3):

    current_year = datetime.datetime.now().strftime('%Y')
    current_month = datetime.datetime.now().strftime('%m')
    current_day = datetime.datetime.now().strftime('%d')

    source_path = '/tmp/' + filename
    destination_path = f'{backup_type}/{current_year}/{current_month}/{current_day}/{filename}'
    boto_s3.upload_file(source_path, s3_bucket, destination_path)

def lambda_handler(event, context):
    ### getting enviromental variables###
    DAILY_BACKUP_S3_BUCKET = os.environ['DAILY_BACKUP_S3_BUCKET']
    WEEKLY_BACKUP_S3_BUCKET = os.environ['WEEKLY_BACKUP_S3_BUCKET']

    try:
        backup_type = event['backup-type']
    except:
        backup_type = 'ad-hoc'

    current_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    print('\nBackup Type : ' + backup_type + '    @ ' + current_date)

    # define output bucket
    if backup_type == 'daily':
        OUTPUT_S3_BUCKET = DAILY_BACKUP_S3_BUCKET
    elif backup_type == 'weekly':
        OUTPUT_S3_BUCKET = WEEKLY_BACKUP_S3_BUCKET
    else:
        OUTPUT_S3_BUCKET = DAILY_BACKUP_S3_BUCKET
    
    # Initiate boto3 clients
    config = Config(
        retries = {
            'max_attempts': 100,
            'mode': 'adaptive'
            })
    s3 = boto3.client('s3')
    azn_connect = boto3.client('connect', config=config)
    ### Start of backing up Instance basics
    instances_raw = azn_connect.list_instances()
    # creates a variables that just contains the Instance list
    instances = instances_raw['InstanceSummaryList']

    instances_num = len(instances)
    # used so that folder is only created for contact flows on the first instance
    print('\nNumber of Connect Instances : ' + str(instances_num))

    for instance in instances:
        print('\nConnect Instance Alias : ' + instance['InstanceAlias'])
        print('Connect Instance ARN : ' + instance['Arn'])
        # created variable used for user backup
        instance_id_management = instance['IdentityManagementType']
        # Writes basic instance config to file
        basic_config_file = current_date+'_'+instance['InstanceAlias']+'.instance.config'
        # create config file in tmp folder
        json_convert_write_file(instance, '/tmp/'+basic_config_file, 'w')
        # upload file to s3 bucket
        s3_upload(basic_config_file, backup_type, OUTPUT_S3_BUCKET, s3)
    ### End of backing up Instance basics

    ### Start of backing up Instance Storage
        storage_types = ['CHAT_TRANSCRIPTS','CALL_RECORDINGS',
                        'SCHEDULED_REPORTS','MEDIA_STREAMS',
                        'CONTACT_TRACE_RECORDS','AGENT_EVENTS']
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
        instance_storage_file = current_date+'_'+instance['InstanceAlias']+'.instance_storage.config'
        json_convert_write_file(main_storages_output, '/tmp/'+instance_storage_file, 'w')
        # upload file to s3 bucket
        s3_upload(instance_storage_file, backup_type, OUTPUT_S3_BUCKET, s3)
        print('Number of Instance Storage config backed up : '+ str(storage_num))
    ### end of backing up Instance Storage

    ### start of backing up Quick connects
        #set some variables for later use
        q_connect_num = 1
        q_connects_output = {}

        paginator = azn_connect.get_paginator('list_quick_connects')
        response_iterator = paginator.paginate(InstanceId=instance['Id'])

        for page in response_iterator:
            q_connects = page['QuickConnectSummaryList']
            # got through quick connects
            for q_connect in q_connects:
                q_connect_raw = azn_connect.describe_quick_connect(InstanceId=instance['Id'], QuickConnectId=q_connect['Id'])
                q_connect = q_connect_raw['QuickConnect']
                # add queue to queue json output
                q_connect_output = {'q_connect'+str(q_connect_num) : q_connect}
                q_connects_output.update(q_connect_output)
                q_connect_num = q_connect_num + 1

        # Write json queue config to file
        quick_connects_file = current_date+'_'+instance['InstanceAlias']+'.quick_connects.config'
        json_convert_write_file(q_connects_output, '/tmp/'+quick_connects_file, 'w')

        # upload file to s3 bucket
        s3_upload(quick_connects_file, backup_type, OUTPUT_S3_BUCKET, s3)

        print('Number of Quick connects backed up : '+ str(q_connect_num-1))

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
        queues_file = current_date+'_'+instance['InstanceAlias']+'.queues.config'
        json_convert_write_file(queues_output, '/tmp/'+queues_file, 'w')

        # upload file to s3 bucket
        s3_upload(queues_file, backup_type, OUTPUT_S3_BUCKET, s3)

        print('Number of Queues backed up : '+ str(queue_num-1))
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
        hoo_file = current_date+'_'+instance['InstanceAlias']+'.hours_of_operation.config'
        json_convert_write_file(hoos_output, '/tmp/'+hoo_file, 'w')

        # upload file to s3 bucket
        s3_upload(hoo_file, backup_type, OUTPUT_S3_BUCKET, s3)

        print('Number of Hours of Operations backed up : '+ str(hoo_num-1))

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
        routing_profiles_file = current_date+'_'+instance['InstanceAlias']+'.routing_profiles.config'
        json_convert_write_file(routing_profiles_output, '/tmp/'+routing_profiles_file, 'w')

        # upload file to s3 bucket
        s3_upload(routing_profiles_file, backup_type, OUTPUT_S3_BUCKET, s3)

        print('Number of Routing Profiles Backed up : ' + str(routing_profile_num-1))
    ### Start of backing up routing profiles

    ### Start of backing up security profiles
    #### need security profiles to backup users to csv ####
        # get list of security profiles
        security_profiles_raw = azn_connect.list_security_profiles(InstanceId=instance['Id'])
        security_profiles = security_profiles_raw['SecurityProfileSummaryList']
        # write security profiles to file
        security_profiles_file = current_date+'_'+instance['InstanceAlias']+'.security_profiles.config'
        json_convert_write_file(security_profiles, '/tmp/'+security_profiles_file, 'w')

        # upload file to s3 bucket
        s3_upload(security_profiles_file, backup_type, OUTPUT_S3_BUCKET, s3)

        print('Number of Security Profiles Backed up : '+ str(len(security_profiles)))
    ### End of backing up security profiles

    ### Start of backing up Users
        #set some variables for later use
        user_num = 1
        users_output = {}

        # create csv file and add columns
        users_csv_file = current_date+'_'+instance['InstanceAlias']+'.users.csv'
        user_f = open('/tmp/'+users_csv_file, 'w')
        # setup csv output depending on the id management
        if instance_id_management == 'SAML':
            user_f.write('first name,last name,user login,routing profile name,security_profile_name_1|security_profile_name_2,phone type (soft/desk),phone number,soft phone auto accept (yes/no),ACW timeout (seconds)\n')
        if instance_id_management == 'CONNECT_MANAGED':
            user_f.write('first name,last name,email address,password,user login,routing profile name,security_profile_name_1|security_profile_name_2,phone type (soft/desk),phone number,soft phone auto accept (yes/no),ACW timeout (seconds)\n')

        # get list of users in instance

        # get list of users in instance
        # Create a reusable Paginator
        paginator = azn_connect.get_paginator('list_users')
        response_iterator = paginator.paginate(InstanceId=instance['Id'])

        for page in response_iterator:
            users = page['UserSummaryList']

            # need to add the other connect id management at a later date
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
                user_security_profile_output = ''
                for security_profile in security_profiles:
                    if security_profile['Id'] in user['SecurityProfileIds']:
                    # adds pipe to user_security_profile_output if this is the 2nd security profile found on the user
                        if sec_profile_dectected != 0:
                            user_security_profile_output =  user_security_profile_output +'|'
                        # adding security profile to security profile output
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
                    user_f.write( user_indentity['FirstName']+','+ \
                                user_indentity['LastName']+','+ \
                                user['Username']+','+ \
                                user['RoutingProfileId']+','+ \
                                user_security_profile_output+','+ \
                                user_phone_type +','+ \
                                user_phone_config['DeskPhoneNumber']+','+ \
                                user_auto_accept+','+ \
                                str(user_phone_config['AfterContactWorkTimeLimit'])+'\n')
                if instance_id_management == 'CONNECT_MANAGED':
                    user_f.write( user_indentity['FirstName']+','+ \
                                user_indentity['LastName']+','+ \
                                user_indentity['Email']+','+ \
                                ','+ \
                                user['Username']+','+ \
                                user['RoutingProfileId']+','+ \
                                user_security_profile_output+','+ \
                                user_phone_type +','+ \
                                user_phone_config['DeskPhoneNumber']+','+ \
                                user_auto_accept+','+ \
                                str(user_phone_config['AfterContactWorkTimeLimit'])+'\n')
        # Write json user config to file
        users_file = current_date+'_'+instance['InstanceAlias']+'.users.config'
        json_convert_write_file(users_output, '/tmp/'+users_file, 'w')

       # upload file to s3 bucket
        s3_upload(users_file, backup_type, OUTPUT_S3_BUCKET, s3)

        print('Number of users backed up : '+ str(user_num-1))
        user_f.close()

        # upload users csv file to s3 bucket
        s3_upload(users_csv_file, backup_type, OUTPUT_S3_BUCKET, s3)

        print('Users Backed up to CSV and JSON')

    ### End of backing up Users

    ### Start of Backing up Contact Flows
        contact_flow_types=[
            'CONTACT_FLOW','CUSTOMER_QUEUE','CUSTOMER_HOLD','CUSTOMER_WHISPER','AGENT_HOLD','AGENT_WHISPER','OUTBOUND_WHISPER','AGENT_TRANSFER','QUEUE_TRANSFER',
        ]
        contact_flow_list_raw = azn_connect.list_contact_flows(InstanceId=instance['Id'], ContactFlowTypes=contact_flow_types)
        contact_flow_list = contact_flow_list_raw['ContactFlowSummaryList']

        contact_flows_backedup = {}
        contact_flows_backedup_num = 0
        contact_flows_not_backedup = {}
        contact_flows_not_backedup_num = 0
        
        # create folder for contact flows if it doesnt exsist
        contact_flow_folder_path = '/tmp/contact_flows'
        folder_exists = os.path.exists(contact_flow_folder_path)
        if not folder_exists:
            os.mkdir(contact_flow_folder_path)

        for contact_flow in contact_flow_list:
            get_contact_flow_details = 'successful'
            # try checks if contact flow is published
            try:
                contact_flow_raw = azn_connect.describe_contact_flow(InstanceId=instance['Id'], ContactFlowId=contact_flow['Id'])
            except:
                contact_flows_not_backedup.update({contact_flow['Name'] : contact_flow})
                print('Contact Flow NOT Backed Up - '+contact_flow['Name'])
                get_contact_flow_details = 'failed'

                contact_flows_not_backedup_num = contact_flows_not_backedup_num + 1

            if get_contact_flow_details == 'successful':
                contact_flows_backedup.update({contact_flow['Name'] : contact_flow})

                # backup contact flow to xml file
                contact_flow_xml = contact_flow_raw['ContactFlow']['Content']
                # write json to file
                # make contact flow name a useable file name
                contact_flow_file_safe_name = contact_flow['Name'].replace(' ', '-')
                contact_flow_file_safe_name = contact_flow_file_safe_name.replace('---', '-')
                contact_flow_file_safe_name = contact_flow_file_safe_name.replace('--', '-')

                xml_file = 'contact_flows/'+current_date+'_'+instance['InstanceAlias']+'.contact_flow.'+contact_flow_file_safe_name+'.xml'

                xml = open('/tmp/'+xml_file, 'w')
                xml.write(contact_flow_xml)
                xml.close()

                # upload contact flow to s3 bucket
                s3_upload(xml_file, backup_type, OUTPUT_S3_BUCKET, s3)

                contact_flows_backedup_num = contact_flows_backedup_num + 1

        contact_flows_backedup_file = current_date+'_'+instance['InstanceAlias']+'.contact_flows_backedup.config'
        json_convert_write_file(contact_flows_backedup, '/tmp/'+contact_flows_backedup_file, 'w')
        contact_flows_not_backedup_file = current_date+'_'+instance['InstanceAlias']+'.contact_flows_not_backedup.config'
        json_convert_write_file(contact_flows_not_backedup, '/tmp/'+contact_flows_not_backedup_file, 'w')

        s3_upload(contact_flows_backedup_file, backup_type, OUTPUT_S3_BUCKET, s3)
        s3_upload(contact_flows_not_backedup_file, backup_type, OUTPUT_S3_BUCKET, s3)

        print('Number of Contact Flows Backed up : '+ str(contact_flows_backedup_num))
        print('Number of Contact Flows NOT Backed up : '+ str(contact_flows_not_backedup_num))
    ### End of Backing up Contact Flows

if __name__ == '__main__':
    event = {
        'backup-type' : 'ad-hoc'
    }

    lambda_handler(event, None)
