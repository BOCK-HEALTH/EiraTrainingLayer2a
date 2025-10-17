# Create a single security group for all instances
resource "aws_security_group" "shared_sg" {
  name        = "Eira_1_sec_grp"
  description = "Allow SSH inbound traffic"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
module "ec2_instance_1" {
  source        = "../../modules/ec2"
  ami_id        = var.ami_id
  instance_type = var.instance_type
  volume_size   = var.volume_size
  vpc_id        = var.vpc_id
  security_group_ids = [aws_security_group.shared_sg.id]
  tags          = var.tags_1
  key_name      = var.key_name
  user_data     = <<-EOF
    #!/bin/bash
    cd /home/ubuntu
    sudo su
    sudo apt update -y
    git clone https://github.com/BOCK-HEALTH/Youtube_video_links_extraction.git
    cd Youtube_video_links_extraction
    echo "API_KEY=your_youtube_api_key_here" > /home/ubuntu/Youtube_video_links_extraction/.env
    sudo chmod 004 /home/ubuntu/Youtube_video_links_extraction/.env
    sudo apt install python3-pip -y
    pip3 install -r requirements.txt
    cd ..
    sudo chmod 777 Video_links_extraction
  EOF
}

module "ec2_instance_2" {
  source        = "../../modules/ec2"
  ami_id        = var.ami_id
  instance_type = var.instance_type
  volume_size   = var.volume_size
  vpc_id        = var.vpc_id
  security_group_ids = [aws_security_group.shared_sg.id]
  tags          = var.tags_2
  key_name      = var.key_name
  user_data     = <<-EOF
    #!/bin/bash
    cd /home/ubuntu
    sudo su
    sudo apt update -y
    mkdir Eira1_A2A_dataset_load
    cd Eira1_A2A_dataset_load
    sudo apt install python3-pip -y
    pip3 install boto3
    echo "import boto3
    # ---------- CONFIG ----------
    MAIN_BUCKET = 'eira1-general-dataset'
    SUB_BUCKET = 'eira1-a2a-ds'
    PREFIX = 'audio/'
    REGION = 'ap-south-1'

    # ---------- CREDENTIALS ----------
    AWS_ACCESS_KEY_ID = #Your IAM access key here
    AWS_SECRET_ACCESS_KEY = #Your IAM secret key here
    # ----------------------------

    def copy_updated_files():
        s3 = boto3.resource(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=REGION
        )

        src_bucket = s3.Bucket(MAIN_BUCKET)
        dest_bucket = s3.Bucket(SUB_BUCKET)

        print(f'Starting copy from {MAIN_BUCKET} to {SUB_BUCKET}...')

        for obj in src_bucket.objects.filter(Prefix=PREFIX):
            src_key = obj.key
            copy_source = {'Bucket': MAIN_BUCKET, 'Key': src_key}

            # Copy the file (will overwrite if exists)
            dest_bucket.Object(src_key).copy(copy_source)
            print(f'Copied/Updated: {src_key}')

        print('Copy process completed.')

    if __name__ == '__main__':
        copy_updated_files()
              " > A2A_dataset_load.py
    EOF
}

module "ec2_instance_3" {
  source        = "../../modules/ec2"
  ami_id        = var.ami_id
  instance_type = var.instance_type
  volume_size   = var.volume_size
  vpc_id        = var.vpc_id
  security_group_ids = [aws_security_group.shared_sg.id]
  tags          = var.tags_3
  key_name      = var.key_name
  user_data     = <<-EOF
    #!/bin/bash
    cd /home/ubuntu
    sudo su
    sudo apt update -y
    mkdir Eira1_A2V_dataset_load
    cd Eira1_A2V_dataset_load
    sudo apt install python3-pip -y
    pip3 install boto3
    echo "import boto3
    # ---------- CONFIG ----------
    MAIN_BUCKET = 'eira1-general-dataset'
    SUB_BUCKET = 'eira1-a2v-ds'
    PREFIX = 'videos/'
    REGION = 'ap-south-1'

    # ---------- CREDENTIALS ----------
    AWS_ACCESS_KEY_ID = #Your IAM access key here
    AWS_SECRET_ACCESS_KEY = #Your IAM secret key here
    # ----------------------------

    def copy_updated_files():
        s3 = boto3.resource(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=REGION
        )

        src_bucket = s3.Bucket(MAIN_BUCKET)
        dest_bucket = s3.Bucket(SUB_BUCKET)

        print(f'Starting copy from {MAIN_BUCKET} to {SUB_BUCKET}...')

        for obj in src_bucket.objects.filter(Prefix=PREFIX):
            src_key = obj.key
            copy_source = {'Bucket': MAIN_BUCKET, 'Key': src_key}

            # Copy the file (will overwrite if exists)
            dest_bucket.Object(src_key).copy(copy_source)
            print(f'Copied/Updated: {src_key}')

        print('Copy process completed.')

    if __name__ == '__main__':
        copy_updated_files()
              " > A2V_dataset_load.py
    EOF
}

module "ec2_instance_4" {
  source        = "../../modules/ec2"
  ami_id        = var.ami_id
  instance_type = var.instance_type
  volume_size   = var.volume_size
  vpc_id        = var.vpc_id
  security_group_ids = [aws_security_group.shared_sg.id]
  tags          = var.tags_4
  key_name      = var.key_name
  user_data     = <<-EOF
    #!/bin/bash
    cd /home/ubuntu
    sudo su
    sudo apt update -y
    mkdir Eira1_A2T_dataset_load
    cd Eira1_A2T_dataset_load
    sudo apt install python3-pip -y
    pip3 install boto3
    echo "import boto3
    # ---------- CONFIG ----------
    MAIN_BUCKET = 'eira1-general-dataset'
    SUB_BUCKET = 'eira1-a2t-ds'
    PREFIX = 'transcripts/'
    REGION = 'ap-south-1'

    # ---------- CREDENTIALS ----------
    AWS_ACCESS_KEY_ID = #Your IAM access key here
    AWS_SECRET_ACCESS_KEY = #Your IAM secret key here
    # ----------------------------

    def copy_updated_files():
        s3 = boto3.resource(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=REGION
        )

        src_bucket = s3.Bucket(MAIN_BUCKET)
        dest_bucket = s3.Bucket(SUB_BUCKET)

        print(f'Starting copy from {MAIN_BUCKET} to {SUB_BUCKET}...')

        for obj in src_bucket.objects.filter(Prefix=PREFIX):
            src_key = obj.key
            copy_source = {'Bucket': MAIN_BUCKET, 'Key': src_key}

            # Copy the file (will overwrite if exists)
            dest_bucket.Object(src_key).copy(copy_source)
            print(f'Copied/Updated: {src_key}')

        print('Copy process completed.')

    if __name__ == '__main__':
        copy_updated_files()
              " > A2T_dataset_load.py
    EOF
}

module "ec2_instance_5" {
  source        = "../../modules/ec2"
  ami_id        = var.ami_id
  instance_type = var.instance_type
  volume_size   = var.volume_size
  vpc_id        = var.vpc_id
  security_group_ids = [aws_security_group.shared_sg.id]
  tags          = var.tags_5
  key_name      = var.key_name
  user_data     = <<-EOF
    #!/bin/bash
    cd /home/ubuntu
    sudo su
    sudo apt update -y
    mkdir Eira1_A2I_dataset_load
    cd Eira1_A2I_dataset_load
    sudo apt install python3-pip -y
    pip3 install boto3
    echo "import boto3
    # ---------- CONFIG ----------
    MAIN_BUCKET = 'eira1-general-dataset'
    SUB_BUCKET = 'eira1-a2i-ds'
    PREFIX = 'pairs/'
    REGION = 'ap-south-1'

    # ---------- CREDENTIALS ----------
    AWS_ACCESS_KEY_ID = #Your IAM access key here
    AWS_SECRET_ACCESS_KEY = #Your IAM secret key here
    # ----------------------------

    def copy_updated_files():
        s3 = boto3.resource(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=REGION
        )

        src_bucket = s3.Bucket(MAIN_BUCKET)
        dest_bucket = s3.Bucket(SUB_BUCKET)

        print(f'Starting copy from {MAIN_BUCKET} to {SUB_BUCKET}...')

        for obj in src_bucket.objects.filter(Prefix=PREFIX):
            src_key = obj.key
            copy_source = {'Bucket': MAIN_BUCKET, 'Key': src_key}

            # Copy the file (will overwrite if exists)
            dest_bucket.Object(src_key).copy(copy_source)
            print(f'Copied/Updated: {src_key}')

        print('Copy process completed.')

    if __name__ == '__main__':
        copy_updated_files()
              " > A2I_dataset_load.py
    EOF
}