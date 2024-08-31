resource "aws_instance" "auth_service" {
  ami                    = "ami-0e86e20dae9224db8"
  instance_type          = "t2.micro"
  key_name               = aws_key_pair.auth_service_key.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]
  iam_instance_profile   = aws_iam_instance_profile.instance_profile.name
  tags = {
    Name = "AuthServiceInstance"
  }
}

resource "tls_private_key" "ssh_key_pair" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "auth_service_key" {
  key_name   = "auth_service_key"
  public_key = tls_private_key.ssh_key_pair.public_key_openssh
}

resource "local_file" "private_key_pem" {
  content  = tls_private_key.ssh_key_pair.private_key_pem
  filename = "${path.module}/aws_ec2_key.pem"
}

resource "null_resource" "set_permissions" {
  provisioner "local-exec" {
    command = "chmod 600 ${path.module}/aws_ec2_key.pem"
  }

  depends_on = [local_file.private_key_pem]
}

resource "aws_security_group" "allow_ssh" {
  name_prefix = "allow_ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.ip_address
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "public_ip" {
  value = aws_instance.auth_service.public_ip
}
