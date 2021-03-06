from fastapi.testclient import TestClient
from jose import jwt

from app import models
from app.auth import auth_router


HTTP_200_OK = 200
HTTP_401_UNAUTHORIZED = 401
TEST_SECRET_KEY = 'samplekeyfortests'
TEST_ALGORITHM = 'HS256'


def test_login(monkeypatch, test_app: TestClient):
    mock_user = models.User(
            first_name='Test',
            last_name='User',
            email='test@user.com',
            id=1,
            team_id=1)
    data_to_encode = {'sub': mock_user.email, 'exp': 15}
    access_token = jwt.encode(data_to_encode, TEST_SECRET_KEY, TEST_ALGORITHM)

    def mock_authenticate_user(*args):
        return mock_user

    def mock_create_access_token(*args, **kwargs):
        return access_token

    monkeypatch.setattr(models.User, 'authenticate_user', mock_authenticate_user)
    monkeypatch.setattr(auth_router, 'create_access_token', mock_create_access_token)

    form_data = dict(username=mock_user.email, password='password', scope='')
    response = test_app.post('/token', data=form_data)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {'access_token': access_token, 'token_type': 'bearer'}


def test_login_invalid(monkeypatch, test_app: TestClient):
    def mock_authenticate_user(*args):
        return None

    monkeypatch.setattr(models.User, 'authenticate_user', mock_authenticate_user)

    form_data = dict(username='bad@email.com', password='password')
    response = test_app.post('/token', data=form_data)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == 'Could not validate credentials'


def test_read_users_me(test_app: TestClient):
    response = test_app.get('/self/me')
    response_data = response.json()
    assert response_data['id'] == 1
    assert response_data['first_name'] == 'Test'
    assert response_data['last_name'] == 'User'
    assert response_data['email'] == 'test@user.com'
    assert response_data['team_id'] == 1
