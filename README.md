# Python Project Template Repository

> A template for creating new python projects repositories in the [@Flyability](https://github.com/Flyability) organization

This repository is meant to serve as a general template for how to set up new python projects repositories in the [@Flyability](https://github.com/Flyability) organization. In general, setting up a new repository should take only a few minutes; use this repository as a way of finding example files, and use the following checklist to ensure that you've set up the repository correctly.

## Use Template

> [!CAUTION]
> This is meant to be used from **[Use this template](https://github.com/Flyability/python-template-repository)** feature.

Once the repository is created, you can clone it on our workstation and complete the checklist.

### Using Template Locally

If you want to use the template without creating a github repository first:

```bash
git clone https://github.com/Flyability/your_python_template_repository
cd your_python_template_repository/
rm -rf .git
git add --all
git commit -m "Initial commit"
```

## Checklist

Go through this checklist after creating your repository. It should only take a couple of minutes; if there is a way to make this more efficient, open an issue and let's talk about it here! \m/

### Main Files

- [ ] Rename all instances of `python_template_repository` in all files to match the new repo title by running the following commands:
- [ ] Rename the template README: `mv README.md setup_checklist.md` Once you complete the checklist, you can remove this file
- [ ] Use the example README as repository README: `mv example-README.md README.md`

```bash
python3 rename_project.py
```

- [ ] Delete `rename_project.py`
- [ ] Manually go through and edit the rest of the README.
- [ ] Make sure `pyproject.toml` is correct, did you change the name and the dependencies?
- [ ] Make sure an appropriate package author has been set
- [ ] Remove the `dummy` packages and replace it by your files.

### Dotfiles

- [ ] Do you need a `.gitignore` file?

### Documentation

- [ ] Did you add your project on [readthedocs.com](https://readthedocs.com/dashboard)? To do so, contact an admin of [@Flyability](https://github.com/Flyability) organization.
- [ ] Did you write a proper documentation for your project?
- [ ] Did you write a proper README.md file?

### GitHub Metadata

- [ ] Have you added a short description to the repository?
  - [ ] Is the description matched in the byline under the title in the README?
- [ ] Have you added topics to the GitHub repository: `stability`, `python`, and so on?
- [ ] Is `master` the default branch? Did you protect it?
  - [ ] The following must be ticked:
    - [ ] Require a pull request before merging,
    - [ ] Require approvals (1),
    - [ ] Require review from Code Owners,
    - [ ] Allow specified actors to bypass required pull requests (flyabot),
    - [ ] Require status checks to pass before merging,
    - [ ] Require branches to be up to date before merging,
    - [ ] Require conversation resolution before merging
- [ ] Did you change the repository merging setting to "Allow only merge squash"?

### Github Actions Workflows

- [ ] Did you create the [SonarQubecloud](https://sonarcloud.io/) project related to your repository?
  - [ ] Did you double-checked that the sonar configuration is correct (name and project key) ?
- [ ] Choose the image that you need to run github actions (`ubuntu-24.04` by default).
- [ ] Consider if you want to cache the python dependencies. The advantage is that for a
    large amount of dependencies, the workflow will be faster. The disadvantage is
    the added complexity if something breaks.

## Contribute

If you think this could be better, please open a pull request!
