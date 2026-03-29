# Profiling lintian-brush on an existing package
---

For this task, I'm using `python3-dulwich` package for profiling with *lintian-brush*. 

## Steps taken:
1. Built *lintian-brush* from the source
    `cargo build --release`
2. Downloaded the deb package for `python3-dulwich`
3. Ran *lintian* on the `.deb` package to check out any existing issues. 
    ![alt text](/assets/image.png)
    (mostly warning regarding man pages)
4. Set up a git repository inside the source of `python3-dulwich` as lintian-requires a vcs setup inside the folder and added all the files as a single commit. 
5. Ran *lintian-brush* after the commit 
    ![alt text](/assets/image2.png)
6. Ran with *strace* to figure how many file related syscalls were made.<br>
    `strace -e trace=file lintian-brush (out.log)`<br>
7. Wrote a [jupyter notebook](/assets/strace_log.ipynb) using **pandas** to visualize the strace logs. The notebook only tracks the syscalls made within the folder where lintian-brush was called.
