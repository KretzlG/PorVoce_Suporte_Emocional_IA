
import pytest
from app.models.user import User, UserRole

def test_user_creation():
    user = User(
        email='test@teste.com',
        username='testuser',
        first_name='Test',
        last_name='User',
        role=UserRole.CLIENT
    )
    user.set_password('senha123')
    assert user.check_password('senha123')
    assert user.full_name == 'Test User'
    assert user.is_client
    assert not user.is_admin
