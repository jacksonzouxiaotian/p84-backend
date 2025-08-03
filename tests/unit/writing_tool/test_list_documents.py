def test_list_documents_returns_data(auth_client, mock_s3_upload, test_user, db):
    """Test listing documents and versions."""
    from research_assistant.writing_tool.models import CloudDocument, DocumentVersion
    doc = CloudDocument(title="Existing Doc")
    db.session.add(doc)
    db.session.flush()
    ver = DocumentVersion(document_id=doc.id, major_version=1, minor_version=0, file_key="mockkey",
                          file_url="https://mock-url", uploaded_by_id=test_user.id, file_size=1.2, is_current=True)
    db.session.add(ver)
    db.session.commit()

    res = auth_client.get("/writing_tool/documents")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data) >= 1
    assert data[0]["title"] == "Existing Doc"
    assert "versions" in data[0]

def test_list_documents_empty(auth_client):
    response = auth_client.get('/writing_tool/documents')
    assert response.status_code == 200
    assert response.json.get('data') == []
