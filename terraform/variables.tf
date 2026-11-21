variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance size"
  default     = "t3.small"
}

variable "key_name" {
  type        = string
  description = "Name of existing AWS EC2 Key Pair"
}

variable "private_key_path" {
  type        = string
  description = "Local path to your .pem private key file for SSH"
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "CIDR block allowed to SSH into the instance"
  default     = "0.0.0.0/0"
}
