import io

def test_upload_new_version(auth_client, mock_s3_upload, test_user, db):
    """Test uploading a new version of a document."""
    from research_assistant.writing_tool.models import CloudDocument
    doc = CloudDocument(title="Doc")
    db.session.add(doc)
    db.session.commit()

    file_data = (io.BytesIO(b"new content"), "new.docx")
    res = auth_client.post(f"/writing_tool/documents/{doc.id}/versions", data={"file": file_data})
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["code"] == 0
    assert "version" in json_data

def test_upload_version_missing_file(auth_client):
    response = auth_client.post('/writing_tool/documents/1/versions', data={}, content_type='multipart/form-data')
    assert response.status_code == 400

def test_upload_version_nonexistent_document(auth_client):
    data = {'file': (io.BytesIO(b"dummy"), 'test.docx')}
    response = auth_client.post('/writing_tool/documents/999/versions', data=data, content_type='multipart/form-data')
    assert response.status_code == 404
