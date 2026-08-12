import pytest
from app.llm import LLMError, OpenAICompatibleDriver


def test_extract_openai_content():
    data = {"choices": [{"message": {"role": "assistant", "content": '{"ok": true}'}}]}
    assert OpenAICompatibleDriver._extract_content(data) == '{"ok": true}'


def test_extract_openai_content_list():
    data = {"choices": [{"message": {"content": [{"type": "text", "text": '{"ok": true}'}]}}]}
    assert OpenAICompatibleDriver._extract_content(data) == '{"ok": true}'


def test_extract_openai_error_is_descriptive():
    with pytest.raises(LLMError, match="upstream"):
        OpenAICompatibleDriver._extract_content({"error": {"message": "upstream failed"}})


def test_extract_openai_missing_choices_is_descriptive():
    with pytest.raises(LLMError, match="missing 'choices'"):
        OpenAICompatibleDriver._extract_content({"foo": "bar"})
