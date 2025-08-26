import json
import sys
import os
import pytest
from unittest.mock import Mock, patch

# Ensure handler.py is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))
from handler import lambda_handler


# ---- Helpers ----
class SimpleContext:
    aws_request_id = "test-request-id"


# ---- Tests ----
@patch('handler.boto3.client')
def test_successful_translation(mock_boto_client):
    os.environ['REQUESTS_BUCKET'] = 'test-requests'
    os.environ['RESPONSES_BUCKET'] = 'test-responses'
    
    mock_s3 = Mock()
    mock_translate = Mock()
    mock_translate.translate_text.return_value = {
        'TranslatedText': 'Bonjour',
        'SourceLanguageCode': 'en',
        'TargetLanguageCode': 'fr'
    }

    def client_side_effect(service_name):
        return {'s3': mock_s3, 'translate': mock_translate}.get(service_name, Mock())
    
    mock_boto_client.side_effect = client_side_effect

    event = {"source_lang": "en", "target_lang": "fr", "texts": ["Hello"]}
    response = lambda_handler(event, SimpleContext())

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'jobId' in body
    assert 'outputKey' in body
    assert body['responsesBucket'] == 'test-responses'

    # Validate AWS calls
    mock_translate.translate_text.assert_called_with(
        Text="Hello", SourceLanguageCode="en", TargetLanguageCode="fr"
    )
    assert mock_s3.put_object.call_count == 2  # request + response saved


def test_missing_environment_variables():
    os.environ.pop('REQUESTS_BUCKET', None)
    os.environ.pop('RESPONSES_BUCKET', None)

    event = {"source_lang": "en", "target_lang": "fr", "texts": ["Hello"]}
    response = lambda_handler(event, SimpleContext())

    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['error'] == 'InternalServerError'


@pytest.mark.parametrize("event", [
    {"source_lang": "en"},  # missing target_lang & texts
    {"target_lang": "fr", "texts": ["Hello"]},  # missing source_lang
    {"source_lang": "en", "target_lang": "fr"},  # missing texts
    {"source_lang": "en", "target_lang": "en", "texts": ["Hello"]},  # same lang
    {"source_lang": "en", "target_lang": "fr", "texts": []}  # empty array
])
def test_invalid_inputs(event):
    os.environ['REQUESTS_BUCKET'] = 'test-requests'
    os.environ['RESPONSES_BUCKET'] = 'test-responses'

    response = lambda_handler(event, SimpleContext())

    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'BadRequest'


@patch('handler.boto3.client')
def test_api_gateway_event(mock_boto_client):
    os.environ['REQUESTS_BUCKET'] = 'test-requests'
    os.environ['RESPONSES_BUCKET'] = 'test-responses'

    mock_s3 = Mock()
    mock_translate = Mock()
    mock_translate.translate_text.return_value = {
        'TranslatedText': 'Bonjour',
        'SourceLanguageCode': 'en',
        'TargetLanguageCode': 'fr'
    }

    def client_side_effect(service_name):
        return {'s3': mock_s3, 'translate': mock_translate}.get(service_name, Mock())
    
    mock_boto_client.side_effect = client_side_effect

    event = {
        "body": json.dumps({
            "source_lang": "en",
            "target_lang": "fr",
            "texts": ["Hello"]
        })
    }

    response = lambda_handler(event, SimpleContext())
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['responsesBucket'] == 'test-responses'
