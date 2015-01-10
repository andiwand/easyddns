from setuptools import setup

setup(
    name="easyddns",
    version="0.0.1",
    url="https://github.com/andiwand/easyddns",
    license="GNU Lesser General Public License",
    author="Andreas Stefl",
    install_requires=["easyname.py"],
    author_email="stefl.andreas@gmail.com",
    description="easyname domain ddns proxy",
    long_description="",
    package_dir={"": "src"},
    packages=["easyddns"],
    platforms="any",
    dependency_links=["https://github.com/andiwand/easyname.py/tarball/master#egg=easyname.py"],
    scripts=["src/easyddns/easyddns.py"],
)
