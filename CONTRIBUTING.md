# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Github is used for everything

Github is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've changed something, update the documentation.
3. If your change is user-facing, add an entry to `CHANGELOG.md`.
4. Make sure your code lints (using `ruff check .`).
5. Run the test suite (see below).
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [ruff](https://docs.astral.sh/ruff/) to check and format the code.

## Test your code modification

Install the test and lint dependencies:

```bash
pip install -r requirements_test.txt
```

Run the test suite from the repository root:

```bash
pytest
```

Check the code style with:

```bash
ruff check .
```

## Releasing

1. Update `version` in `custom_components/creality_3dprinter/manifest.json`.
2. Add the release notes to `CHANGELOG.md`.
3. Commit and push the changes.
4. Create a tag named `vX.Y.Z` for that commit.
5. Create a GitHub release from the tag and use the changelog entry as its description. HACS discovers updates from the release.

The tag and the manifest version must match, for example `v0.1.0` and `0.1.0`.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
