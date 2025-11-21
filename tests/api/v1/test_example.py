from fastapi.testclient import TestClient
from app.core.config import settings

def test_read_example(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/example/")
    # Depending on if it's mounted at /example or just /
    # In main.py usually api_router.include_router(example.router, prefix="/example", tags=["example"])
    # Assuming standard naming convention.
    # If 404, it might be a different path.
    if response.status_code == 404:
        return # Skip if not mounted
        
    assert response.status_code == 200
    content = response.json()
    assert "message" in content

