"""Exercise the release commands with a local Git origin and a fake GitHub CLI."""

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VERSION = "1.2.3"
TAG = f"v{VERSION}"


def git(path, *args):
    return subprocess.run(
        ["git", "-C", str(path), *args], check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture
def release_repo(tmp_path, monkeypatch):
    repo = tmp_path / "checkout"
    origin = tmp_path / "origin.git"
    repo.mkdir()
    origin.mkdir()
    git(origin, "init", "--bare")
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "API Utils Tests")
    git(repo, "config", "user.email", "release@example.invalid")
    git(repo, "remote", "add", "origin", str(origin))
    scripts = repo / "scripts"
    scripts.mkdir()
    for name in ("tag-release", "publish-package"):
        shutil.copy(ROOT / "scripts" / name, scripts)
    (repo / "pyproject.toml").write_text(f'[project]\nversion = "{VERSION}"\n')
    (repo / ".gitignore").write_text("/dist/\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Release fixture")
    git(repo, "push", "-u", "origin", "main")

    commands = tmp_path / "bin"
    commands.mkdir()
    gh = commands / "gh"
    gh.write_text("""#!/bin/sh
case "$1 $2" in
  "api --paginate") printf '%s\\n' "${RELEASE_TAGS:-}" ;;
  "release view") printf '%s\\n' "${ASSET_COUNT:-0}" ;;
  "release upload")
    printf '%s\\n' "$@" > "$UPLOAD_LOG"
    exit "${UPLOAD_STATUS:-0}" ;;
  *) exit 2 ;;
esac
""")
    pipenv = commands / "pipenv"
    pipenv.write_text(f'#!/bin/sh\nshift 2\nexec "{sys.executable}" "$@"\n')
    for command in (gh, pipenv):
        command.chmod(0o755)
    monkeypatch.setenv("PATH", f"{commands}:{os.environ['PATH']}")
    monkeypatch.setenv("UPLOAD_LOG", str(tmp_path / "uploads"))
    return repo, origin, tmp_path / "uploads"


def helper(repo, name, *args):
    return subprocess.run(
        ["sh", str(repo / "scripts" / name), *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def test_tag_release_requires_clean_remote_main(release_repo):
    repo, _, _ = release_repo
    git(repo, "switch", "-c", "next")
    assert "on main" in helper(repo, "tag-release", "--no-push").stderr
    git(repo, "switch", "main")
    (repo / "untracked").touch()
    assert "clean" in helper(repo, "tag-release", "--no-push").stderr
    (repo / "untracked").unlink()
    git(repo, "commit", "--allow-empty", "-m", "Local only")
    assert "match main on origin" in helper(repo, "tag-release", "--no-push").stderr


def test_tag_release_refuses_release_and_existing_tags(release_repo, monkeypatch):
    repo, origin, _ = release_repo
    monkeypatch.setenv("RELEASE_TAGS", TAG)
    assert "Release" in helper(repo, "tag-release", "--no-push").stderr
    monkeypatch.delenv("RELEASE_TAGS")
    prepared = helper(repo, "tag-release", "--no-push")
    assert prepared.returncode == 0, prepared.stderr
    assert TAG not in git(origin, "tag").splitlines()
    assert "locally" in helper(repo, "tag-release", "--no-push").stderr
    git(repo, "push", "origin", TAG)
    git(repo, "tag", "-d", TAG)
    assert "on origin" in helper(repo, "tag-release", "--no-push").stderr


def test_publish_refuses_wrong_version_or_moved_tag(release_repo):
    repo, origin, uploads = release_repo
    git(repo, "tag", "v1.2.2")
    assert "Missing local tag" in helper(repo, "publish-package").stderr
    git(repo, "tag", TAG)
    git(repo, "push", "origin", TAG)
    git(origin, "tag", "-d", TAG)
    assert "on origin must match HEAD" in helper(repo, "publish-package").stderr
    assert not uploads.exists()


def test_publish_rejects_assets_and_propagates_upload_failure(
    release_repo, monkeypatch
):
    repo, _, uploads = release_repo
    git(repo, "tag", "-a", TAG, "-m", "Annotated release")
    git(repo, "push", "origin", TAG)
    monkeypatch.setenv("ASSET_COUNT", "1")
    assert "already has assets" in helper(repo, "publish-package").stderr
    assert not uploads.exists()
    monkeypatch.setenv("ASSET_COUNT", "0")

    dist = repo / "dist"
    dist.mkdir()
    wheel = dist / f"api_utils-{VERSION}-py3-none-any.whl"
    sdist = dist / f"api_utils-{VERSION}.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")
    monkeypatch.setenv("UPLOAD_STATUS", "23")
    assert helper(repo, "publish-package").returncode == 23
    assert "--clobber" not in uploads.read_text().splitlines()
    for asset in (wheel, sdist):
        assert asset.name in uploads.read_text().splitlines()
        assert (
            f"{hashlib.sha256(asset.read_bytes()).hexdigest()}  {asset.name}"
            in (dist / "SHA256SUMS").read_text()
        )
