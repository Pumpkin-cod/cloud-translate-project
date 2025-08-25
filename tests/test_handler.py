import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from handler import lambda_handler # type: ignore

def test_lambda_handler():
    event = {}
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 200
    assert 'Hello from Lambda!' in response['body']