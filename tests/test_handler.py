import json
import sys
import os
import pytest
from unittest.mock import Mock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from moto import mock_s3, mock_translate
import boto3
from handler import lambda_handler

@mock_s3
@mock_translate
def test_successful_translation():
    # Setup mock AWS services
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-requests')
    s3.create_bucket(Bucket='test-responses')
    
    # Mock environment variables
    os.environ['REQUESTS_BUCKET'] = 'test-requests'
    os.environ['RESPONSES_BUCKET'] = 'test-responses'
    
    # Test event
    event = {
        "source_lang": "en",
        "target_lang": "fr",
        "texts": ["Hello", "World"]
    }
    
    context = Mock()
    context.aws_request_id = "test-request-id"
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'jobId' in body
    assert 'outputKey' in body
    assert body['responsesBucket'] == 'test-responses'

def test_missing_environment_variables():
    # Clear environment variables
    os.environ.pop('REQUESTS_BUCKET', None)
    os.environ.pop('RESPONSES_BUCKET', None)
    
    event = {"source_lang": "en", "target_lang": "fr", "texts": ["Hello"]}
    context = Mock()
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['error'] == 'InternalServerError'

def test_invalid_input():
    os.environ['REQUESTS_BUCKET'] = 'test-requests'
    os.environ['RESPONSES_BUCKET'] = 'test-responses'
    
    # Missing required fields
    event = {"source_lang": "en"}
    context = Mock()
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'BadRequest'

def test_api_gateway_event():
    os.environ['REQUESTS_BUCKET'] = 'test-requests'
    os.environ['RESPONSES_BUCKET'] = 'test-responses'
    
    # API Gateway HTTP API v2 format
    event = {
        "body": json.dumps({
            "source_lang": "en",
            "target_lang": "fr",
            "texts": ["Hello"]
        })
    }
    context = Mock()
    
    with mock_s3(), mock_translate():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-requests')
        s3.create_bucket(Bucket='test-responses')
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200