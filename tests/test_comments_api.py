import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "https://jsonplaceholder.typicode.com"

# Фикстура для API клиента
@pytest.fixture(scope="session")
def api_request_context():
    with sync_playwright() as p:
        request_context = p.request.new_context(base_url=BASE_URL)
        yield request_context
        request_context.dispose()

# Параметризованный тест с валидацией всех полей комментариев для каждого поста
@pytest.mark.parametrize("post_id", range(1, 11))
def test_get_and_validate_comments(api_request_context, post_id):
    response = api_request_context.get(f"/posts/{post_id}/comments")
    assert response.status == 200, f"Expected 200 for post_id={post_id}, got {response.status}"

    data = response.json()
    assert isinstance(data, list), f"Response for post_id={post_id} is not a list"

    for comment in data:
        assert "postId" in comment and comment["postId"] == post_id, f"postId mismatch: {comment}"
        assert "id" in comment and isinstance(comment["id"], int), f"id missing or invalid: {comment}"
        assert "name" in comment and comment["name"].strip(), f"name missing or empty: {comment}"
        assert "email" in comment and "@" in comment["email"], f"email invalid or missing: {comment}"
        assert "body" in comment and comment["body"].strip(), f"body missing or empty: {comment}"

# Базовый тест POST запроса
def test_post_new_comment(api_request_context):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "body": "This is a test comment."
    }
    response = api_request_context.post("/posts/1/comments", data=payload)
    assert response.status == 201  # Created
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["body"] == payload["body"]
    assert "id" in data

# Отправка пустого имени
def test_post_comment_empty_name(api_request_context):
    payload = {
        "name": "",
        "email": "valid@example.com",
        "body": "Comment body"
    }
    response = api_request_context.post("/posts/1/comments", data=payload)
    # Для API jsonplaceholder 201, в реальном API ловим 400
    assert response.status in [201, 400]
    

# Невалидный email (без @)
def test_post_comment_invalid_email(api_request_context):
    payload = {
        "name": "Valid Name",
        "email": "not-an-email",
        "body": "Valid comment"
    }
    response = api_request_context.post("/posts/1/comments", data=payload)
    assert response.status in [201, 400]

# Пустой body
def test_post_comment_empty_body(api_request_context):
    payload = {
        "name": "Another User",
        "email": "user@example.com",
        "body": ""
    }
    response = api_request_context.post("/posts/1/comments", data=payload)
    assert response.status in [201, 400]