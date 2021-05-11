###################################################
# creates csv for users for each connect instance #
# and uploads teh csv fiel to an s3 bucket        #
###################################################

# Requirements:
# - Connect - Read Access
# - S3 - Write access only to bucket where csv files are saved

# Expected event input, s3_object_prefix is optional :
#   {
#    "s3_bucket": "s3 bucket",
#    "s3_object_prefix": "connect_backup/"
#   }

import logging
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def upload_file(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    file_name = str(file_name)
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# connect backup users function
def connect_backup_users(instance):
    azn_connect = boto3.client('connect')
    # created variable used for user backup
    instance_id_management = instance['IdentityManagementType']

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
    csv_output = instance['InstanceAlias']+".users.csv"
    user_f = open('/tmp/'+csv_output, 'w')
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
    logger.info(instance['InstanceAlias']+': '+str(user_num-1)+' users backed up')
    user_f.close()
    return csv_output
### End of backing up users function

##### Start of Main lambda function #####
def lambda_handler(event, context):
    s3_bucket = event['s3_bucket']
    s3_object_prefix = event['s3_object_prefix']
    azn_connect_instance = boto3.client('connect')
    instances_raw = azn_connect_instance.list_instances()
    # creates a variables that just contains the Instance list
    instances = instances_raw['InstanceSummaryList']
    instances_num = len(instances)
    logger.info("Number of Connect Instances : " + str(instances_num))

    for instance in instances:
        # back up users to csv file
        csv_output = connect_backup_users(instance)
        csv_output = str(csv_output)
        # upload csv file to s3 bucket
        datetime_now = datetime.now()
        datetime_now = datetime_now.strftime("%Y-%m-%d_%H:%M.")

        if s3_object_prefix is not None:
            s3_object = str(s3_object_prefix + datetime_now +csv_output)
            upload_status = upload_file('/tmp/'+csv_output, s3_bucket, s3_object)
        else:
            upload_status = upload_file('/tmp/'+csv_output, s3_bucket)
            s3_object = str(datetime_now + csv_output)
        
        logger.info(instance['InstanceAlias'] +' users: s3://' + s3_bucket + '/' + s3_object)
##### End of Main lambda function #####