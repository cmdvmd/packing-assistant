<img src="icon.png" align="right" alt="Icon"/>

# Packer

[Video Demo](https://youtu.be/uLSk44_PynM)

A simple app to keep track of items packed in multiple bags written with [Python](https://python.org),
[Kivy](https://kivy.org), and [SQLite](https://sqlite.org). Users can include details of their bags,
such as a name and description which can be edited at anytime. After creating a bag, users can add items
as they begin to pack. Upon adding a bag to the app, a QR code will be generated, which can be saved and
stuck to its respective bag. Upon pressing the camera button on the main screen, this QR code can be scanned.
Scanning a valid QR code will show the details of the corresponding bag.

Packer can help keep track of belongings packed into bags. At the airport, many people will attempt to find
something they packed and have to dig through all of their bags just to find it. By listing the items in Packer,
Users wil be able to find items quickly. The QR code also allows users to find all items in their bag quickly.
As a safety feature, the QR code will only work on the device it was generated on.

### Files

- [main.py](main.py)
    - Main file of the app
    - Handles the app's logic
- [packer.kv](packer.kv)
    - Written in KV language
    - Handles the app's user interface

## Installation

Download the Packer source code and run the following command to install Packer's requirements:

```shell
$ pip install -r requirements.txt
```

## Build

Ensure to run Packer correctly based on the target platform

### Desktop

Run packer like any other script on Desktop

```shell
$ python main.py
```

### Android

To build Packer for Android, use [Buildozer](https://buildozer.readthedocs.io/en/latest/installation.html).
A [`buildozer.spec`](buildozer.spec) file has been included, which can be edited as needed

```shell
$ pip install buildozer
$ buildozer -v android debug
```
_Note: Buildozer is not available for Windows. To compile for Android on Windows, use the Windows Subsystem for Linux (WSL)_
