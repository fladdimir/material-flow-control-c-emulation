# conveyor system emulation for C-based control code testing

## requirements

pip install -r requirements.txt

## generate cffi wrapper for C module control code

python module_control/emulation/cffi/prepare_cffi.py

## run simple animation draft for test scenario

python simulator/frontend/arcade_test.py

## run tests

pytest tests
