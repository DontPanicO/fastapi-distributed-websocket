import os.path
import re

from setuptools import setup, find_packages


def read(*parts):
    with open(os.path.join(*parts)) as f:
        return f.read().strip()


def read_version():
    regexp = re.compile(r'^__version__\W*=\W*\'([\d.abrc]+)\'')
    init_py = os.path.join(
        os.path.dirname(__file__), 'distributed_websocket', '__init__.py'
    )
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        raise RuntimeError(f'Cannot find version in {init_py}')


classifiers = [
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3 :: Only',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
    'Framework :: AsyncIO',
    'Framework :: FastAPI',
]


setup(
    name='fastapi-distributed-websocket',
    version=read_version(),
    author='Andrea Tedeschi',
    author_email='andrea.tedeschi@andreatedeschi.uno',
    description='Large scale WebSocket with FastAPI',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=classifiers,
    platforms=['POSIX'],
    url='https://github.com/DontPanicO/fastapi-distributed-websocket',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'redis>=4.3.1',
        'fastapi>=0.75.2',
        'websockets>=10.3',
    ],
    package_data={'distributed_websocket': ['py.typed']},
    python_requires='>=3.10',
    include_package_data=True,
)
