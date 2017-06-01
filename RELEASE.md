# Releasing Rambo

This documents how to release Rambo. Various steps in this document may
require privileged access to private systems, so this document is only
targetted at Rambo core members who have the ability to cut a release.

1. Update `version.txt` to the version you want to release.

1. Update [CHANGELOG.md](https://bitbucket.org/terminal_labs/rambo/src/master/CHANGELOG.md) to have a header with the release version and date.

1. Commit those changes and also tag the release with the version:

        $ git tag vX.Y.Z
        $ git push --tags

1. Update `version.txt` to the next version and append `.dev` and add
  a new blank entry in the CHANGELOG, commit, and push.
