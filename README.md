# TO DO

- lambda permissions - remove permissions 
- add variable forhour to do backup

# Amazon Connect Config Backup

This terraform module deploys everything to backup amazon connect config. a lambda which is scheduled to run daily and weekly backup jobs that backup all amazon instances in the account in which it is deployed

summary of what it creates:

- Lambda
- IAM role for Lambda
- Event Rules for daily and weekly jobs  
- S3 Bucket to store backups
- SNS Topic for backup failures

## Configuration

- `s3_name_prefix` - Optional - Prefix to be added to s3 bucket name. Default: `""`
- `retention_daily_backups` - Required - Number of days to keep daily backups.
- `retention_weekly_backups` - Required - Number of weeks to keep weekly backups
- `hour_for_backup` - Optional - Hour of the day to run the backup. Default: `1`
- `weekly_backup_day` - Optional - Day to do the weekly back up, first 3 letters in of the day in caps. Default: `SUN`
- `cloudwatch_log_group_retention` - Optional - Number of days to keep lambda logs. Default: `180`
- `environment` - Optional - Environment where this module will be deployed. Default: `""`
- `parent_tags` - Optional - Map of tags to be applied to all resources. Default: `{}`

## Outputs

N/A

## Example
Example only using required variables:
```
module "connect-backup" {
  source = "github.com/MWarren1/Amazon-Connect-Config-Backup.git?ref=adding-terraform-module"

  retention_daily_backups  = 30
  retention_weekly_backups = 52
}
```

Example using all variables
```
module "connect-backup" {
  source = "github.com/MWarren1/Amazon-Connect-Config-Backup.git?ref=adding-terraform-module"

  s3_name_prefix                 = "company-name"
  retention_daily_backups        = 30
  retention_weekly_backups       = 52
  hour_for_backup                = 23
  weekly_backup_day              = "MON"
  cloudwatch_log_group_retention = 365
  environment                    = "prd"
  
  parent_tags = {
    iac   = "terraform"
    owner = "John Wick"
  }
}
```