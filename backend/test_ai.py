import requests

def test_ai_endpoints():
    data = {
        "n": 90,
        "p": 42,
        "k": 43,
        "temperature": 20.8,
        "humidity": 82,
        "ph": 6.5,
        "rainfall": 202,
        "user_id": 1
    }
    
    # Test FastAPI (on port 8002)
    url_fastapi = "http://localhost:8002/recommend_crop"
    print(f"Testing FastAPI {url_fastapi}...")
    try:
        response = requests.post(url_fastapi, data=data)
        print(f"Status: {response.status_code}")
        print(f"Result: {response.json()}")
    except Exception as e:
        print(f"FastAPI Error: {e}")

    # Test Django (on port 8000)
    url_django = "http://localhost:8000/recommend_crop/"
    print(f"\nTesting Django {url_django}...")
    try:
        # Django Rest Framework usually expects JSON if content type is set, but here it's Form data
        response = requests.post(url_django, data=data)
        print(f"Status: {response.status_code}")
        print(f"Result: {response.json()}")
    except Exception as e:
        print(f"Django Error: {e}")

if __name__ == "__main__":
    test_ai_endpoints()
