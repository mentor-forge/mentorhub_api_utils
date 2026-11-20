# GitHub Release distribution

## Delivery audit

The inspected feature branch declares version 1.0.4, and the checkout contains tag `v1.0.4`. Choose the next patch version after checking local and remote tags and releases. The build uses setuptools, discovers `api_utils*` packages, and packages the README and project metadata. The package includes configuration, Flask authentication and route helpers, MongoDB helpers, and shared services. Preserve the `api_utils` import and the normalized `api-utils` distribution identity and public exports.

Both Stage Zero build entry points currently use Pipenv to build a wheel and source archive. The tag helper pushes the version tag, and the tagged workflow assumes an AWS role and uses Twine to send both artifacts to CodeArtifact. The operator publish helper also uses the AWS CLI and Twine. The development Pipfile and lock already declare public PyPI as their only index.

The package code has no boto3, botocore, Cognito client, or CodeArtifact integration. Its runtime integrations include configured MongoDB access, Flask, Prometheus metrics, and JWT processing. The token module imports `jwt`, and the development Pipfile supplies PyJWT, but the project metadata does not list it. Add PyJWT to the wheel's runtime dependencies before publication and verify the top-level import from a clean install outside the source checkout.

## Release artifacts and consumer installation

Publish the tested `api_utils-X.Y.Z-py3-none-any.whl` and `api_utils-X.Y.Z.tar.gz` with a SHA-256 checksum file on the public Mentor Hub API Utils GitHub Release tagged `vX.Y.Z`. Check that the tag, project metadata, and built artifact versions agree. Use Python 3.12 for build and consumer verification. Public release downloads require no credential. Keep certificates verified and resolve third-party dependencies from public PyPI.

Example Pipfile for a consumer. Replace `X.Y.Z` with the published version.

```toml
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[packages]
api-utils = {file = "https://github.com/mentor-forge/mentorhub_api_utils/releases/download/vX.Y.Z/api_utils-X.Y.Z-py3-none-any.whl"}

[requires]
python_version = "3.12"
```

Compare the wheel's SHA-256 against the published checksum, generate the lock with `pipenv lock`, and verify the exact URL and wheel digest in `Pipfile.lock`. Commit the Pipfile and lockfile together. Use `pipenv sync` in a clean environment and verify the installed distribution version, import location, and expected configuration, authentication, and service exports. Always use the direct wheel URL for Mentor Hub API Utils. The public PyPI project with the same normalized distribution name is unrelated.

## Release order and rollback

1. Merge and validate the publisher changes on main. A maintainer verifies an unused version, then tags the intended main commit and uses the release workflow to publish the tested artifacts and checksums. Existing tags and release assets are immutable.
2. Validate the published release in a clean external consumer before updating dependent APIs. Record the tag commit, artifact URL, package version, and wheel hash. Keep those consumers on their existing versions until this check passes.
3. Update each consumer's exact URL and lockfile, then verify clean installs, tests, and container builds. Roll back a regression by restoring an earlier verified GitHub-hosted wheel URL and its matching lockfile. The first GitHub-hosted release is the rollback floor.
