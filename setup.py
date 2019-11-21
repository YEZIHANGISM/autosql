import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='autosql',
    version="1.0.0",
    author='yezihangism',
    author_email='yezihangism@gmail.com',
    py_modules=['autosql.autosql'],
    url='https://github.com/YEZIHANGISM/autosql',
    long_description = long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages()
)