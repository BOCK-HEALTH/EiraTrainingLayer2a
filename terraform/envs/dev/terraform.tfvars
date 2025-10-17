aws_region   = "ap-south-1"
ami_id       = "ami-021a584b49225376d"
instance_type = "t2.micro"
volume_size  = 30
vpc_id       = "vpc-071bbb019115241cb"
sg_name      = "Eira_1_sec_grp"
tags = {
  Name = "Eira_1_General_Dataset_Pipeline"
  Env  = "dev"
}
key_name = "YQA_key"