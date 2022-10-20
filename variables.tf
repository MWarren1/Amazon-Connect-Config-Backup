variable "s3_name_prefix" {
  type        = string
  description = "prefix to be added to s3 bucket name"
  default     = ""
}

variable "log_bucket_name" {
  type        = string
  description = "logging bucket used by connect backup bucket"
  default     = ""
}

variable "retention_daily_backups" {
  type        = number
  description = "number of days to keep daily backups"
}

variable "retention_weekly_backups" {
  type        = number
  description = "number of weeks to keep weekly backups"
}

variable "hour_for_backup" {
  type        = number
  description = "hour of the day to run the backup"
  default     = 1
}

variable "weekly_backup_day" {
  type        = string
  description = "day to do the weekly back up, first 3 letters in caps"
  default     = "SUN"

  validation {
    condition     = var.weekly_backup_day == "MON" || var.weekly_backup_day == "TUE" || var.weekly_backup_day == "WED" || var.weekly_backup_day == "THU" || var.weekly_backup_day == "FRI" || var.weekly_backup_day == "SAT" || var.weekly_backup_day == "SUN"
    error_message = "The weekly_backup_day value must be MON, TUE, WED, THU, FRI, SAT or SUN"
  }
}

variable "cloudwatch_log_group_retention" {
  type        = number
  description = "number of days to keep lambda logs"
  default     = 180
}

variable "sns-subscription-email" {
  type        = list(string)
  description = "list of email addresses to subscribe to backup failed sns topic"
  default     = []
}

variable "sns-subscription-sqs" {
  type        = list(string)
  description = "list of sqs queues to subscribe to backup failed sns topic"
  default     = []
}

variable "environment" {
  type        = string
  description = "environment where this module will be deployed"
  default     = ""
}

variable "parent_tags" {
  type        = map(any)
  description = "map of tags to be applied to all resources"
  default     = {}
}