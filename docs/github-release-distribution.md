# GitHub Release distribution

## Delivery audit

The delivery audit started at version 1.0.4. Version 1.0.5 is prepared for review as the first GitHub-hosted version. The build uses setuptools, discovers `api_utils*` packages, and packages the README and project metadata. The package includes configuration, Flask authentication and route helpers, MongoDB helpers, and shared services. Preserve the `api_utils` import and the normalized `api-utils` distribution identity and public exports.

Before the migration, both Stage Zero build entry points used Pipenv to build a wheel and source archive. The tag helper pushed the version tag, and the former tagged workflow and operator helper uploaded both artifacts to CodeArtifact. The development Pipfile and lock already declare public PyPI as their only index.

The package code has no boto3, botocore, Cognito client, or CodeArtifact integration. Its runtime integrations include configured MongoDB access, Flask, Prometheus metrics, and JWT processing. The token module imports `jwt`. The wheel now declares PyJWT as a runtime dependency along with Flask, PyMongo, and the Prometheus Flask exporter.

## Release artifacts and consumer installation

Publish the tested `api_utils-X.Y.Z-py3-none-any.whl` and `api_utils-X.Y.Z.tar.gz` with a SHA-256 checksum file on the public Mentor Hub API Utils GitHub Release tagged `vX.Y.Z`. Check that the tag, project metadata, and built artifact versions agree. Use Python 3.12 for build and consumer verification. Public release downloads require no credential. Keep certificates verified and resolve third-party dependencies from public PyPI.

Example Pipfile for a consumer. Replace `X.Y.Z` with the published version.

```toml
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[packages]
api-utils = {file = "https://github.com/mentor-forge/mentorhub_api_utils/releases/download/v1.0.5/api_utils-1.0.5-py3-none-any.whl"}

[requires]
python_version = "3.12"
```

Compare the wheel's SHA-256 against the published checksum, generate the lock with `pipenv lock`, and verify the exact URL and wheel digest in `Pipfile.lock`. Commit the Pipfile and lockfile together. Use `pipenv sync` in a clean environment and verify the installed distribution version, import location, and expected configuration, authentication, and service exports. Always use the direct wheel URL for Mentor Hub API Utils. The public PyPI project with the same normalized distribution name is unrelated.

## Release order and rollback

1. Merge and validate the publisher changes on main. A maintainer verifies an unused version, then tags the intended main commit and uses the release workflow to publish the tested artifacts and checksums. Existing tags and release assets are immutable.
2. Validate the published release in a clean external consumer before updating dependent APIs. Record the tag commit, artifact URL, package version, and wheel hash. Keep those consumers on their existing versions until this check passes.
3. Update each consumer's exact URL and lockfile, then verify clean installs, tests, and container builds. Roll back a regression by restoring an earlier verified GitHub-hosted wheel URL and its matching lockfile. The first GitHub-hosted release is the rollback floor.

## CI and publication

Pull requests use read-only CI to sync the public lock, run unit tests and lint, and inspect the built wheel and source archive. The tag workflow uses the same checks and transfers the resulting distributions and checksums to a separate publication job. That job checks the tag against package metadata, verifies that the commit belongs to main and that the repository is public, then creates the release using the tested assets. Existing releases remain immutable. The first real publication and clean consumer download are maintainer and acceptance gates.

## Consumer acceptance checklist

Create a temporary project outside the API Utils checkout using the example
Pipfile above. After publication, download the wheel and checksum file from the
release without credentials and verify the wheel checksum before installing.
Run these checks in the temporary project:

```sh
pipenv lock
pipenv sync
pipenv run python -m pip check
pipenv run python -c 'from importlib.metadata import version; import api_utils; from api_utils import Config, Token, create_flask_token, MongoIO, JourneyService, NoteService; print(version("api-utils"), api_utils.__file__)'
```

Confirm the lockfile contains the exact GitHub asset URL and the published
wheel hash, and lists public PyPI as its package index. Confirm the printed
version matches the tag and the import resolves inside the temporary virtual
environment. Run the artifact inspection from the API Utils checkout with
`API_UTILS_WHEEL` set to the downloaded wheel path and
`pipenv run pytest tests/release/test_wheel_contents.py`. Record the actual
release URL, tag commit, version, checksum, and clean-install results before
handing off to consumers.

Before publication, the same Pipenv lock and sync checks passed with the
locally built 1.0.5 wheel supplied as a local file URL. The lock contained the
matching wheel SHA-256, public PyPI remained the sole package index, and the
isolated install passed dependency, version, import path, and public export
checks. This evidence covers the local artifact. Published asset verification
remains pending maintainer publication.
