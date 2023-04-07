import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vprimer",
    version="1.0.2",
    author="satoshi-natsume",
    author_email="s-natsume@ibrc.or.jp",
    description="V-primer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ncod3/vprimer",
    packages=setuptools.find_packages(),
    license='MIT',
    entry_points = {
        'console_scripts': ['vprimer = vprimer.main:main']
    },
    python_requires='>=3.7',
)
