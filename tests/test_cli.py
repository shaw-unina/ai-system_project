"""CLI smoke tests. Use the mock backend to stay offline."""
from __future__ import annotations

import json

from misinfo import cli, config


def test_cli_info_runs(monkeypatch, capsys):
    monkeypatch.setenv("MISINFO_BACKEND", "mock")
    monkeypatch.setenv("MISINFO_CACHE", "false")
    config.get_settings.cache_clear()
    rc = cli.main(["info"])
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["backend"] == "mock"
    assert payload["model_id"] == "mock"
    config.get_settings.cache_clear()


def test_cli_parser_builds():
    p = cli.build_parser()
    args = p.parse_args(["verify", "hello"])
    assert args.cmd == "verify"
    assert args.claim == "hello"
