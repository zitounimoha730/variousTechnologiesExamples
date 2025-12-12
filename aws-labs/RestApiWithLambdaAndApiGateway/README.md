# Building a Serverless REST API with Lambda and API Gateway

Building a Serverless REST API with Lambda and API Gateway
## Introduction
In this hands-on lab, you'll build a serverless REST API from scratch using AWS best practices. Starting with basic Lambda functions, you'll progress through packaging with AWS SAM, configuring API Gateway endpoints, and implementing production-ready features like error handling and retry logic.

## Solution
### Objective One : Deploy and validate a serverless API using AWS SAM
Open AWS CloudShell, then install and configure Python 3.12:

```
sudo dnf install python3.12 python3.12-pip -y
sudo ln -sf /usr/bin/python3.12 /usr/bin/python
sudo ln -sf /usr/bin/pip3.12 /usr/bin/pip
```

Download and extract the lab files:

```
git clone https://github.com/pluralsight-cloud/lab-Building-a-Serverless-REST-API-with-Lambda-and-API-Gateway.git
cd lab-Building-a-Serverless-REST-API-with-Lambda-and-API-Gateway
unzip lab-files.zip
cd lab-files/objective-1
```

Review the SAM template:
```

cat template.yaml
```
Review the Lambda function code:
```
cat src/app.py
```

Validate and build the template:
```
sam validate
sam build
```

Deploy the application:
```
sam deploy --guided
```

When prompted, use these settings:

Stack Name: task-api-basic
Accept defaults for region
Confirm changes: N
Allow IAM role creation: Y
Disable rollback: N
TaskFunction has no authentication. Is this okay?: Y
Save arguments to configuration file: Y
Accept defaults for SAM configuration file: Press Enter to accept the defult
Accept defaults for SAM configuration environment: Press Enter to accept the defult
You may see repeated questions about TaskFunction has no authentication. Is this okay? - answer Y to all of them. This happens because SAM checks each API endpoint individually.

To test the API, first get your API URL:
```
API_URL=$(aws cloudformation describe-stacks \
 --stack-name task-api-basic \
 --query "Stacks[0].Outputs[?OutputKey=='TaskApiUrl'].OutputValue" \
 --output text)
 ```

If given a Safe Paste pop-up, uncheck the box then click Paste. (Press Enter to execute the command.)

Test the endpoint by creating a task:
```
curl -X POST "${API_URL}/tasks" \
 -H "Content-Type: application/json" \
 -d '{"title": "Call Vet", "description": "Book vaccinations for Ralph"}'
 ```

Get all tasks to view the created task:
```
curl -X GET "${API_URL}/tasks"
```

To review the Lambda function using the AWS console, in the search bar type Lambda and click on it, click on your function with the prefix task-api-basic-TaskFunction-

To review the API Gateway using the AWS console, in the search bar type API Gateway and click on it, click on your API named: task-api-basic

### Objective Two: Configure production-ready API Gateway settings
Navigate to the directory named objective-2
```
cd ../objective-2
```

Review the code in the SAM template that adds API Gateway staging environments, custom response handling and API Gateway routes:
```
cat template.yaml
```

Review the Lambda function code, that adds custom response handling and environment awareness:
```
cat src/app.py
```

Update the application using AWS SAM:
```
sam build
```

Deploy the development environment:
```
sam deploy --guided \
    --parameter-overrides Environment=dev ApiStageName=v1
```

When prompted, use these settings:

Stack Name: task-api-dev
Accept defaults for region
Parameter environment: dev
Parameter API stagename: v1
Confirm changes: N
Allow IAM role creation: Y
Disable rollback: N
TaskFunction has no authentication. Is this okay?: Y
Save arguments to configuration file: Y
Accept defaults for SAM configuration file: Press Enter to accept the defult
Accept defaults for SAM configuration environment: Press Enter to accept the defult
You may see repeated questions about TaskFunction has no authentication. Is this okay? - answer Y to all of them. This happens because SAM checks each API endpoint individually.

Deploy separate staging environment:
```
sam deploy --stack-name task-api-staging \
 --parameter-overrides Environment=staging ApiStageName=v1 \
 --no-confirm-changeset
```

Deploy separate production environment:
```
sam deploy --stack-name task-api-prod \
 --parameter-overrides Environment=prod ApiStageName=v1 \
 --no-confirm-changeset
```
To test the new API routes we just created, first get the API URLs for all environments:
```
DEV_API_URL=$(aws cloudformation describe-stacks \
 --stack-name task-api-dev \
 --query "Stacks[0].Outputs[?OutputKey=='TaskApiUrl'].OutputValue" \
 --output text)

STAGING_API_URL=$(aws cloudformation describe-stacks \
 --stack-name task-api-staging \
 --query "Stacks[0].Outputs[?OutputKey=='TaskApiUrl'].OutputValue" \
 --output text)

PROD_API_URL=$(aws cloudformation describe-stacks \
 --stack-name task-api-prod \
 --query "Stacks[0].Outputs[?OutputKey=='TaskApiUrl'].OutputValue" \
 --output text)
```

