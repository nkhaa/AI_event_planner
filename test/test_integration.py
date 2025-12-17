
import pytest
import os
import sys
import tempfile
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import app, init_db


@pytest.fixture
def client():
    """Test client with temporary database"""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    # Override database path
    original_db = 'event.db'
    if os.path.exists(original_db):
        os.rename(original_db, f'{original_db}.backup')
    
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink('event.db')
    
    # Restore original database
    if os.path.exists(f'{original_db}.backup'):
        os.rename(f'{original_db}.backup', original_db)


@pytest.fixture
def user_data():
    """Sample user data"""
    return {
        "identifier": "test@example.com",
        "password": "password123",
        "user_type": "user"
    }


@pytest.fixture
def provider_data():
    """Sample provider data"""
    return {
        "identifier": "provider@example.com",
        "password": "password123",
        "user_type": "provider"
    }


@pytest.fixture
def venue_data():
    """Sample venue data"""
    return {
        "name": "Grand Hall",
        "location": "Улаанбаатар, СБД",
        "capacity": 200,
        "price": 5000000,
        "packages": "Төрсөн өдөр, Хурим, Бизнес уулзалт",
        "description": "Орчин үеийн тохижилттай том танхим",
        "contact_phone": "99001122",
        "contact_email": "info@grandhall.mn",
        "image_url": "https://example.com/hall.jpg"
    }


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Нэвтрэх системийн тестүүд"""
    
    def test_register_user_success(self, client, user_data):
        """✅ Хэрэглэгч амжилттай бүртгүүлэх"""
        response = client.post('/register', json=user_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['user_type'] == 'user'
        assert 'user_id' in data
    
    def test_register_provider_success(self, client, provider_data):
        """✅ Үйлчилгээ үзүүлэгч амжилттай бүртгүүлэх"""
        response = client.post('/register', json=provider_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['user_type'] == 'provider'
    
    def test_register_duplicate_user(self, client, user_data):
        """❌ Давхардсан хэрэглэгч бүртгэх"""
        # First registration
        client.post('/register', json=user_data)
        
        # Try duplicate
        response = client.post('/register', json=user_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'бүртгэлтэй' in data['error']
    
    def test_register_invalid_email(self, client):
        """❌ Буруу и-мэйл форматаар бүртгэх"""
        response = client.post('/register', json={
            "identifier": "invalid-email",
            "password": "password123"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_register_short_password(self, client):
        """❌ Богино нууц үгээр бүртгэх"""
        response = client.post('/register', json={
            "identifier": "test@example.com",
            "password": "12345"  # Too short
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'нууц үг' in data['error'].lower()
    
    def test_register_missing_fields(self, client):
        """❌ Талбар дутуу бүртгэх"""
        response = client.post('/register', json={
            "identifier": "test@example.com"
            # Missing password
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_login_success(self, client, user_data):
        """✅ Амжилттай нэвтрэх"""
        # Register first
        client.post('/register', json=user_data)
        
        # Logout to test login
        client.post('/logout')
        
        # Login
        response = client.post('/login', json={
            "identifier": user_data['identifier'],
            "password": user_data['password']
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['user_type'] == user_data['user_type']
    
    def test_login_wrong_password(self, client, user_data):
        """❌ Буруу нууц үгээр нэвтрэх"""
        # Register first
        client.post('/register', json=user_data)
        client.post('/logout')
        
        # Try login with wrong password
        response = client.post('/login', json={
            "identifier": user_data['identifier'],
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_nonexistent_user(self, client):
        """❌ Бүртгэлгүй хэрэглэгчээр нэвтрэх"""
        response = client.post('/login', json={
            "identifier": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401
    
    def test_logout_success(self, client, user_data):
        """✅ Амжилттай гарах"""
        # Register and login
        client.post('/register', json=user_data)
        
        # Logout
        response = client.post('/logout')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
    
    def test_current_user_authenticated(self, client, user_data):
        """✅ Нэвтэрсэн хэрэглэгчийн мэдээлэл авах"""
        # Register (auto-login)
        client.post('/register', json=user_data)
        
        # Get current user
        response = client.get('/api/current-user')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['identifier'] == user_data['identifier']
        assert data['user_type'] == user_data['user_type']
    
    def test_current_user_not_authenticated(self, client):
        """❌ Нэвтрээгүй байхад мэдээлэл авах"""
        response = client.get('/api/current-user')
        
        assert response.status_code == 401


# ============================================================================
# PROVIDER MANAGEMENT TESTS
# ============================================================================

class TestProviderManagement:
    """Үйлчилгээ удирдлагын тестүүд"""
    
    def test_register_venue_success(self, client, provider_data, venue_data):
        """✅ Үйлчилгээ амжилттай бүртгэх"""
        # Register as provider
        client.post('/register', json=provider_data)
        
        # Register venue
        response = client.post('/api/providers/register', json=venue_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'provider_id' in data
        assert data['message'] == 'Үйлчилгээ амжилттай бүртгэгдлээ!'
    
    def test_register_venue_not_authenticated(self, client, venue_data):
        """❌ Нэвтрээгүй байхад үйлчилгээ бүртгэх"""
        response = client.post('/api/providers/register', json=venue_data)
        
        assert response.status_code == 401
    
    def test_register_venue_missing_fields(self, client, provider_data):
        """❌ Талбар дутуу үйлчилгээ бүртгэх"""
        client.post('/register', json=provider_data)
        
        response = client.post('/api/providers/register', json={
            "name": "Test Hall"
            # Missing required fields
        })
        
        assert response.status_code == 400
    
    def test_register_venue_invalid_capacity(self, client, provider_data, venue_data):
        """❌ Буруу хүчин чадалтай үйлчилгээ бүртгэх"""
        client.post('/register', json=provider_data)
        
        venue_data['capacity'] = 0  # Invalid
        response = client.post('/api/providers/register', json=venue_data)
        
        assert response.status_code == 400
    
    def test_register_venue_negative_price(self, client, provider_data, venue_data):
        """❌ Сөрөг үнэтэй үйлчилгээ бүртгэх"""
        client.post('/register', json=provider_data)
        
        venue_data['price'] = -1000  # Invalid
        response = client.post('/api/providers/register', json=venue_data)
        
        assert response.status_code == 400
    
    def test_get_provider_by_id(self, client, provider_data, venue_data):
        """✅ ID-гаар үйлчилгээ олох"""
        # Register provider and venue
        client.post('/register', json=provider_data)
        reg_response = client.post('/api/providers/register', json=venue_data)
        provider_id = reg_response.get_json()['provider_id']
        
        # Get provider
        response = client.get(f'/api/providers/{provider_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == venue_data['name']
        assert data['location'] == venue_data['location']
    
    def test_get_provider_not_found(self, client):
        """❌ Олдохгүй үйлчилгээ хайх"""
        response = client.get('/api/providers/99999')
        
        assert response.status_code == 404
    
    def test_get_my_providers(self, client, provider_data, venue_data):
        """✅ Миний үйлчилгээнүүдийг авах"""
        # Register provider
        client.post('/register', json=provider_data)
        
        # Register multiple venues
        client.post('/api/providers/register', json=venue_data)
        
        venue_data2 = venue_data.copy()
        venue_data2['name'] = 'Small Hall'
        client.post('/api/providers/register', json=venue_data2)
        
        # Get my providers
        response = client.get('/api/providers/my')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
    
    def test_get_my_providers_not_authenticated(self, client):
        """❌ Нэвтрээгүй байхад миний үйлчилгээ авах"""
        response = client.get('/api/providers/my')
        
        assert response.status_code == 401
    
    def test_update_provider_success(self, client, provider_data, venue_data):
        """✅ Үйлчилгээ амжилттай засах"""
        # Register provider and venue
        client.post('/register', json=provider_data)
        reg_response = client.post('/api/providers/register', json=venue_data)
        provider_id = reg_response.get_json()['provider_id']
        
        # Update venue
        update_data = {"name": "Updated Hall", "price": 6000000}
        response = client.put(f'/api/providers/{provider_id}', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        
        # Verify update
        get_response = client.get(f'/api/providers/{provider_id}')
        updated = get_response.get_json()
        assert updated['name'] == 'Updated Hall'
        assert updated['price'] == 6000000
    
    def test_update_provider_not_owner(self, client, provider_data, user_data, venue_data):
        """❌ Өөрийн биш үйлчилгээ засах"""
        # Register provider and venue
        client.post('/register', json=provider_data)
        reg_response = client.post('/api/providers/register', json=venue_data)
        provider_id = reg_response.get_json()['provider_id']
        
        # Logout and login as different user
        client.post('/logout')
        client.post('/register', json=user_data)
        
        # Try to update
        response = client.put(f'/api/providers/{provider_id}', json={"name": "Hacked"})
        
        assert response.status_code == 403
    
    def test_delete_provider_success(self, client, provider_data, venue_data):
        """✅ Үйлчилгээ амжилттай устгах"""
        # Register provider and venue
        client.post('/register', json=provider_data)
        reg_response = client.post('/api/providers/register', json=venue_data)
        provider_id = reg_response.get_json()['provider_id']
        
        # Delete
        response = client.delete(f'/api/providers/{provider_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        
        # Verify deletion
        get_response = client.get(f'/api/providers/{provider_id}')
        assert get_response.status_code == 404
    
    def test_delete_provider_not_owner(self, client, provider_data, user_data, venue_data):
        """❌ Өөрийн биш үйлчилгээ устгах"""
        # Register provider and venue
        client.post('/register', json=provider_data)
        reg_response = client.post('/api/providers/register', json=venue_data)
        provider_id = reg_response.get_json()['provider_id']
        
        # Logout and login as different user
        client.post('/logout')
        client.post('/register', json=user_data)
        
        # Try to delete
        response = client.delete(f'/api/providers/{provider_id}')
        
        assert response.status_code == 403


# ============================================================================
# SEARCH TESTS
# ============================================================================

class TestSearch:
    """Хайлтын тестүүд"""
    
    def test_search_all_providers(self, client, provider_data, venue_data):
        """✅ Бүх үйлчилгээ хайх"""
        # Register provider and venues
        client.post('/register', json=provider_data)
        client.post('/api/providers/register', json=venue_data)
        
        venue_data2 = venue_data.copy()
        venue_data2['name'] = 'Small Hall'
        client.post('/api/providers/register', json=venue_data2)
        
        # Search without filters
        response = client.get('/api/providers/search')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
    
    def test_search_by_location(self, client, provider_data, venue_data):
        """✅ Байршлаар хайх"""
        # Register venues in different locations
        client.post('/register', json=provider_data)
        
        venue1 = venue_data.copy()
        venue1['location'] = 'Улаанбаатар, СБД'
        client.post('/api/providers/register', json=venue1)
        
        venue2 = venue_data.copy()
        venue2['name'] = 'Countryside Hall'
        venue2['location'] = 'Дархан'
        client.post('/api/providers/register', json=venue2)
        
        # Search for Улаанбаатар
        response = client.get('/api/providers/search?location=Улаанбаатар')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert 'Улаанбаатар' in data[0]['location']
    
    def test_search_by_price_range(self, client, provider_data, venue_data):
        """✅ Үнийн хязгаараар хайх"""
        client.post('/register', json=provider_data)
        
        # Register venues with different prices
        venue1 = venue_data.copy()
        venue1['price'] = 3000000
        client.post('/api/providers/register', json=venue1)
        
        venue2 = venue_data.copy()
        venue2['name'] = 'Expensive Hall'
        venue2['price'] = 10000000
        client.post('/api/providers/register', json=venue2)
        
        # Search for affordable venues
        response = client.get('/api/providers/search?min_price=0&max_price=5000000')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['price'] <= 5000000
    
    def test_search_by_capacity(self, client, provider_data, venue_data):
        """✅ Хүчин чадлаар хайх"""
        client.post('/register', json=provider_data)
        
        # Register venues with different capacities
        venue1 = venue_data.copy()
        venue1['capacity'] = 50
        client.post('/api/providers/register', json=venue1)
        
        venue2 = venue_data.copy()
        venue2['name'] = 'Large Hall'
        venue2['capacity'] = 500
        client.post('/api/providers/register', json=venue2)
        
        # Search for venues with capacity >= 100
        response = client.get('/api/providers/search?capacity=100')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['capacity'] >= 100
    
    def test_search_by_event_type(self, client, provider_data, venue_data):
        """✅ Эвентийн төрлөөр хайх"""
        client.post('/register', json=provider_data)
        
        venue1 = venue_data.copy()
        venue1['packages'] = 'Төрсөн өдөр, Хурим'
        client.post('/api/providers/register', json=venue1)
        
        venue2 = venue_data.copy()
        venue2['name'] = 'Business Center'
        venue2['packages'] = 'Бизнес уулзалт, Семинар'
        client.post('/api/providers/register', json=venue2)
        
        # Search for wedding venues
        response = client.get('/api/providers/search?event_type=Хурим')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert 'Хурим' in data[0]['packages']
    
    def test_search_combined_filters(self, client, provider_data, venue_data):
        """✅ Олон шүүлтүүрээр хайх"""
        client.post('/register', json=provider_data)
        
        # Register multiple venues
        for i in range(3):
            venue = venue_data.copy()
            venue['name'] = f'Hall {i+1}'
            venue['location'] = 'Улаанбаатар' if i < 2 else 'Дархан'
            venue['price'] = 3000000 + (i * 2000000)
            venue['capacity'] = 100 + (i * 100)
            client.post('/api/providers/register', json=venue)
        
        # Search with multiple filters
        response = client.get(
            '/api/providers/search?'
            'location=Улаанбаатар&'
            'min_price=2000000&'
            'max_price=6000000&'
            'capacity=150'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1  # Only Hall 2 matches


# ============================================================================
# STATS TESTS
# ============================================================================

class TestStats:
    """Статистикийн тестүүд"""



# ============================================================================
# PAGE ROUTES TESTS
# ============================================================================

class TestPageRoutes:
    """Хуудасны тестүүд"""
    
    def test_index_page(self, client):
        """✅ Нүүр хуудас"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Event Planner' in response.data
    
    def test_dashboard_authenticated(self, client, user_data):
        """✅ Нэвтэрсэн хэрэглэгчийн dashboard"""
        client.post('/register', json=user_data)
        
        response = client.get('/dashboard')
        
        assert response.status_code == 200
        assert b'dashboard' in response.data or b'Dashboard' in response.data
    
    def test_dashboard_not_authenticated(self, client):
        """❌ Нэвтрээгүй dashboard"""
        response = client.get('/dashboard')
        
        assert response.status_code == 200
        # Should redirect to index
        assert b'Event Planner' in response.data
    
    def test_search_page(self, client):
        """✅ Хайлтын хуудас"""
        response = client.get('/search')
        
        assert response.status_code == 200
        assert b'search' in response.data or b'Search' in response.data
    
    def test_provider_register_page_authenticated(self, client, provider_data):
        """✅ Үйлчилгээ бүртгэх хуудас (нэвтэрсэн)"""
        client.post('/register', json=provider_data)
        
        response = client.get('/provider-register')
        
        assert response.status_code == 200
    
    def test_provider_register_page_not_authenticated(self, client):
        """❌ Үйлчилгээ бүртгэх хуудас (нэвтрээгүй)"""
        response = client.get('/provider-register')
        
        assert response.status_code == 200
        # Should show index
        assert b'Event Planner' in response.data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])