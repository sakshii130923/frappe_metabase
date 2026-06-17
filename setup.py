from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="frappe_metabase",
    version="0.1.0",
    description="Metabase dashboard embedding for Frappe",
    author="Frappe Metabase Contributors",
    author_email="hello@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
