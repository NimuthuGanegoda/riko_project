from backend.managers.action_manager import ActionManager, ALLOWED_APPS, SAFE_APP_NAME_RE


def test_allowed_app_names_match_the_safe_pattern():
    for name in ALLOWED_APPS:
        assert SAFE_APP_NAME_RE.match(name)


def test_launch_app_rejects_unlisted_app():
    manager = ActionManager()
    result = manager.launch_app("some_totally_unlisted_app")
    assert "not in the allowed app list" in result


def test_launch_app_rejects_shell_metacharacters():
    manager = ActionManager()
    result = manager.launch_app("notepad & rm -rf /")
    assert "invalid app name" in result


def test_launch_app_rejects_non_string_input():
    manager = ActionManager()
    result = manager.launch_app(None)
    assert "invalid app name" in result


def test_parse_and_execute_strips_action_tag_from_text():
    manager = ActionManager()
    clean_text, result = manager.parse_and_execute(
        'Sure senpai! [ACTION: {"action": "get_time", "param": ""}]'
    )
    assert "[ACTION" not in clean_text
    assert result is not None


def test_parse_and_execute_reports_unknown_action():
    manager = ActionManager()
    _, result = manager.parse_and_execute(
        '[ACTION: {"action": "delete_everything", "param": ""}]'
    )
    assert result == "Unknown action: delete_everything"
