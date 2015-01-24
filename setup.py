from setuptools import setup

setup(
    name="ezddns",
    version="0.0.1",
    url="https://github.com/andiwand/ezddns",
    license="GNU Lesser General Public License",
    author="Andreas Stefl",
    install_requires=["ezname"],
    author_email="stefl.andreas@gmail.com",
    description="easyname domain ddns proxy",
    long_description="",
    package_dir={"": "src"},
    packages=["ezddns"],
    platforms="any",
    dependency_links=["https://github.com/andiwand/ezname/tarball/master#egg=easyname.py"],
    entry_points={'console_scripts':['ezddns = ezddns.cli:main']},
)
