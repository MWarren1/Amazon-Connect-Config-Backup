# Amazon Connect Config Backup

This terraform module deploys everything to backup amazon connect config. a lambda which is scheduled to run daily and weekly backup jobs that backup all amazon instances in the account in which it is deployed. It will backup the following configurations:

- Bacic Instance
- Instance Storage
- Hours of Operation
- Queues
- Routing Profiles
- Security Profiles
- Contact Flows (Only Published Contact Flows)
- Agents - In both json and csv format

summary of what it creates:

- Lambda
- IAM role for Lambda
- Event Rules for daily and weekly jobs  
- S3 Buckets to store backups
- SNS Topic and Cloudwatch Alarm

## Configuration

- `s3_name_prefix` - Optional - Prefix to be added to s3 bucket name. Default: `""`
- `log_bucket_name` - Optional - Logging bucket used by connect backup bucket. Default: `""`
- `retention_daily_backups` - Required - Number of days to keep daily backups.
- `retention_weekly_backups` - Required - Number of weeks to keep weekly backups
- `hour_for_backup` - Optional - Hour of the day to run the backup. Default: `1`
- `weekly_backup_day` - Optional - Day to do the weekly back up, first 3 letters in of the day in caps. Default: `SUN`
- `cloudwatch_log_group_retention` - Optional - Number of days to keep lambda logs. Default: `180`
- `encyrpt_sns` - Optional - Should the sns be encrypted?. Default: `false`
- `sns-subscription-email` - Optional - List of email addresses to subscribe to backup failed sns topic. Default: `[]`
- `sns-subscription-sqs` - Optional - List of sqs queues to subscribe to backup failed sns topic. Default: `[]`
- `object_lock_enabled` - Optional - should object lock be enabled?. Default: `false`
- `object_lock_mode` - Optional - object lock mode. value must be `GOVERNANCE` or `COMPLIANCE`. Default `GOVERNANCE`
- `environment` - Optional - Environment where this module will be deployed. Default: `""`
- `parent_tags` - Optional - Map of tags to be applied to all resources. Default: `{}`

## Outputs

N/A

## Example
Example only using required variables:
```
module "connect-backup" {
  source = "github.com/MWarren1/Amazon-Connect-Config-Backup.git"

  retention_daily_backups  = 30
  retention_weekly_backups = 52
}
```

Example using all variables
```
module "connect-backup" {
  source = "github.com/MWarren1/Amazon-Connect-Config-Backup.git"

  s3_name_prefix                 = "company-name"
  retention_daily_backups        = 30
  retention_weekly_backups       = 52
  hour_for_backup                = 23
  weekly_backup_day              = "MON"
  cloudwatch_log_group_retention = 365
  object_lock_enabled            = true
  object_lock_mode               = "GOVERNANCE"
  environment                    = "prd"
  
  parent_tags = {
    iac   = "terraform"
    owner = "John Wick"
  }
}
```