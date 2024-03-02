from setuptools import find_packages, setup

setup(
    name="godrick",
    version='0.0.1',
    packages=find_packages(where='python'),
    package_dir={'' : 'python'},
    #package_data={"hydra" : ["hydra_units.txt"]},
    #install_requires=['ase', 'pint >= 0.17 '],
    #scripts=['bin/nativeToLammpsInputs', 'bin/nd2ToNativeWorkflow'],
    license = 'Copyright © 2024 by Matthieu Dreher. All rights reserved',
    python_requires='>=3.6',
    author='Matthieu Dreher',
    author_email='dreher.matthieu@gmail.com',
    maintainer='Matthieu Dreher',
    maintainer_email='dreher.matthieu@gmail.com',
    description='Godrick Project'
    #url='https://canadianbanknote2.sharepoint.com/:fl:/r/contentstorage/CSP_93ea96cc-cba0-4afe-b2fc-c832493f52fd/Document%20Library/LoopAppData/Hydra%20Home%20Page.loop?d=w57566401a5d145d9aa4163b41872cbbd&csf=1&web=1&e=NNbJyT&nav=cz0lMkZjb250ZW50c3RvcmFnZSUyRkNTUF85M2VhOTZjYy1jYmEwLTRhZmUtYjJmYy1jODMyNDkzZjUyZmQmZD1iJTIxekpicWs2RExfa3F5X01neVNUOVNfYWpLSldZaTdkdEh1Ul9rRWdmM0E4WEJ2SDZuQV8waVNid3FncDlzY0tDdyZmPTAxT1RRNTc0SUJNUkxGUFVORjNGQzJVUUxEV1FNSEZTNTUmYz0lMkYmYT1Mb29wQXBwJnA9JTQwZmx1aWR4JTJGbG9vcC1wYWdlLWNvbnRhaW5lciZ4PSU3QiUyMnclMjIlM0ElMjJUMFJUVUh4allXNWhaR2xoYm1KaGJtdHViM1JsTWk1emFHRnlaWEJ2YVc1MExtTnZiWHhpSVhwS1luRnJOa1JNWDJ0eGVWOU5aM2xUVkRsVFgyRnFTMHBYV1drM1pIUklkVkpmYTBWblpqTkJPRmhDZGtnMmJrRmZNR2xUWW5keFozQTVjMk5MUTNkOE1ERlBWRkUxTnpSTFRqZFpWelJOTnpZME5rcEVTekpRUWtSWFdVeFROVXhZVlElM0QlM0QlMjIlMkMlMjJpJTIyJTNBJTIyMmNlMWIwMzUtY2M1Yy00Y2VkLWE3NTktN2EyNGRiMDM0MjlkJTIyJTdE',
)