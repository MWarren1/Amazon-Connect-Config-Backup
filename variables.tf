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
}

variable "environment" {
  type        = string
  description = "environment"
}

variable "cloudwatch_log_group_retention" {
  type        = number
  description = "number of days to keep lambda logs"
  default     = 180
}

variable "parent_tags" {
  type        = map(any)
  description = "map of tags"
}