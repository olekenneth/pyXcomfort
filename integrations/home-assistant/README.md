# How to use the integration

## Run commands
```bash
# Make directories
mkdir -p ~/.homeassistant/custom_components/light

# Change to correct directory
cd ~/.homeassistant/custom_components/light

# Checkout repo
git clone git@github.com:olekenneth/pyXcomfort.git

# Symlink integration
ln -s pyXcomfort/integrations/home-assistant/xcomfort.py
```

## Add Xcomfort configuration.yaml
```yaml
light:
- platform: xcomfort
device: /dev/ttyUSB0 # default
devices:
- serial: 2118499
name: Pendel
- serial: 5077172
name: Plafond
```
Where do I get the serial from? You need to look in the [Eaton MRF software](http://www.eaton.eu/Europe/Electrical/ProductsServices/Residential/xComfort-RFSmartHomeSolutions/PCT_1118492#tabs-11)

![Eaton MRF File menu][images/MRF-menu.jpg]
Open File > Details about components

![Eaton MRF Detail screen][images/MRF-details.jpg]
Look at the Serienummer (serial number). I have removed mine, but hopefully you will find your there.



Then you can setup restart Home Assistant
