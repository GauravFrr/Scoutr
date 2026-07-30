import requests

BASE_URL = "http://localhost:3001"

def test_api():
    print("=== Testing Notes API CRUD + Tag Search ===")
    
    # 1. Create a Note with tags
    print("\n1. Creating Note 1 (Groceries) with tags...")
    note1_data = {
        "title": "Groceries",
        "content": "buy milk, apples, bread",
        "tags": ["shopping", "food"]
    }
    r = requests.post(f"{BASE_URL}/notes", json=note1_data)
    assert r.status_code == 200, f"Create failed: {r.status_code}"
    note1 = r.json()
    print("Created Note 1:", note1)
    assert note1["title"] == "Groceries"
    assert note1["tags"] == ["shopping", "food"]
    note1_id = note1["_id"]

    # 2. Create Note 2 (Work Todo) with tags
    print("\n2. Creating Note 2 (Work Todo) with tags...")
    note2_data = {
        "title": "Work Todo",
        "content": "prepare presentation, review pull request",
        "tags": ["work", "important"]
    }
    r = requests.post(f"{BASE_URL}/notes", json=note2_data)
    assert r.status_code == 200, f"Create failed: {r.status_code}"
    note2 = r.json()
    print("Created Note 2:", note2)
    assert note2["title"] == "Work Todo"
    assert note2["tags"] == ["work", "important"]
    note2_id = note2["_id"]

    # 3. Retrieve all Notes
    print("\n3. Retrieving all notes...")
    r = requests.get(f"{BASE_URL}/notes")
    assert r.status_code == 200, f"Retrieve all failed: {r.status_code}"
    notes = r.json()
    print(f"Total notes retrieved: {len(notes)}")
    assert len(notes) >= 2

    # 4. Retrieve single Note 1
    print("\n4. Retrieving single Note 1...")
    r = requests.get(f"{BASE_URL}/notes/{note1_id}")
    assert r.status_code == 200, f"Retrieve single failed: {r.status_code}"
    print("Retrieved Note 1:", r.json())
    assert r.json()["title"] == "Groceries"

    # 5. Update Note 1
    print("\n5. Updating Note 1 tags and content...")
    update_data = {
        "title": "Groceries List",
        "content": "buy milk, apples, bread, bananas",
        "tags": ["shopping", "food", "fruits"]
    }
    r = requests.put(f"{BASE_URL}/notes/{note1_id}", json=update_data)
    assert r.status_code == 200, f"Update failed: {r.status_code}"
    updated_note = r.json()
    print("Updated Note 1:", updated_note)
    assert updated_note["title"] == "Groceries List"
    assert updated_note["tags"] == ["shopping", "food", "fruits"]

    # 6. Search notes by tag (tags)
    print("\n6. Searching notes by tag 'fruits'...")
    r = requests.get(f"{BASE_URL}/notes/tag/fruits")
    assert r.status_code == 200, f"Tag search failed: {r.status_code}"
    tag_results = r.json()
    print("Tag Search Results:", tag_results)
    found = any(note["_id"] == note1_id for note in tag_results)
    assert found, "Created Note 1 not found in tag search results"

    # 7. Delete both notes
    print("\n7. Deleting Note 1 and Note 2...")
    r = requests.delete(f"{BASE_URL}/notes/{note1_id}")
    assert r.status_code == 200, f"Delete Note 1 failed: {r.status_code}"
    r = requests.delete(f"{BASE_URL}/notes/{note2_id}")
    assert r.status_code == 200, f"Delete Note 2 failed: {r.status_code}"
    print("Both notes deleted successfully.")

    # 8. Verify deletion
    print("\n8. Verifying deletion...")
    r = requests.get(f"{BASE_URL}/notes/{note1_id}")
    assert r.status_code == 404, f"Expected 404 but got: {r.status_code}"
    print("Confirmed Note 1 is gone.")

    print("\n=== ALL TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_api()
