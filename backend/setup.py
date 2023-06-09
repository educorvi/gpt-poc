from setuptools import setup

requirements = [
    "websockets~=11.0.3",
    "PyYAML~=6.0",
    "langchain~=0.0.188",
    "elasticsearch~=8.8.0",
    "openai~=0.27.7",
    "aiohttp==3.8.4"
]

setup(
    name="gpt-poc-backend",
    version="0.0.3",
    author="Julian Pollinger",
    author_email="julian.pollinger@educorvi.de",
    description="A proof of concept for chatgpt integrated with elasticsearch",
    license="MIT",
    py_modules=["backend", "customElasticSearchRetriever", "tools"],
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    scripts=["gpt-poc-backend"],
    data_files=[("/etc/gpt-poc", ["conf.template.yaml"])],
    install_requires=requirements
    )
