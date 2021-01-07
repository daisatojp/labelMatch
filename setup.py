from __future__ import print_function
import sys
import re
import distutils.spawn
from setuptools import setup, find_packages


def get_version():
    filename = 'PointMatcher/__init__.py'
    with open(filename) as f:
        match = re.search(r"""^__version__ = ['"]([^'"]*)['"]""", f.read(), re.M)
    if not match:
        raise RuntimeError("{} doesn't contain __version__".format(filename))
    version = match.groups()[0]
    return version


required_packages = find_packages()
required_packages.append('PointMatcher')


required_dependencies = [
    'numpy==1.19.3',
    'opencv-python',
    'pyqt5'
]


def main():
    version = get_version()

    if sys.argv[1] == 'release':
        if not distutils.spawn.find_executable('twine'):
            print('Please install twine', file=sys.stderr)
            sys.exit(1)

        commands = [
            'git tag v{:s}'.format(version),
            'git push origin master --tag',
            'python setup.py sdist',
            'twine upload dist/PointMatcher-{:s}.tar.gz'.format(version),
        ]
        for cmd in commands:
            subprocess.check_call(shlex.split(cmd))
        sys.exit(0)

    setup(
        name='PointMatcher',
        version=version,
        packages=required_packages,
        description='Correspondence Points Annotation Tool',
        author='Dai Sato',
        author_email='dai.sato.jp@gmail.com',
        url="https://github.com/daisatojp/PointMatcher",
        install_requires=required_dependencies,
        license='MIT',
        keywords='Image Annotation, Correspondence Points',
        classifiers=[
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            'License :: OSI Approved :: MIT License',
        ],
        package_data={'PointMatcher': ['icons/*', 'strings/*']},
        entry_points={
            'console_scripts': [
                'PointMatcher=PointMatcher.PointMatcher:main',
            ],
        },
        data_files=[],
    )


if __name__ == '__main__':
    main()
