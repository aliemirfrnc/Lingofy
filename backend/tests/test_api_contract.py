import pytest
from fastapi.testclient import TestClient
from backend.main import app
import json
from unittest.mock import AsyncMock

client = TestClient(app)

def validate_schema(response_json, expected_schema):
    """
    Strict validation of JSON schema.
    expected_schema should be a dict where keys are field names and values are types.
    """
    for key, expected_type in expected_schema.items():
        assert key in response_json, f"Missing key: {key}"
        
        value = response_json[key]
        if expected_type is None:
            continue # allow anything
            
        if expected_type == "nullable_string":
            assert value is None or isinstance(value, str), f"Field {key} should be str or null, got {type(value)}"
        elif expected_type == "list_of_strings":
            assert isinstance(value, list), f"Field {key} should be list, got {type(value)}"
            assert all(isinstance(i, str) for i in value), f"Field {key} should contain only strings"
        else:
            assert isinstance(value, expected_type), f"Field {key} should be {expected_type}, got {type(value)}"
            
    # Check for extra fields
    for key in response_json.keys():
        assert key in expected_schema, f"Unexpected extra key: {key}"

@pytest.mark.asyncio
async def test_word_info_contract(mocker):
    # Mock auth dependency across decorators and handlers
    mocker.patch("backend.routes.word_info.require_user_id", return_value=1)
    mocker.patch("backend.dependencies.subscription.require_user_id", return_value=1)
    mocker.patch("backend.dependencies.subscription.SubscriptionService.consume_feature_atomic", return_value=(True, ""))
    
    # Needs to bypass dependency injection for current_user by overriding in app
    app.dependency_overrides = {}
    from backend.routes.auth import require_user_id
    app.dependency_overrides[require_user_id] = lambda: 1
    
    mock_dict = mocker.patch("backend.routes.word_info.DictionaryService.get_word_definition")
    mock_dict_instance = AsyncMock()
    mock_dict.return_value = {
        "word": "banana",
        "meanings": ["muz"],
        "part_of_speech": "noun",
        "pronunciation": "bəˈnænə",
        "synonyms": ["plantain"],
        "antonyms": [],
        "syllables": "ba-na-na"
    }
    
    mock_trans = mocker.patch("backend.routes.word_info.TranslationService.get_turkish_translation", new_callable=AsyncMock)
    mock_trans.return_value = "muz"
    
    mock_ai = mocker.patch("backend.routes.word_info.get_ai_service")
    mock_ai_instance = AsyncMock()
    mock_ai.return_value = mock_ai_instance
    mock_ai_instance.get_word_context.return_value = {
        "contextual_meaning": "A yellow fruit.",
        "ai_learning_tip": "Remember it's yellow."
    }
    
    # We must patch get_conn to mock DB times_seen
    conn = mocker.patch("backend.routes.word_info.get_conn")
    cursor = conn.return_value.cursor.return_value
    cursor.fetchone.return_value = (5, 20, 1600000.0, 1500000.0, 1, 0, "Learning", 3)
    
    response = client.post(
        "/api/word-info",
        json={"word": "banana", "context_line": ""},
        headers={"Authorization": "Bearer fake_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    expected_schema = {
        "word": str,
        "turkish_meanings": "list_of_strings",
        "part_of_speech": str,
        "pronunciation": str,
        "definition": str,
        "grammar_note": str,
        "synonyms": "list_of_strings",
        "antonyms": "list_of_strings",
        "examples": "list_of_strings",
        "collocations": "list_of_strings",
        "phrasal_verbs": "list_of_strings",
        "word_family": "list_of_strings",
        "syllables": str,
        "contextual_meaning": str,
        "ai_learning_tip": str,
        "times_seen": int,
        "learning_percentage": int,
        "last_seen": float,
        "first_seen": float,
        "is_favorite": bool,
        "is_memorized": bool,
        "mastery_level": str,
        "review_count": int
    }
    
    validate_schema(data, expected_schema)
    
@pytest.mark.asyncio
async def test_translate_contract(mocker):
    mocker.patch("backend.routes.translate.require_user_id", return_value=1)
    mocker.patch("backend.dependencies.subscription.require_user_id", return_value=1)
    mocker.patch("backend.dependencies.subscription.SubscriptionService.consume_feature_atomic", return_value=(True, ""))
    
    app.dependency_overrides = {}
    from backend.routes.auth import require_user_id
    app.dependency_overrides[require_user_id] = lambda: 1
    
    mock_trans = mocker.patch("backend.core.services.dictionary_service.TranslationService.get_turkish_translation", new_callable=AsyncMock)
    mock_trans.return_value = "elma"
    
    response = client.post(
        "/translate-line",
        json={"text": "apple"},
        headers={"Authorization": "Bearer fake_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    expected_schema = {
        "translation": str
    }
    
    validate_schema(data, expected_schema)
