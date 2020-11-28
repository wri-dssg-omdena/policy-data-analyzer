# Create the basic infrasturcture on AWS
In order to use the commands below you have to install and configure the AWS CLI.

## Create S3 bucket on AWS from the CLI
```
aws s3api create-bucket --bucket wri-latin-test --region us-west-1 --create-bucket-configuration 
```

## Create keypair for EC2 instance from the AWS CLI
```
aws ec2 create-key-pair --key-name WRIEC2 --output text > WRIEC2.pem
```


## Create the infrastructure stack
```
aws cloudformation create-stack --stack-name WRI-latin-infra --template-body file://infrastructure.yml --parameters file://infrastructure-params.json --region us-west-1 --capabilities CAPABILITY_NAMED_IAM 
```

## Update the infrastructure stack
```
aws cloudformation update-stack --stack-name WRI-latin-infra --template-body file://infrastructure-pw.yml --parameters file://infrastructure-params.json --region us-west-1 --capabilities CAPABILITY_NAMED_IAM --profile Omdena
```

## Create the database stack
```
aws cloudformation create-stack --stack-name WRI-latin-db --template-body file://database.yml --parameters file://database-params.json --region us-west-1 --capabilities CAPABILITY_NAMED_IAM 
```

## Create the server stack
```
aws cloudformation create-stack --stack-name WRI-latin-server --template-body file://server.yml --parameters file://server-params.json --region us-west-1 --capabilities CAPABILITY_NAMED_IAM 
```

## Update stack
```
aws cloudformation update-stack --stack-name WRI-latin-server --template-body file://server.yml --parameters file://server-params.json --region us-west-1 --capabilities CAPABILITY_NAMED_IAM 
```

## Describe stack
```
aws cloudformation describe-stack-resources --stack-name WRI-latin-server
```

## Delete the stack
```
aws cloudformation delete-stack --stack-name WRI-latin-server
```


