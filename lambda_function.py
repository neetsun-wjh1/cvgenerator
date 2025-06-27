import json
import customLogging
import ai
from config import Config

# Set up logging
logger = customLogging.safe_logger_setup()

def validate_request_body(body):
    """
    Validate the request body structure
    Expected: {'name': 'value', 'country': 'value', 'designation': 'value' (optional)}
    """
    
    # Check if body is a dictionary
    if not isinstance(body, dict):
        return {
            'valid': False,
            'message': 'Request body must be a JSON object'
        }
    
    # Check required fields
    required_fields = ['name', 'country','transactionId']
    missing_fields = []
    
    for field in required_fields:
        if field not in body:
            missing_fields.append(field)
        elif not body[field] or not isinstance(body[field], str) or not body[field].strip():
            missing_fields.append(f"{field} (empty or invalid)")
    
    if missing_fields:
        return {
            'valid': False,
            'message': f"Missing or invalid required fields: {', '.join(missing_fields)}"
        }
    
    # Check for unexpected fields (optional validation)
    allowed_fields = ['name', 'country', 'designation', 'transactionId']
    unexpected_fields = [field for field in body.keys() if field not in allowed_fields]
    
    if unexpected_fields:
        logger.warning(f"Unexpected fields in request: {unexpected_fields}")
        # You can choose to reject or just warn
        # For now, we'll just log a warning and continue
    
    # Validate designation if provided
    if 'designation' in body:
        if body['designation'] is not None and not isinstance(body['designation'], str):
            return {
                'valid': False,
                'message': 'Designation must be a string or null'
            }
    
    return {'valid': True, 'message': 'Valid'}

def process_person_data(request_body):
    """
    Process the validated person data
    """
    try: 
        # Extract and clean the data
        name = request_body['name'].strip()
        country = request_body['country'].strip()
        designation = request_body.get('designation', '').strip() if request_body.get('designation') else ''
        transactionId = request_body['transactionId'].strip()
        
        logger.info(f"Processing data for Transaction No {transactionId}: Profile Name - {name}, Country - {country}, Designation - {designation}")
        
        # Initialize AI graph
        logger.info("initialize build graph")
        graph = ai.create_graph()
        
        # Process messages using AI
        response, threadid = ai.process_messages(
            name=name,
            countryName=country,
            designation=designation,
            transaction_id=transactionId,
            human_message_template=Config.HUMAN_MESSAGE_TEMPLATE,
            sectionNameList=["main_particulars", "education", "career", "appointments", "reference"],
            graph=graph
        )
        
        logger.info(f"AI processing completed. Thread ID: {threadid}")
        
       # Return the AI response and transactionId
        return response
    
    except Exception as e:
        logger.error(f"Error processing person data: {str(e)}")
        raise Exception(f"Failed to process person data: {str(e)}")

def context_timestamp():
    """Generate timestamp for response"""
    from datetime import datetime
    return datetime.timezone.utc.isoformat() + 'Z'

def lambda_handler(event, context):
    """
    AWS Lambda function to handle POST requests with name/country/designation JSON body
    """
    
    try:
        # Log the incoming event for debugging
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Only handle POST requests
        http_method = event.get('httpMethod', '')
        if http_method != 'POST':
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Method not allowed. Only POST requests are supported.'
                })
            }
        
        # Check if body exists
        if not event.get('body'):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Request body is required'
                })
            }
        
        # Parse JSON body
        try:
            body_content = event['body']
            
            # Handle base64 encoded body if necessary
            if event.get('isBase64Encoded', False):
                import base64
                body_content = base64.b64decode(body_content).decode('utf-8')
            
            request_body = json.loads(body_content)
            logger.info(f"Parsed request body: {request_body}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON body: {str(e)}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid JSON format in request body',
                    'message': str(e)
                })
            }
        
        # Validate and process the request body
        validation_result = validate_request_body(request_body)
        if not validation_result['valid']:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Validation failed',
                    'message': validation_result['message']
                })
            }
        
        # Process the valid request using AI
        try:
            response_data = process_person_data(request_body)
        except Exception as e:
            logger.error(f"Error in AI processing: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Internal server error during AI processing',
                    'message': str(e)
                })
            }
       
        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }
       
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }