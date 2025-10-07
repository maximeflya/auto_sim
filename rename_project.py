import subprocess
from pathlib import Path

project_title = input("Project title: ")
package_name = input("Python package name: ")
github_link = input("GitHub link (eg. python-template-repository): ")
sonar_cloud_link = input("SonarCloud link (eg. Flyability_python-template-repository): ")

for path in [
    Path(p)
    for p in subprocess.run(["git", "ls-files"], stdout=subprocess.PIPE)
    .stdout.decode()
    .splitlines()
]:
    try:
        with path.open() as file:
            s = file.read()
        s = s.replace(
            "Flyability/python-template-repository", f"Flyability/{github_link}"
        )
        s = s.replace("python_template_repository", package_name)
        s = s.replace("Python Template Repository", project_title)
        s = s.replace(
            "Flyability_python-template-repository",
            sonar_cloud_link,
        )
        with path.open("w") as file:
            file.write(s)
    except UnicodeDecodeError:
        pass

template_package_path = Path(__file__).parent / "src" / "python_template_repository"
template_package_path.rename(template_package_path.with_name(package_name))

# Change package folder name
if Path(__file__).parent.name != package_name:
    template_repo_path = Path(__file__).parent
    template_repo_path.rename(template_repo_path.with_name(package_name))
