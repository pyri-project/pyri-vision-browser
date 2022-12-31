from setuptools import setup, find_packages, find_namespace_packages

setup(
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    include_package_data=True,
    package_data = {
        'pyri.vision_browser.panels': ['*.html'],
        'pyri.vision_browser.components': ['*.html'],
        'pyri.vision_browser.dialogs': ['*.html']
    },
    zip_safe=False
)