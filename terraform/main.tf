terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Fetch default VPC
data "aws_vpc" "default" {
  default = true
}

# Fetch latest Ubuntu 24.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"] # Canonical
}

# Security group
resource "aws_security_group" "psych_buddy_sg" {
  name        = "psych-buddy-sg"
  description = "Security group for Psych Buddy EC2"
  vpc_id      = data.aws_vpc.default.id

  # Inbound SSH
  ingress {
    description = "SSH from allowed IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  # All outbound traffic
  egress {
    description = "Outbound connections"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "psych-buddy-sg"
  }
}

# EC2 Instance
resource "aws_instance" "psych_buddy" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  vpc_security_group_ids      = [aws_security_group.psych_buddy_sg.id]
  associate_public_ip_address = true

  root_block_device {
    volume_size           = 25
    volume_type           = "gp3"
    delete_on_termination = true
  }

  # SSH connection configuration for provisioners
  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file(var.private_key_path)
    host        = self.public_ip
    timeout     = "5m"
  }

  # Step 1: Create application directory on remote instance
  provisioner "remote-exec" {
    inline = [
      "mkdir -p /home/ubuntu/psych-agent",
      "mkdir -p /home/ubuntu/psych-agent/logs"
    ]
  }

  # Step 2: Upload source files and directories from local project
  provisioner "file" {
    source      = "${path.module}/../config"
    destination = "/home/ubuntu/psych-agent/config"
  }

  provisioner "file" {
    source      = "${path.module}/../core"
    destination = "/home/ubuntu/psych-agent/core"
  }

  provisioner "file" {
    source      = "${path.module}/../mcp"
    destination = "/home/ubuntu/psych-agent/mcp"
  }

  provisioner "file" {
    source      = "${path.module}/../models"
    destination = "/home/ubuntu/psych-agent/models"
  }

  provisioner "file" {
    source      = "${path.module}/../utils"
    destination = "/home/ubuntu/psych-agent/utils"
  }

  provisioner "file" {
    source      = "${path.module}/../main.py"
    destination = "/home/ubuntu/psych-agent/main.py"
  }

  provisioner "file" {
    source      = "${path.module}/../requirements.txt"
    destination = "/home/ubuntu/psych-agent/requirements.txt"
  }

  provisioner "file" {
    source      = "${path.module}/../.env"
    destination = "/home/ubuntu/psych-agent/.env"
  }

  provisioner "file" {
    source      = "${path.module}/../credentials.json"
    destination = "/home/ubuntu/psych-agent/credentials.json"
  }

  provisioner "file" {
    source      = "${path.module}/../token.json"
    destination = "/home/ubuntu/psych-agent/token.json"
  }

  # Step 3: Configure swap, install dependencies, and setup systemd service
  provisioner "remote-exec" {
    inline = [
      "set -e",

      # Configure swap space
      "sudo fallocate -l 2G /swapfile || true",
      "sudo chmod 600 /swapfile",
      "sudo mkswap /swapfile || true",
      "sudo swapon /swapfile || true",
      "echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab",

      # Install system packages
      "sudo apt-get update -y",
      "sudo apt-get install -y python3-pip python3-venv build-essential",

      # Setup Python virtual environment
      "python3 -m venv /home/ubuntu/psych-agent/venv",
      "/home/ubuntu/psych-agent/venv/bin/pip install --upgrade pip",
      "/home/ubuntu/psych-agent/venv/bin/pip install -r /home/ubuntu/psych-agent/requirements.txt",

      # Create systemd service
      "sudo bash -c 'cat << \"SERVICE\" > /etc/systemd/system/psych-buddy.service\n[Unit]\nDescription=Psych Buddy ReAct Agent System\nAfter=network.target\n\n[Service]\nType=simple\nUser=ubuntu\nWorkingDirectory=/home/ubuntu/psych-agent\nEnvironment=PYTHONUNBUFFERED=1\nExecStart=/home/ubuntu/psych-agent/venv/bin/python main.py\nRestart=always\nRestartSec=10\nKillSignal=SIGINT\nTimeoutStopSec=30\n\n[Install]\nWantedBy=multi-user.target\nSERVICE'",

      # Enable and start service
      "sudo systemctl daemon-reload",
      "sudo systemctl enable psych-buddy",
      "sudo systemctl restart psych-buddy"
    ]
  }

  tags = {
    Name = "psych-buddy-instance"
  }
}
