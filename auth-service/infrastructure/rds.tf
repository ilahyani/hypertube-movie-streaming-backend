resource "aws_db_instance" "hyperdb" {
  allocated_storage        = 20
  engine                   = "postgres"
  engine_version           = "16.1"
  identifier               = "hyperdb"
  instance_class           = "db.t3.micro"
  db_name                  = var.db_name
  username                 = var.db_user
  password                 = var.db_passwd
  storage_encrypted        = false
  multi_az                 = false
  publicly_accessible      = true
  delete_automated_backups = true
  skip_final_snapshot      = true
  apply_immediately        = true
  vpc_security_group_ids   = [aws_security_group.rds_sg.id]
}

resource "aws_security_group" "rds_sg" {
  name        = "rds_sg"
  description = "Allow PostgreSQL traffic"

  ingress {
    from_port   = 5432
    to_port     = 5432
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
