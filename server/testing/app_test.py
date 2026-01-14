import pytest
from app import app, db
from models import Review, User, Game

@pytest.fixture
def client():
    # Use a separate database file for testing to ensure isolation
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing.db'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Seed some data for testing
        user = User(name="Test User")
        game = Game(title="Test Game Unique", genre="Action", platform="PC", price=60)
        db.session.add(user)
        db.session.add(game)
        db.session.commit()
        
        review = Review(score=8, comment="Great game!", game_id=game.id, user_id=user.id)
        db.session.add(review)
        db.session.commit()

        yield app.test_client()
        
        db.session.remove()
        db.drop_all()

def test_get_reviews(client):
    response = client.get('/reviews')
    assert response.status_code == 200
    assert len(response.json) >= 1
    assert response.json[0]['comment'] == "Great game!"

def test_post_review(client):
    data = {
        "score": 10,
        "comment": "Masterpiece!",
        "game_id": 1,
        "user_id": 1
    }
    response = client.post('/reviews', data=data)
    assert response.status_code == 201
    assert response.json['comment'] == "Masterpiece!"
    
    # Verify in DB
    with app.app_context():
        review = Review.query.filter_by(comment="Masterpiece!").first()
        assert review is not None

def test_patch_review(client):
    data = {
        "score": 9,
        "comment": "Actually, it's pretty good."
    }
    response = client.patch('/reviews/1', data=data)
    assert response.status_code == 200
    assert response.json['score'] == 9
    assert response.json['comment'] == "Actually, it's pretty good."

def test_delete_review(client):
    response = client.delete('/reviews/1')
    assert response.status_code == 200
    assert response.json['delete_successful'] is True
    
    # Verify in DB
    with app.app_context():
        review = Review.query.get(1)
        assert review is None

def test_get_nonexistent_review(client):
    response = client.get('/reviews/999')
    assert response.status_code == 404
    assert "does not exist" in response.json['message']
