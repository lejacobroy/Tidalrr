rm -rf __init__.spec 
rm -rf dist
rm -rf build
rm -rf MANIFEST.in
rm -rf *.egg-info

pip3 uninstall tidalrr
pip3 install -r requirements.txt

cd tidalrr
python3 setup.py sdist bdist_wheel

cd ..
pyinstaller -F tidalrr/tidalrr.py

cd tidalrr
python3 setup.py install

pip uninstall -y tidalrr
