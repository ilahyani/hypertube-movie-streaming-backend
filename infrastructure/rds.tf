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
}
