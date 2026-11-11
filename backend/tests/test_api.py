from app.schemas import CodeReviewRequest


def test_code_review_request_rejects_invalid_syntax():
    try:
        CodeReviewRequest(code='def broken_syntax(:')
        assert False, 'Expected validation error'
    except ValueError:
        pass


def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_review_endpoint_requires_valid_python(client):
    response = client.post('/api/review', json={'code': 'def broken_syntax(:'})
    assert response.status_code == 422


def test_review_endpoint_accepts_valid_python(client):
    code = 'def divide(a, b):\n    return a / b\n'
    response = client.post('/api/review', json={'code': code})
    assert response.status_code == 200
    payload = response.json()
    assert payload['original_code'] == code.strip()
    assert 'findings' in payload
    assert 'summary' in payload
