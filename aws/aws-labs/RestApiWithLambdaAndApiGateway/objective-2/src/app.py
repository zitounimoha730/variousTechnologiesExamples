import json
import uuid
import os
from datetime import datetime
import logging

# Configure logging based on environment
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# Environment variables
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
API_STAGE = os.environ.get('API_STAGE', 'v1')

# In-memory storage (in production, you'd use DynamoDB)
tasks = {}

def lambda_handler(event, context):
    """
    Enhanced Lambda handler with custom response handling and environment awareness
    """
    
    # Log request details
    http_method = event['httpMethod']
    path = event['path']
    
    logger.info(f"Environment: {ENVIRONMENT}, Method: {http_method}, Path: {path}")
    
    try:
        # Route the request
        if http_method == 'GET' and path == '/health':
            return health_check()
        elif http_method == 'GET' and path == '/tasks':
            return get_all_tasks()
        elif http_method == 'POST' and path == '/tasks':
            return create_task(event)
        else:
            return create_error_response(404, 'NOT_FOUND', 'Endpoint not found')
            
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return create_error_response(500, 'INTERNAL_ERROR', 'Internal server error occurred')

def health_check():
    """Health check endpoint demonstrating custom response handling"""
    return create_success_response(200, {
        'status': 'healthy',
        'environment': ENVIRONMENT,
        'stage': API_STAGE,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    })

def get_all_tasks():
    """Get all tasks with enhanced response format"""
    task_list = list(tasks.values())
    
    return create_success_response(200, {
        'tasks': task_list,
        'count': len(task_list)
    })

def create_task(event):
    """Create a new task with enhanced validation and response handling"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        title = body.get('title', '').strip()
        description = body.get('description', '').strip()
        
        # Enhanced validation
        validation_errors = []
        
        if not title:
            validation_errors.append('Title is required')
        elif len(title) > 100:
            validation_errors.append('Title must be 100 characters or less')
            
        if len(description) > 500:
            validation_errors.append('Description must be 500 characters or less')
        
        if validation_errors:
            return create_error_response(400, 'VALIDATION_ERROR', 'Validation failed', 
                                       details={'errors': validation_errors})
        
        # Create new task
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'title': title,
            'description': description,
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

def create_success_response(status_code, data):
    """Create a standardized success response with custom headers"""
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
    """Create a standardized error response with custom headers"""
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