Print the API URLs for each environment:
```
echo "Dev API URL: $DEV_API_URL"

echo "Staging API URL: $STAGING_API_URL"

echo "Production API URL: $PROD_API_URL"
```

Perform a health check by calling the GET method on the API health route in each environment:
```
curl -s -X GET "${DEV_API_URL}/health" | jq '.data.environment'

curl -s -X GET "${STAGING_API_URL}/health" | jq '.data.environment'

curl -s -X GET "${PROD_API_URL}/health" | jq '.data.environment'
```

View the custom headers that we configured:
```
curl -i "${DEV_API_URL}/health"
```

You should see custom headers like:

x-environment: dev
x-api-stage: v1
x-timestamp: 2025-12-12T17:00:45.549417
Perform a validation check by calling the POST method on the API tasks route, to create a new task:
```
curl -X POST "${DEV_API_URL}/tasks" \
 -H "Content-Type: application/json" \
 -d '{"title": "Pack for vacation"}'
```

### Objective Three: Implement reliability patterns for your API
Navigate to the directory named objective-3 Review the code in the SAM template and Lambda function code that adds the SQS dead letter queue and retry handling:
```
cd ../objective-3
cat template.yaml

cat src/app.py
```

Update the application to add the new features using AWS SAM, this will update your existing task-api-dev stack:
```
sam build
 
sam deploy --guided \
 --parameter-overrides Environment=dev ApiStageName=v1
```

When prompted, use these settings:

Stack Name: task-api-dev
Accept defaults for region
Parameter environment: dev
Parameter API stagename: v1
Confirm changes: N
Allow IAM role creation: Y
Disable rollback: N
TaskFunction has no authentication. Is this okay?: Y
Save arguments to configuration file: Y
Accept defaults for SAM configuration file: Press Enter to accept the defult
Accept defaults for SAM configuration environment: Press Enter to accept the defult
You may see repeated questions about TaskFunction has no authentication. Is this okay? - answer Y to all of them. This happens because SAM checks each API endpoint individually.

Update other environments
```
sam deploy \
 --stack-name task-api-staging \
 --parameter-overrides Environment=staging ApiStageName=v1 \
 --no-confirm-changeset
sam deploy \
 --stack-name task-api-prod \
 --parameter-overrides Environment=prod ApiStageName=v1 \
 --no-confirm-changeset
```

To verify the DLQ configuration, first get the API URLs

Get API URL:
```
DEV_API_URL=$(aws cloudformation describe-stacks \
    --stack-name task-api-dev \
    --query "Stacks[0].Outputs[?OutputKey=='TaskApiUrl'].OutputValue" \
    --output text)
```

Get DLQ URL:
```
DLQ_URL=$(aws cloudformation describe-stacks \
    --stack-name task-api-dev \
    --query "Stacks[0].Outputs[?OutputKey=='TaskDLQUrl'].OutputValue" \
    --output text)
echo "API URL: $DEV_API_URL"
echo "DLQ URL: $DLQ_URL"
```

Test the DLQ configuration, by checking the health status:
```
curl -X GET "${DEV_API_URL}/health" | jq '.data.features'
```

Test the error handling scenarios Create a task with no title:
```
curl -X POST "${DEV_API_URL}/tasks" \
  -H "Content-Type: application/json" \
  -d '{"description": "No title"}' | jq '.'
```

Create a task with invalid priority:
```
curl -X POST "${DEV_API_URL}/tasks" \
 -H "Content-Type: application/json" \
 -d '{"title": "Test", "priority": "invalid"}' | jq '.'
```

Test by creating server errors (5xx) that should trigger DLQ

Test unhandled exception:
```
   curl -X POST "${DEV_API_URL}/test/error" \
   -H "Content-Type: application/json" \
   -d '{"errorType": "exception"}' | jq '.'
```

Test DLQ message sending:
```
curl -X POST "${DEV_API_URL}/test/error" \
  -H "Content-Type: application/json" \
  -d '{"errorType": "dlq"}' | jq '.'
```

Receive messages from DLQ
```
aws sqs receive-message \
  --queue-url "$DLQ_URL" \
  --max-number-of-messages 5 \
  --query "Messages[*].Body" \
  --output json | jq '.'
```

Test retry behavior with random errors
```
echo "Testing retry behavior..."
for i in {1..10}; do
    echo -n "Attempt $i: "
    curl -s -X POST "${DEV_API_URL}/test/error" \
    -H "Content-Type: application/json" \
    -d '{"errorType": "random"}' | \
    jq -r 'if .success then "SUCCESS - " + .data.message else "ERROR - " + .error.message end'
    sleep 1
done
```