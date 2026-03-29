# Profiling lintian-brush on an existing package
---

For this task, I'm using `python3-dulwich` package for profiling with *lintian-brush*. 

## Steps taken:
1. Built *lintian-brush* from the source
    `cargo build --release`
2. Downloaded the deb package for `python3-dulwich`
3. Ran *lintian* on the `.deb` package to check out any existing issues. 
     