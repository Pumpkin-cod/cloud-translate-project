import json
import sys
import os
import pytest
from unittest.mock import Mock, patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from moto import mock_aws
import boto3
from handler import lambda_handler

@patch('handler.boto3.client')
def test_successful_translation(mock_boto_client):
    # Mock environment variables
    os.environ['REQUESTS_BUCKET'] = 'test-requests'
    os.environ['RESPONSES_BUCKET'] = 'test-responses'
    
    # Mock S3 and Translate clients
    mock_s3 = Mock()
    mock_translate = Mock()
    mock_translate.translate_text.return_value = {
        'TranslatedText': 'Bonjour',
        'SourceLanguageCode': 'en',
        'TargetLanguageCode': 'fr'
    }
    
    def client_side_effect(service_name):
        if service_name == 's3':
            return mock_s3
        elif service_name == 'translate':
            return mock_translate
        return Mock()
    
    mock_boto_client.side_effect = client_side_effect
    
    # Test event
    event = {
        "source_lang": "en",
        "target_lang": "fr",
        "texts": ["Hello"]
    }
    
    # Simple context object
    class SimpleContext:
        aws_request_id = "test-request-id"
    
    context = SimpleContext()
    
    response = lambda_handler(event, context)
    
    if response['statusCode'] != 200:
        print(f"Error response: {response}")
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
    
    class SimpleContext:
        aws_request_id = "test-request-id"
    
    context = SimpleContext()
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['error'] == 'InternalServerError'

def test_invalid_input():
    os.environ['REQUESTS_BUCKET'] = 'test-requests'
    os.environ['RESPONSES_BUCKET'] = 'test-responses'
    
    # Missing required fields
    event = {"source_lang": "en"}
    
    class SimpleContext:
        aws_request_id = "test-request-id"
    
    context = SimpleContext()
    
    response = lambda_handler(event, context)
    
    if response['statusCode'] != 400:
        print(f"Error response: {response}")
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'BadRequest'

@patch('handler.boto3.client')
def test_api_gateway_event(mock_boto_client):
    os.environ['REQUESTS_BUCKET'] = 'test-requests'
    os.environ['RESPONSES_BUCKET'] = 'test-responses'
    
    # Mock clients
    mock_s3 = Mock()
    mock_translate = Mock()
    mock_translate.translate_text.return_value = {
        'TranslatedText': 'Bonjour',
        'SourceLanguageCode': 'en',
        'TargetLanguageCode': 'fr'
    }
    
    def client_side_effect(service_name):
        if service_name == 's3':
            return mock_s3
        elif service_name == 'translate':
            return mock_translate
        return Mock()
    
    mock_boto_client.side_effect = client_side_effect
    
    # API Gateway HTTP API v2 format
    event = {
        "body": json.dumps({
            "source_lang": "en",
            "target_lang": "fr",
            "texts": ["Hello"]
        })
    }
    
    class SimpleContext:
        aws_request_id = "test-request-id"
    
    context = SimpleContext()
    
    response = lambda_handler(event, context)
    
    if response['statusCode'] != 200:
        print(f"Error response: {response}")
    assert response['statusCode'] == 200