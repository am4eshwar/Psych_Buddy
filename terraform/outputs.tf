output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.psych_buddy.id
}

output "instance_public_ip" {
  description = "Public IP address of the deployed bot"
  value       = aws_instance.psych_buddy.public_ip
}

output "ssh_login_command" {
  description = "Command to SSH into instance"
  value       = "ssh -i ${var.private_key_path} ubuntu@${aws_instance.psych_buddy.public_ip}"
}

output "service_status_command" {
  description = "Command to check bot service status"
  value       = "ssh -i ${var.private_key_path} ubuntu@${aws_instance.psych_buddy.public_ip} 'sudo systemctl status psych-buddy'"
}

output "service_logs_command" {
  description = "Command to view live logs"
  value       = "ssh -i ${var.private_key_path} ubuntu@${aws_instance.psych_buddy.public_ip} 'journalctl -u psych-buddy -f'"
}
