def test_delete_document_success(auth_client, mock_s3_client, test_user, db):
    """Test deleting entire document and its versions."""
    from research_assistant.writing_tool.models import CloudDocument, DocumentVersion
    doc = CloudDocument(title="Doc")
    db.session.add(doc)
    db.session.flush()
    version = DocumentVersion(document_id=doc.id, major_version=1, minor_version=0, file_key="mockkey",
                              file_url="https://mock-url", uploaded_by_id=test_user.id, file_size=1.2, is_current=True)
    db.session.add(version)
    db.session.commit()

    res = auth_client.delete(f"/writing_tool/documents/{doc.id}")
    assert res.status_code == 200
    assert res.get_json()["code"] == 0

def test_delete_nonexistent_document(auth_client):
    response = auth_client.delete('/writing_tool/documents/999')
    assert response.status_code == 404
