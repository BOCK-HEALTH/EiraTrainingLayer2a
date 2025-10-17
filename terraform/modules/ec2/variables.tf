variable "security_group_ids" {
  description = "List of security group IDs to associate with EC2 instance"
  type        = list(string)
}
variable "user_data" {
  description = "The user_data script to run on instance boot."
  type        = string
}
variable "ami_id" {
  description = "AMI ID for the instance"
  type        = string
}

variable "instance_type" {
  description = "Instance type"
  type        = string
  default     = "t2.micro"
}

variable "volume_size" {
  description = "Root volume size in GB"
  type        = number
  default     = 8
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "sg_name" {
  description = "Security group name"
  type        = string
  default     = "free-tier-sg"
}

variable "tags" {
  description = "Tags for the instance"
  type        = map(string)
  default     = {}
}

variable "key_name" {
  description = "Key pair name for SSH access"
  type        = string
}