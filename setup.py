from setuptools import setup

setup(
    name="pygame-chess",
    version="1.0",
    packages=["src"],
    package_data={"assets": ["pieces/*.png"]},
    install_requires=["pygame>=2.5.2"],
)
