variable "s3_name_prefix" {
  type        = string
  description = "prefix to be added to s3 bucket name, should end with -"
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

variable "weekly_backup_day" {
  type        = string
  description = "day to do the weekly back up, first 3 letters in caps"
  default     = "SUN"

  validation {
    condition     = var.weekly_backup_day == "MON" || var.weekly_backup_day == "TUE" || var.weekly_backup_day == "WED" || var.weekly_backup_day == "THU" || var.weekly_backup_day == "FRI" || var.weekly_backup_day == "SAT" || var.weekly_backup_day == "SUN"
    error_message = "The weekly_backup_day value must be MON, TUE, WED, THU, FRI, SAT or SUN"
  }
}

variable "lambda_timeout" {
  type        = number
  description = "number of seconds before backup lambda will timeout"
  default     = 600

  validation {
    condition     = var.lambda_timeout <= 900
    error_message = "The lambda_timeout value needs to be 900 seconds (15 mins) or less"
  }
}

variable "cloudwatch_log_group_retention" {
  type        = number
  description = "number of days to keep lambda logs"
  default     = 180
}

variable "environment" {
  type        = string
  description = "environment"
}

variable "parent_tags" {
  type        = map(any)
  description = "map of tags"
}