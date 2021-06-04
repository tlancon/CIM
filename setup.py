import setuptools

with open('requirements.txt', 'r') as fc:
    requirements = [line.strip() for line in fc]

setuptools.setup(
    name='CIM',
    version='0.1.0',
    author='Trevor Lancon',
    description='Map images to one another with landmarks and create a script view them in napari.',
    long_description='Align a series of images to a single reference using landmarks,'
                     'then create a napari script to open them in the context of one another. ',
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>3.6',
    install_requires=requirements
)
