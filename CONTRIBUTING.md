# Contributing to advarchs

The following is a set of guidelines to contribute to Advarchs and its libraries, which are
hosted on the [elessarelfstone](https://github.com/elessarelfstone) on GitHub.

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change.

This project adheres to the [Contributor Covenant 1.2](http://contributor-covenant.org/version/1/2/0).
By participating, you are advised to adhere to this Code of Conduct in all your interactions with
this project

## Reporting issues

Reporting issues is a great way to contribute to our project.

Before raising a new issue, check [the issues list](https://github.com/elessarelfstone/advarchs/issues).
A solution to your issue might already be in the works!

If stuble upon a bug - big or small - report it. But, remember, a good bug report shouldn't leave
others needing to chase you for more information. Please be as detailed as possible. The following
questions might serve as a template for writing a detailed report:

- What were you trying to achieve?
- What are the expected results?
- What are the received results?
- What are the steps to reproduce the issue?
- In what environment did you encounter the issue?

You may also ask simple questions relating to the project or find some documentation missing.
We would like to know about it too, so don't hesitate!

At the same time, please keep your issues constrained to a single problem. If the problem is systemic,
you may report it as well, we'll take it one step at time from then on.

## Pull requests

Good pull requests (e.g. patches, improvements, new features, docs) are of great help. But, again, they
should remain focused on the scope of a single problem and **avoid unrelated commits**.

**Please ask first** (say, via issue) before embarking on any large pull request (e.g. implementing new features,
refactoring code etc.). You risk wasting your own effort on work that won't be accepted by us.

Please adhere to the [PEP-8](https://www.python.org/dev/peps/pep-0008/) coding conventions as used by this project.

To contribute to the project, [fork](https://help.github.com/articles/fork-a-repo/) it,
clone your fork repository, and configure the remotes:

```shell
git clone https://github.com/<your-username>/advarchs.git
cd advarchs
git remote add upstream https://github.com/elessarelfstone/advarchs.git
```

If your cloned repository is behind the upstream commits, then get the latest changes from upstream:

```shell
git checkout master
git pull --rebase upstream master
```

Create a new topic branch from `master` using the naming convention `ARCH-[issue-number]`
to help us keep track of your contribution scope:

```
git checkout -b ARCH-[issue-number]
```

Commit your changes in logical chunks. When you are ready to commit, make sure
to write a Good Commit Message™. Consult the [Erlang's contributing guide](https://github.com/erlang/otp/wiki/Writing-good-commit-messages)
if you're unsure of what constitutes a Good Commit Message™. Use [interactive rebase](https://help.github.com/articles/about-git-rebase)
to group your commits into logical units of work before making it public.

Note that every commit you make must be signed. By signing off your work you indicate that you
are accepting the [Developer Certificate of Origin](https://developercertificate.org/).

Use your real name (sorry, no pseudonyms or anonymous contributions). If you set your `user.name`
and `user.email` git configs, you can sign your commit automatically with `git commit -s`.

Locally merge (or rebase) the upstream development branch into your topic branch:

```
git pull --rebase upstream master
```

Push your topic branch up to your fork:

```
git push origin ARCH-[issue-number]
```

[Open a Pull Request](https://help.github.com/articles/using-pull-requests/) with a clear title
and detailed description.
