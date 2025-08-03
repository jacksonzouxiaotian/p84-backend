def test_download_version_success(auth_client, mock_s3_client, test_user, db):
    """Test successfully generating a download link for an existing document version."""
    from research_assistant.writing_tool.models import CloudDocument, DocumentVersion
    
    # Create a test document
    doc = CloudDocument(title="Doc")
    db.session.add(doc)
    db.session.flush()

    # Create a version for the document
    version = DocumentVersion(
        document_id=doc.id,
        major_version=1,
        minor_version=0,
        file_key="mockkey",
        file_url="https://mock-url",
        uploaded_by_id=test_user.id,
        file_size=1.2,
        is_current=True
    )
    db.session.add(version)
    db.session.commit()

    # Request to generate a presigned download URL
    res = auth_client.get(f"/writing_tool/documents/{doc.id}/versions/v1.0/download")
    
    # Assert successful response with mocked URL
    assert res.status_code == 200
    assert res.get_json()["file_url"].startswith("https://mock-presigned-url")


def test_download_nonexistent_version(auth_client, mock_s3_client):
    """Test that requesting a non-existent document version returns 400 or 404."""
    response = auth_client.get('/writing_tool/documents/1/versions/v9.9/download')
    assert response.status_code in (400, 404)
