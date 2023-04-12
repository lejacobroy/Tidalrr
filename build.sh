rm -rf dist
rm -rf build 
rm -rf __init__.spec

cd build
rm -rf __init__.spec 
rm -rf dist
rm -rf build 
rm -rf exe
rm -rf MANIFEST.in
rm -rf *.egg-info

python setup.py sdist bdist_wheel
pyinstaller -F build/__init__.py

pip uninstall -y tidalrr

cd ..