from setuptools import setup, find_packages


setup(name='scalable-gpt-developer',
      version='0.1.0',
      description='Use LLMs to write multifile applications, scalably',
      author='Hugh Perkins',
      author_email='hughperkins@gmail.com',
      python_requires='>=3.10, <4',
      url='https://github.com/hughperkins/scalable-gpt-developer',
      packages=find_packages(),
)
