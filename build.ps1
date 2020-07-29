[CmdletBinding()]
param (
    [String]$AccountId = "780016325729",
    [String]$Region = "us-east-1",
    [String][Parameter(Mandatory = $true)]$Tag,
    [switch]$Local
)

if ($Local) {
    docker build -t con-pca-api:$Tag .
}
else {
    docker build "https://github.com/cisagov/con-pca-api.git#develop" -t con-pca-api:$Tag
}

aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com/con-pca-api"
docker tag "con-pca-api:$Tag" "$AccountId.dkr.ecr.$Region.amazonaws.com/con-pca-api:$Tag"
docker push "$AccountId.dkr.ecr.$Region.amazonaws.com/con-pca-api:$Tag"
