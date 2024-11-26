# rainbow-sparkles

## touch screen
sudo apt install python3-venv
python -m venv env --system-site-packages
source env/bin/activate

cd ~
sudo apt-get update
sudo apt-get install -y git python3-pip
pip3 install --upgrade adafruit-python-shell click
git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
cd Raspberry-Pi-Installer-Scripts

sudo -E env PATH=$PATH python3 adafruit-pitft.py
# screen is 3.5in resistive
# rotation should be 90


## raspberrypi
pip install matplotlib
# not sure why but I had to do this to make tk figures work
sudo pip3 install pillow --upgrade

pip install RPi.GPIO
sudo dtparam spi=on

export DISPLAY=:0.0


# MAX6675 - thermocouple

# https://github.com/tdack/MAX6675/tree/master

sudo apt-get update
sudo apt-get install build-essential python-dev-is-python3 python3-smbus

python3 setup.py install


## ssh
isaacparsons@10.0.0.141
password: password