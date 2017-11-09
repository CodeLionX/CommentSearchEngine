#!/bin/sh

# please run this script from project root

# install dependecies
pip3 install --upgrade setuptools

pip3 install nltk
python3 - <<NLTKDOWNLOAD
    import nltk
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download('wordnet')
NLTKDOWNLOAD

pip3 install --upgrade -r requirements.txt

# build project
python3 setup.py build
