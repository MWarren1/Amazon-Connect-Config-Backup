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
  validation {
    condition = (
      var.hour_for_backup >= 1 &&
      var.hour_for_backup <= 24
    )
    error_message = "Invalid Range: 1 - 24."
  }
}

variable "weekly_backup_day" {
  type        = string
  description = "day to do the weekly back up, first 3 letters in caps"
  default     = "SUN"

  validation {
    condition     = contains(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"], var.weekly_backup_day)
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

variable "encyrpt_sns" {
  type        = bool
  description = "should the sns be encrypted?"
  default     = false
}

variable "object_lock_enabled" {
  type        = bool
  description = "should object lock be enabled? Changing this will cause the buckets to be destroyed and recreated"
  default     = false
}

variable "object_lock_mode" {
  type        = string
  description = "object lock mode"
  default     = "GOVERNANCE"
  validation {
    condition     = var.object_lock_mode == "GOVERNANCE" || var.object_lock_mode == "COMPLIANCE"
    error_message = "The object_lock_mode value must be GOVERNANCE or COMPLIANCE"
  }
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
