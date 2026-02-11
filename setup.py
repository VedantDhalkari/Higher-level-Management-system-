"""
Setup script for packaging the application
"""
from setuptools import setup, find_packages

setup(
    name="boutique-management-system",
    version="1.0.0",
    author="Your Name",
    description="Boutique Management & Billing System for Women's Ethnic Wear",
    packages=find_packages(),
    install_requires=[
        'customtkinter>=5.2.0',
        'Pillow>=10.0.0',
        'reportlab>=4.0.0',
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'boutique-system=main:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Financial :: Point-Of-Sale',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)