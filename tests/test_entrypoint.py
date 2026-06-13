import io

import main as entrypoint


class TtyInput(io.StringIO):
    """Small stdin replacement that behaves like an interactive terminal."""

    def isatty(self) -> bool:
        return True


def test_python_main_without_input_starts_api(monkeypatch) -> None:
    calls: list[tuple[str, str, int]] = []

    monkeypatch.setattr(entrypoint.sys, "stdin", TtyInput())
    monkeypatch.setattr(
        entrypoint.uvicorn,
        "run",
        lambda application, host, port: calls.append((application, host, port)),
    )

    exit_code = entrypoint.main([])

    assert exit_code == 0
    assert calls == [("main:app", "0.0.0.0", 8000)]
