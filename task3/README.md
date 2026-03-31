# Listing fixers operating on same files

Lintian-brush applies the fixers on the source of a certain package. 

These fixers are implemented as modules with the function `fn run()` as their entry point. 

Some of these fixers that operate on the same files, like: 

`debian/copyright`<br>
1. unversioned-copyright-format-uri
2. copyright-has-crs
3. copyright-refers-to-symlink-license

`debian/changelog`<br>

1. debian-changelog-has-wrong-day-of-week
2. debian-changelog-line-too-long
3. initial-upload-closes-no-bugs

Similarly other fixers exists that operate on the same set of files