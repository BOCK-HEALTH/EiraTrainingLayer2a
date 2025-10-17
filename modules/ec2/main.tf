resource "aws_instance" "this" {
  ami                               = var.ami_id
  instance_type                     = var.instance_type
  key_name                          = var.key_name
  instance_initiated_shutdown_behavior = "stop"

  root_block_device {
    volume_size = var.volume_size
    volume_type = "gp2"
  }

  vpc_security_group_ids = var.security_group_ids
  tags = var.tags

  user_data = var.user_data
}