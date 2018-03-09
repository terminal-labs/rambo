# Releasing Rambo

This documents how to release Rambo. Various steps in this document may
require privileged access to private systems, so this document is only
targetted at Rambo core members who have the ability to cut a release.

1. Update `__version__` in `rambo/__init__.py` to the version you want to release.

1. Update [CHANGELOG.md](https://github.com/terminal-labs/rambo/blob/master/CHANGELOG.md) to have a header with the release version and date.

1. Commit those changes and also tag the release with the version:

        $ git tag X.Y.Z
        $ git push --tags

1. Release this version on [GitHub](https://github.com/terminal-labs/rambo/releases).

1. Update `version.txt` to the next version and append `.dev` and add
  [a new blank](https://github.com/terminal-labs/rambo/blob/c955146f3b8e88bb24dddc3755b3b8751a970b1a/CHANGELOG.md) entry in the CHANGELOG, commit, and push.
