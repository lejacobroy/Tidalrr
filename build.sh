rm -rf __init__.spec 
rm -rf dist
rm -rf build
rm -rf MANIFEST.in
rm -rf *.egg-info

python3 setup.py sdist bdist_wheel
pyinstaller -F tidalrr/__init__.py

pip uninstall -y tidalrr
