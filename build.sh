quip version $1
quip clean --macfilesonly
python setup.py sdist bdist_wheel
pip uninstall uac-cli
pip install --upgrade --find-links=./dist/ --pre uac-cli
a=$PWD
cd ..
python -c "import uac_cli; print(uac_cli.__version__)"
cd $a