import json
import uuid
import os
import boto3
from datetime import datetime
import logging

# Configure logging based on environment
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# Environment variables
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
API_STAGE = os.environ.get('API_STAGE', 'v1')
DLQ_URL = os.environ.get('DLQ_URL')  # NEW in Objective 3

# AWS clients (NEW in Objective 3)
sqs = boto3.client('sqs')

# In-memory storage (in production, you'd use DynamoDB)
tasks = {}

def lambda_handler(event, context):
    """
    Lambda handler with DLQ integration and error handling
    """
    
    # Log request details
    http_method = event['httpMethod']
    path = event['path']
    
    logger.info(f"Environment: {ENVIRONMENT}, Method: {http_method}, Path: {path}")
    
    try:
        # Route the request (same as Objective 2 + new error testing endpoint)
        if http_method == 'GET' and path == '/health':
            return health_check()
        elif http_method == 'GET' and path == '/tasks':
            return get_all_tasks()
        elif http_method == 'POST' and path == '/tasks':
            return create_task(event)
        elif http_method == 'POST' and path == '/test/error':  # NEW in Objective 3
            return test_error_handling(event)
        else:
            return create_error_response(404, 'NOT_FOUND', 'Endpoint not found')
            
    except Exception as e:
        # NEW in Objective 3: Send unhandled errors to DLQ
        send_error_to_dlq(e, context, event, "unhandled_exception")
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return create_error_response(500, 'INTERNAL_ERROR', 'Internal server error occurred')

def health_check():
    """Health check endpoint with DLQ status (enhanced from Objective 2)"""
    return create_success_response(200, {
        'status': 'healthy',
        'environment': ENVIRONMENT,
        'stage': API_STAGE,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '3.0.0',  # Updated version
        'features': {  # NEW: Show DLQ status
            'dlq': 'enabled' if DLQ_URL else 'disabled',
            'error_handling': 'enabled'
        }
    })

def get_all_tasks():
    """Get all tasks (same as Objective 2)"""
    task_list = list(tasks.values())
    
    return create_success_response(200, {
        'tasks': task_list,
        'count': len(task_list)
    })

def create_task(event):
    """Create a new task with validation (same as Objective 2)"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        title = body.get('title', '').strip()
        description = body.get('description', '').strip()
        priority = body.get('priority', 'medium').strip().lower()  # NEW: priority validation
        
        # Validation (enhanced from Objective 2)
        validation_errors = []
        
        if not title:
            validation_errors.append('Title is required')
        elif len(title) > 100:
            validation_errors.append('Title must be 100 characters or less')
            
        if len(description) > 500:
            validation_errors.append('Description must be 500 characters or less')
        
        # NEW: Priority validation
        if priority not in ['low', 'medium', 'high']:
            validation_errors.append('Priority must be low, medium, or high')
        
        if validation_errors:
            return create_error_response(400, 'VALIDATION_ERROR', 'Validation failed', 
                                       details={'errors': validation_errors})
        
        # Create new task
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'title': title,
            'description': description,
            'priority': priority,  # NEW field
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'environment': ENVIRONMENT
        }
        
        # Store task
        tasks[task_id] = task
        
        logger.info(f"Task created: {task_id}")
        
        return create_success_response(201, {
            'message': 'Task created successfully',
            'task': task
        })
        
    except json.JSONDecodeError:
        return create_error_response(400, 'INVALID_JSON', 'Request body must be valid JSON')

def test_error_handling(event):
    """NEW in Objective 3: Test error handling and DLQ functionality"""
    try:
        body = json.loads(event.get('body', '{}'))
        error_type = body.get('errorType', 'exception')
        
        if error_type == 'exception':
            # Trigger an unhandled exception
            raise Exception("Test exception for DLQ testing")
        
        elif error_type == 'dlq':
            # Manually send a message to DLQ
            send_error_to_dlq(
                Exception("Manual DLQ test"), 
                event.get('requestContext', {}), 
                event, 
                "manual_dlq_test"
            )
            return create_success_response(200, {
                'message': 'Test message sent to DLQ',
                'dlq_url': DLQ_URL
            })
        
        elif error_type == 'random':
            # Random success/failure for retry testing
            import random
            if random.random() < 0.7:  # 70% chance of failure
                raise Exception("Random test failure")
            else:
                return create_success_response(200, {
                    'message': 'Random test passed',
                    'success_rate': '30%'
                })
        
        else:
            return create_error_response(400, 'INVALID_ERROR_TYPE', 
                                       'errorType must be: exception, dlq, or random')
    
    except json.JSONDecodeError:
        return create_error_response(400, 'INVALID_JSON', 'Request body must be valid JSON')

def send_error_to_dlq(error, context, event, error_type):
    """NEW in Objective 3: Send error details to Dead Letter Queue"""
    if not DLQ_URL:
        logger.warning("DLQ_URL not configured, cannot send error to DLQ")
        return
    
    try:
        error_message = {
            'errorType': error_type,
            'errorMessage': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'environment': ENVIRONMENT,
            'functionName': context.function_name if hasattr(context, 'function_name') else 'unknown',
            'requestId': context.aws_request_id if hasattr(context, 'aws_request_id') else 'unknown',
            'event': {
                'httpMethod': event.get('httpMethod'),
                'path': event.get('path'),
                'body': event.get('body')
            }
        }
        
        sqs.send_message(
            QueueUrl=DLQ_URL,
            MessageBody=json.dumps(error_message),
            MessageAttributes={
                'ErrorType': {
                    'StringValue': error_type,
                    'DataType': 'String'
                },
                'Environment': {
                    'StringValue': ENVIRONMENT,
                    'DataType': 'String'
                }
            }
        )
        
        logger.info(f"Error sent to DLQ: {error_type}")
        
    except Exception as dlq_error:
        logger.error(f"Failed to send message to DLQ: {str(dlq_error)}")

def create_success_response(status_code, data):
    """Create a standardized success response (same as Objective 2)"""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'X-Environment': ENVIRONMENT,
        'X-API-Stage': API_STAGE,
        'X-Timestamp': datetime.utcnow().isoformat()
    }
    
    response_body = {
        'success': True,
        'data': data,
        'meta': {
            'environment': ENVIRONMENT,
            'stage': API_STAGE,
            'timestamp': datetime.utcnow().isoformat()
        }
    }
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(response_body)
    }

def create_error_response(status_code, error_code, message, details=None):
    """Create a standardized error response (same as Objective 2)"""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'X-Environment': ENVIRONMENT,
        'X-API-Stage': API_STAGE,
        'X-Timestamp': datetime.utcnow().isoformat()
    }
    
    error_response = {
        'success': False,
        'error': {
            'code': error_code,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': ENVIRONMENT,
            'stage': API_STAGE
        }
    }
    
    if details:
        error_response['error']['details'] = details
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(error_response)
    }
