variable "tags_1" {
  description = "Tags for EC2 instance 1"
  type        = map(string)
  default     = {
    Name = "Eira_1_general_ds_pipeline"
    Env  = "dev"
  }
}

variable "tags_2" {
  description = "Tags for EC2 instance 2"
  type        = map(string)
  default     = {
    Name = "Eira_1_A2A_pipeline"
    Env  = "dev"
  }
}

variable "tags_3" {
  description = "Tags for EC2 instance 3"
  type        = map(string)
  default     = {
    Name = "Eira_1_A2V_pipeline"
    Env  = "dev"
  }
}

variable "tags_4" {
  description = "Tags for EC2 instance 4"
  type        = map(string)
  default     = {
    Name = "Eira_1_A2T_pipeline"
    Env  = "dev"
  }
}

variable "tags_5" {
  description = "Tags for EC2 instance 5"
  type        = map(string)
  default     = {
    Name = "Eira_1_A2I_pipeline"
    Env  = "dev"
  }
}
variable "aws_region" {
  description = "AWS region to deploy resources"
  default     = "ap-south-1"
}

variable "ami_id" {
  description = "AMI ID for EC2 instance"
  default     = "ami-021a584b49225376d"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.micro"
}

variable "volume_size" {
  description = "Root volume size in GB"
  default     = 8
}

variable "vpc_id" {
  description = "VPC ID for EC2 instance"
}

variable "sg_name" {
  description = "Security group name"
  default     = "dev-free-tier-sg"
}

variable "tags" {
  description = "Tags for EC2 instance"
  type        = map(string)
  default     = {
    Name = "DevFreeTierInstance"
    Env  = "dev"
  }
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
  default     = "YQA_key"
}