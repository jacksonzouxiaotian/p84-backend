import io

def test_create_document_success(auth_client, mock_s3_upload, test_user):
    """Test creating a new document with first version."""
    data = {"title": "My Doc"}
    file_data = (io.BytesIO(b"file content"), "test.docx")
    res = auth_client.post("/writing_tool/documents", data={"title": data["title"], "file": file_data})
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["code"] == 0
    assert "document_id" in json_data

def test_create_document_missing_file(auth_client):
    """Test creating document without file should fail."""
    res = auth_client.post("/writing_tool/documents", data={"title": "Doc without file"})
    assert res.status_code == 400
    assert res.get_json()["code"] == 1

def test_create_document_missing_title(auth_client, mock_s3_upload):
    response = auth_client.post('/writing_tool/documents', data={}, content_type='multipart/form-data')
    assert response.status_code == 400

def test_create_document_missing_file(auth_client, mock_s3_upload):
    response = auth_client.post('/writing_tool/documents', data={'title': 'No file'}, content_type='multipart/form-data')
    assert response.status_code == 400
