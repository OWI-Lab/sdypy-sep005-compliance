import os
import re
from setuptools import setup

base_path = os.path.dirname(__file__)

# Read the project version from "__init__.py"
regexp = re.compile(r'.*__version__ = [\'\"](.*?)[\'\"]', re.S)

init_file = os.path.join(base_path, 'sdypy_sep005', '__init__.py')
with open(init_file, 'r') as f:
    module_content = f.read()

    match = regexp.match(module_content)
    if match:
        version = match.group(1)
    else:
        raise RuntimeError(
            'Cannot find __version__ in {}'.format(init_file))

# Read the "README.rst" for project description
with open('README.rst', 'r') as f:
    readme = f.read()


if __name__ == '__main__':
    setup(
        name='sdypy_sep005',
        description='Checks compatibility with the SDyPy SEP005 guidelines using Pydantic validation',
        long_description=readme,
        license='MIT license',
        url='https://github.com/sdypy',
        version=version,
        author='Wout Weijtjens',
        author_email='wout.weijtjens@vub.be',
        maintainer='Wout Weijtjens',
        maintainer_email='wout.weijtjens@vub.be',
        keywords=['io', 'tdms', 'SEP5', 'validation', 'pydantic'],
        packages=['sdypy_sep005'],
        install_requires=[
            'numpy>=1.11.0',
            'pydantic>=2.0.0',
        ],
        extras_require={
            'dev': [
                'pytest',
                'hypothesis',
                'sphinx',
                'sphinx-rtd-theme',
                'twine',
                'wheel',
            ],
        },
        python_requires='>=3.7',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing',
        ]
    )
