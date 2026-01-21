import json
import uuid
from datetime import datetime

# In-memory storage (in production, you could use DynamoDB)
tasks = {}

def lambda_handler(event, context):
    """
    Main Lambda handler that routes requests based on HTTP method and path
    """
    # This is the request routing logic
    # Get request details
    http_method = event['httpMethod']
    path = event['path']
    path_parameters = event.get('pathParameters') or {}
    
    print(f"Method: {http_method}, Path: {path}")
    
    try:
        # Route the request based on HTTP method and path
        if http_method == 'GET' and path == '/tasks':
            return get_all_tasks()
        elif http_method == 'POST' and path == '/tasks':
            return create_task(event)
        elif http_method == 'GET' and path.startswith('/tasks/'):
            task_id = path_parameters.get('id')
            return get_task(task_id)
        else:
            return create_response(404, {'error': 'Not Found'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error'})

def get_all_tasks():
    """Get all tasks"""
    task_list = list(tasks.values())
    return create_response(200, {
        'tasks': task_list,
        'count': len(task_list)
    })

def create_task(event):
    """Create a new task"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        title = body.get('title')
        
        if not title:
            return create_response(400, {'error': 'Title is required'})
        
        # Create new task
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'title': title,
            'description': body.get('description', ''),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store task
        tasks[task_id] = task
        
        return create_response(201, {
            'message': 'Task created successfully',
            'task': task
        })
        
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON'})

def get_task(task_id):
    """Get a specific task by ID"""
    if not task_id:
        return create_response(400, {'error': 'Task ID is required'})
    
    task = tasks.get(task_id)
    if not task:
        return create_response(404, {'error': 'Task not found'})
    
    return create_response(200, {'task': task})

def create_response(status_code, body):
    """Create a standardized HTTP response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
