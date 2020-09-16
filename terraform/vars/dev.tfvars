app    = "con-pca"
region = "us-east-1"
env = "dev"

vpc_id = "vpc-074f7db64238a2d16"

private_subnet_ids = [
    "subnet-0153f175feb0dfce5",
    "subnet-02f0f6199dd75238b"
]

public_subnet_ids = [
    "subnet-0a365c16b67a2b6b0",
    "subnet-0ea8f699bed93417c"
]

image_repo = "780016325729.dkr.ecr.us-east-1.amazonaws.com/con-pca-api"

domain_name = "con-pca.dev.inltesting.xyz"

yearly_minutes = "30"
cycle_minutes = "15"
monthly_minutes = "10"
