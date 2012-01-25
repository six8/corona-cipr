from distutils.core import setup


def main():
    setup(
        name = 'cipr',
        packages=['cipr', 'cipr.commands'],
        package_dir = {'':'src'},
        package_data={'cipr': [
            'code/*', 
            'skel/default/*'
        ]},
        zip_safe = False,
        version = open('VERSION.txt').read().strip(),
        author='Mike Thornton',
        author_email='six8@devdetails.com',
        url='http://github.com/six8/corona-cipr',
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
            'clik',
            'clom'
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