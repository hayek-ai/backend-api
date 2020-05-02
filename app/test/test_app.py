from app.main import create_app
import json


def test_config():
    assert not create_app('development').testing
    assert create_app('testing').testing


def test_hello(client):
    response = client.get('/hello')
    assert json.loads(response.data) == {'hello': 'world'}
