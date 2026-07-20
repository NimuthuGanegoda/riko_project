import base64
import sys
import types

import pytest


def _install_fake_pyautogui(image_bytes_holder):
    from PIL import Image

    fake_module = types.ModuleType("pyautogui")

    def screenshot():
        img = Image.new("RGB", (10, 10), color=(255, 0, 0))
        return img

    fake_module.screenshot = screenshot
    sys.modules["pyautogui"] = fake_module


@pytest.fixture
def vision_manager_module(monkeypatch):
    _install_fake_pyautogui({})
    # Force a fresh import so VisionManager picks up the fake pyautogui module.
    sys.modules.pop("backend.core.vision_manager", None)
    from backend.core import vision_manager
    return vision_manager


def test_capture_screen_returns_base64_string_when_enabled(vision_manager_module):
    manager = vision_manager_module.VisionManager()
    assert manager.enabled is True

    result = manager.capture_screen()
    assert isinstance(result, str)
    # Should be valid base64.
    base64.b64decode(result)


def test_capture_screen_returns_none_when_pyautogui_unavailable(monkeypatch):
    sys.modules.pop("pyautogui", None)
    # Popping just the submodule isn't enough: the parent package object
    # still holds a cached `vision_manager` attribute from a prior import,
    # and `from backend.core import vision_manager` finds that before
    # re-running the import machinery. Drop the parent too.
    sys.modules.pop("backend.core.vision_manager", None)
    sys.modules.pop("backend.core", None)

    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def blocked_import(name, *args, **kwargs):
        if name == "pyautogui":
            raise ImportError("no pyautogui in this environment")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", blocked_import)

    from backend.core import vision_manager
    manager = vision_manager.VisionManager()

    assert manager.enabled is False
    assert manager.capture_screen() is None
