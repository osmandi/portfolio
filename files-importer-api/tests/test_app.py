import json
from io import BytesIO


def test_hello_world(client):
    res = client.get("/")
    assert res.status_code == 200
    message_expected = {"message": "Hello from root!"}
    assert message_expected == json.loads(res.get_data(as_text=True))


def test_file_different_csv(client):
    response = client.post("/upload", data={"pdf": (BytesIO(b"Test"), "test.pdf")})
    assert response.status_code == 415
    message_expected = {"message": "Error - The file is not a CSV file"}
    assert message_expected == json.loads(response.get_data(as_text=True))
