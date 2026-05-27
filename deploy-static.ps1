param(
    [string]$StackName = "cloud-engineer-portfolio",
    [string]$ProjectName = "cloud-engineer-portfolio",
    [string]$Region = "ap-southeast-2"
)

$ErrorActionPreference = "Stop"

aws cloudformation deploy `
    --stack-name $StackName `
    --template-file "infra/static-site.yaml" `
    --parameter-overrides ProjectName=$ProjectName `
    --region $Region

$bucketName = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" `
    --output text

$distributionId = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" `
    --output text

$siteUrl = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomainName'].OutputValue" `
    --output text

aws s3 sync . "s3://$bucketName" `
    --region $Region `
    --exclude ".git/*" `
    --exclude ".github/*" `
    --exclude "infra/*" `
    --exclude "__pycache__/*" `
    --exclude "queries.db" `
    --exclude "*.pyc" `
    --exclude "server.py" `
    --exclude "deploy-static.ps1"

aws cloudfront create-invalidation `
    --distribution-id $distributionId `
    --paths "/*"

Write-Host "Deployed portfolio to $siteUrl"
