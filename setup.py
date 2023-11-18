from setuptools import setup, find_packages

setup(
    name='gpt_dir',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'openai==1.3.2',
        'tiktoken==0.5.1'
    ],
    scripts=['gpt_dir.py'],
    entry_points={
        'console_scripts': [
            'gpt-dir = gpt_dir:main',
        ],
    },
)