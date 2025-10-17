# Audio2Any Pipeline

This repository contains the complete infrastructure and application code for the Audio2Any Pipeline, a system designed to process YouTube videos, extract various data modalities (video, audio, text, and frame-audio pairs), and store them in AWS S3 for further use in AI/ML model training.

The project leverages Python for data processing and Terraform for automating the cloud infrastructure setup on AWS.

![Pipeline Architecture Diagram](https://drive.google.com/uc?export=view&id=16iZ21JQtJHUzkYT1UtATXZdDnaAgVxpe)

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Getting Started: Developer Guide](#getting-started-developer-guide)
  - [Prerequisites](#prerequisites)
  - [Step 1: Clone the Repository](#step-1-clone-the-repository)
  - [Step 2: Configure AWS Credentials](#step-2-configure-aws-credentials)
  - [Step 3: Set up Terraform](#step-3-set-up-terraform)
  - [Step 4: Deploy the Infrastructure](#step-4-deploy-the-infrastructure)
  - [Step 5: Running the Data Pipeline](#step-5-running-the-data-pipeline)
- [Codebase Deep Dive](#codebase-deep-dive)
  - [youtube_video_links.py](#youtube_video_linkspy)
  - [aws.py](#awspy)
  - [extract_frames_audio_FPS2_prototype.py](#extract_frames_audio_fps2_prototypepy)
- [Infrastructure as Code (IaC) with Terraform](#infrastructure-as-code-iac-with-terraform)
  - [Directory Structure](#directory-structure)
  - [Key Resources](#key-resources)

## Project Overview

The primary goal of the Audio2Any project is to create a scalable pipeline for building datasets from YouTube content. The pipeline automates the following tasks:

- Fetching video links from a specified YouTube channel.
- Downloading the video and extracting the audio.
- Transcribing the audio to text using the Vosk speech recognition model.
- Extracting synchronized frame-audio pairs at a specific frames-per-second (FPS) rate.
- Uploading all extracted artifacts (video, audio, transcript, frame-audio pairs) to designated AWS S3 buckets.

This processed data can then be used to train various multi-modal AI models, such as Audio-to-Video (A2V), Audio-to-Image (A2I), or Audio-to-Text (A2T) models.

## Architecture

The architecture consists of two main parts: the data processing scripts and the cloud infrastructure.

### Data Processing (Python Scripts)

- **youtube_video_links.py**: Scrapes video URLs from a target YouTube channel.
- **aws.py**: The core processing script. It takes a list of YouTube URLs, downloads each video, performs extraction and transcription, and uploads the results to S3. This script is intended to be run on an EC2 instance.
- **extract_frames_audio_FPS2_prototype.py**: A utility script focused on extracting synchronized video frames and short audio clips.

### Infrastructure (Terraform)

- The `Infrastructure` directory contains Terraform code to provision all necessary AWS resources.
- It creates five distinct EC2 instances, each designated for a specific part of the data pipeline (e.g., general processing, Audio-to-Audio, Audio-to-Video).
- It also configures a shared security group and sets up user data scripts to automatically initialize the EC2 instances on boot (e.g., cloning repos, installing dependencies, setting up scripts).

## Getting Started: Developer Guide

Follow these steps to set up the project environment and start contributing.

### Prerequisites

- An AWS account with programmatic access (Access Key ID and Secret Access Key).
- Terraform installed on your local machine.
- Python 3.x installed.
- An AWS EC2 Key Pair (.pem file) for SSH access. Ensure the key name matches the one specified in `Infrastructure/envs/dev/terraform.tfvars` (e.g., `YQA_key`).

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone <repository-url>
cd Audio2Any_Pipeline
```

### Step 2: Configure AWS Credentials

Ensure your AWS credentials are set up correctly. You can configure them as environment variables:

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_REGION="ap-south-1"
```

Alternatively, you can use the AWS CLI to configure a profile.

### Step 3: Set up Terraform

Navigate to the development environment directory:

```bash
cd Infrastructure/envs/dev
```

Initialize Terraform. This will download the necessary provider plugins.

```bash
terraform init
```

### Step 4: Deploy the Infrastructure

Before deploying, review the variables in `terraform.tfvars` and `variables.tf` to ensure they match your AWS environment (e.g., `vpc_id`, `ami_id`, `key_name`).

To see what resources Terraform will create, run:

```bash
terraform plan
```

If the plan looks correct, apply the changes to deploy the infrastructure:

```bash
terraform apply
```

Type `yes` when prompted to confirm. Terraform will now provision the five EC2 instances and the security group. The public IPs of the instances will be displayed as outputs.

### Step 5: Running the Data Pipeline

1. **SSH into the main EC2 instance**: Use the public IP from the Terraform output and your .pem key to connect.

```bash
ssh -i "path/to/your/YQA_key.pem" ubuntu@<public_ip_of_instance_1>
```

2. **Prepare the YouTube links**:
   - Inside the EC2 instance, navigate to the cloned repository (the user data script should have cloned it to `/home/ubuntu/Video_links_extraction`).
   - Run `youtube_video_links.py` to generate a `youtube_video_links.txt` file.

```bash
cd /home/ubuntu/Video_links_extraction
python3 youtube_video_links.py
```

You will be prompted to enter a YouTube channel ID.

3. **Execute the main processing script**:
   - Run the `aws.py` script, which is located in the parent directory.

```bash
cd /home/ubuntu/
# Assuming the aws.py script and vosk model are placed here
python3 aws.py
```

The script will ask for the path to the text file containing the YouTube links. Provide the path to the file you just generated: `/home/ubuntu/Video_links_extraction/youtube_video_links.txt`.

The pipeline will start processing the videos one by one. You can monitor the progress in the console.

## Codebase Deep Dive

### youtube_video_links.py

- **Purpose**: Fetches all video URLs from a given YouTube channel ID.
- **Functionality**: Uses the YouTube Data API v3 to interact with the service. It first finds the 'uploads' playlist for the channel and then iterates through the playlist to retrieve all video IDs.
- **Output**: Saves the list of full YouTube video URLs to a file named `youtube_video_links.txt`.

### aws.py

- **Purpose**: The main orchestration script that processes a list of YouTube video URLs.
- **Key Functions**:
  - `download_youtube_video()`: Downloads a video using yt-dlp.
  - `extract_audio()`: Extracts a WAV audio file from the video using ffmpeg.
  - `transcribe_audio()`: Loads a local Vosk model to perform speech-to-text transcription.
  - `extract_fps_frames_and_audio_chunks()`: Extracts video frames and corresponding 0.5-second audio chunks at a fixed FPS. This is crucial for creating paired data for models like A2I.
  - `upload_to_s3()`: Uses boto3 to upload files to an S3 bucket.
  - `run_pipeline_for_url()`: Sequentially calls all the above functions for a single video URL.
  - `process_links_from_file()`: Reads URLs from a text file and processes them in a batch.

### extract_frames_audio_FPS2_prototype.py

- **Purpose**: A standalone script for testing and prototyping the frame-audio extraction logic.
- **Methodology**:
  - Uses ffmpeg with the fps filter to extract frames.
  - It cleverly parses ffmpeg's showinfo log output to get the precise presentation timestamp (PTS) for each extracted frame.
  - It renames the frame files to include their exact timestamp.
  - For each timestamped frame, it extracts a 0.5-second audio chunk starting from that exact timestamp.
- **Returns**: A list of tuples, where each tuple contains the file path for a frame and its corresponding audio chunk.

## Infrastructure as Code (IaC) with Terraform

The infrastructure is managed entirely through Terraform, ensuring it is version-controlled, repeatable, and easy to manage.

### Directory Structure

```
Infrastructure/
├── modules/
│   └── ec2/         # Reusable module to create an EC2 instance
│       ├── main.tf
│       ├── outputs.tf
│       └── variables.tf
└── envs/
    └── dev/         # 'dev' environment configuration
        ├── main.tf      # Main entrypoint, defines resources
        ├── providers.tf # Defines AWS provider
        ├── variables.tf # Input variables
        ├── outputs.tf   # Outputs (e.g., instance IPs)
        └── terraform.tfvars # Variable values for 'dev'
```

### Key Resources

- **aws_instance** (in `modules/ec2`): A modular resource for creating EC2 instances. It is configured with AMI, instance type, volume size, key pair, and a user data script.
- **aws_security_group** (in `envs/dev/main.tf`): A single, shared security group (`Eira_1_sec_grp`) is created for all instances. It allows inbound SSH traffic (port 22) from any IP and all outbound traffic.
- **User Data**: Each EC2 module in `envs/dev/main.tf` has a `user_data` script. These are shell scripts that run on the instance's first boot. They are used to:
  - Update the OS and install dependencies (git, python3-pip).
  - Clone necessary repositories.
  - Set up environment variables or configuration files.
  - Create and configure the data loading scripts that copy files between S3 buckets.
