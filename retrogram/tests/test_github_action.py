import json

from retrogram import github_action


def test_public_image_url_uses_github_revision(monkeypatch):
    monkeypatch.delenv("PUBLIC_IMAGE_BASE_URL", raising=False)
    monkeypatch.setenv("GITHUB_REPOSITORY", "djkalew/tom-jerry-swag")
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    assert github_action.public_image_url("01.jpg") == (
        "https://raw.githubusercontent.com/djkalew/tom-jerry-swag/abc123/assets/queue/01.jpg"
    )


def test_state_round_trip(tmp_path, monkeypatch):
    state_path = tmp_path / "state.json"
    monkeypatch.setattr(github_action, "STATE", state_path)
    expected = {"next_index": 2, "published": [{"file": "one.jpg"}]}
    github_action.save_state(expected)
    assert github_action.load_state() == expected
    assert json.loads(state_path.read_text(encoding="utf-8")) == expected
