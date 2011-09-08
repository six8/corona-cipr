from setuptools import setup, find_packages

def main():
    setup(
        name = 'cipr',
        packages=['cipr'],
        package_dir = {'':'src'},
        version = '0.7',
        author='Mike Thornton',
        author_email='six8@devdetails.com',
        download_url='http://github.com/six8/corona-cipr',
        keywords=['corona'],
        license='MIT',
        description='A package manager for the Corona SDK',
        classifiers = [
            "Programming Language :: Python",
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Operating System :: POSIX",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
        ],
        install_requires = [
            'Fabric',
        ],
        long_description=open('README.rst').read(),
        entry_points = {
            'console_scripts': [
                'cipr = cipr.commands.main:main',
            ],
        },
    )

if __name__ == '__main__':
    main()