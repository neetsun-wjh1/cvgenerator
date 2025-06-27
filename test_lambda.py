#!/usr/bin/env python3
"""
Local test script for the Lambda function
This simulates the AWS Lambda environment for local testing
"""

import json
import sys
import os
from datetime import datetime

# Add the current directory to Python path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your Lambda function (assuming it's in the same directory)
from lambda_function import lambda_handler  # Replace 'paste' with your actual filename

def create_mock_event(method='POST', body_data=None, is_base64=False):
    """
    Create a mock AWS API Gateway event for testing
    """
    event = {
        'httpMethod': method,
        'headers': {
            'Content-Type': 'application/json',
            'User-Agent': 'test-client/1.0'
        },
        'isBase64Encoded': is_base64,
        'path': '/your-api-path',
        'queryStringParameters': None,
        'requestContext': {
            'requestId': 'test-request-id',
            'stage': 'test'
        }
    }
    
    if body_data:
        if isinstance(body_data, dict):
            event['body'] = json.dumps(body_data)
        else:
            event['body'] = body_data
    else:
        event['body'] = None
    
    return event

def create_mock_context():
    """
    Create a mock AWS Lambda context for testing
    """
    class MockContext:
        def __init__(self):
            self.function_name = 'test-function'
            self.function_version = '$LATEST'
            self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test-function'
            self.memory_limit_in_mb = 128
            self.remaining_time_in_millis = lambda: 30000
            self.log_group_name = '/aws/lambda/test-function'
            self.log_stream_name = '2023/01/01/test-stream'
            self.aws_request_id = 'test-request-id'
    
    return MockContext()

def test_valid_request():
    """Test with valid request data"""
    print("🧪 Testing valid request...")
    
    test_data = {
        "name": "Cho Tae-yul",
        "country": "Korea",
        "designation": "",
        "transactionId": "TXN-12345"
    }
    
    event = create_mock_event('POST', test_data)
    context = create_mock_context()
    
    try:
        response = lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        print(f"Response Body: {json.dumps(json.loads(response['body']), indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_missing_fields():
    """Test with missing required fields"""
    print("\nTesting missing required fields...")
    
    test_data = {
        'name': 'John Doe',
        # Missing country and transactionId
    }
    
    event = create_mock_event('POST', test_data)
    context = create_mock_context()
    
    try:
        response = lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        print(f"Response Body: {json.dumps(json.loads(response['body']), indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_invalid_method():
    """Test with invalid HTTP method"""
    print("\nTesting invalid HTTP method...")
    
    event = create_mock_event('GET')  # Should only accept POST
    context = create_mock_context()
    
    try:
        response = lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        print(f"Response Body: {json.dumps(json.loads(response['body']), indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_invalid_json():
    """Test with invalid JSON"""
    print("\nTesting invalid JSON...")
    
    event = create_mock_event('POST', '{"invalid": json}')  # Invalid JSON
    context = create_mock_context()
    
    try:
        response = lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        print(f"Response Body: {json.dumps(json.loads(response['body']), indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_empty_body():
    """Test with empty body"""
    print("\nTesting empty body...")
    
    event = create_mock_event('POST')  # No body
    context = create_mock_context()
    
    try:
        response = lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        print(f"Response Body: {json.dumps(json.loads(response['body']), indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def interactive_test():
    """Interactive test mode - enter your own data"""
    print("\nInteractive Test Mode")
    print("Enter the test data (or press Enter to skip):")
    
    name = input("Name: ").strip()
    country = input("Country: ").strip()
    designation = input("Designation (optional): ").strip()
    transaction_id = input("Transaction ID: ").strip()
    
    if not name and not country and not transaction_id:
        print("No data entered, skipping interactive test.")
        return
    
    test_data = {}
    if name:
        test_data['name'] = name
    if country:
        test_data['country'] = country
    if designation:
        test_data['designation'] = designation
    if transaction_id:
        test_data['transactionId'] = transaction_id
    
    print(f"\nTesting with your data: {json.dumps(test_data, indent=2)}")
    
    event = create_mock_event('POST', test_data)
    context = create_mock_context()
    
    try:
        response = lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        print(f"Response Body: {json.dumps(json.loads(response['body']), indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    """Run all tests"""
    print("Starting Lambda Function Local Tests")
    print("=" * 50)
    
    # Run automated tests
    # test_valid_request()
    # test_missing_fields()
    # test_invalid_method()
    # test_invalid_json()
    # test_empty_body()
    
    # Interactive test
    try:
        interactive_test()
    except KeyboardInterrupt:
        print("\nInteractive test cancelled by user")
    
    print("\nAll tests completed!")

if __name__ == '__main__':
    main()