# **3OSCx1F**   //    Waveform Generator with Oscilloscope
**3OSCx1F** is a 3-channel waveform generator with a filter (high/lowpass) and an oscilloscope visualising output waveform and spectrum in real time.<br>

## About the project
I started this project as an attempt to create an app visualizing customizable data in real time. It's also a showcase of my self-written library for signal generation.

## Technologies in use
- Python
  - matplotlib
  - PyQt6
  - threading
  - scipy
## Requirements

<details>
  <summary>Click to expand</summary>
  <ul>
    click==8.1.3 <br>
    colorama==0.4.4 <br>
    cycler==0.11.0 <br>
    fonttools==4.33.3 <br>
    kiwisolver==1.4.2 <br>
    matplotlib==3.5.2 <br>
    numpy==1.22.4 <br>
    packaging==21.3 <br>
    Pillow==9.1.1 <br>
    pyparsing==3.0.9 <br>
    PyQt6==6.3.0 <br>
    pyqt6-plugins==6.1.0.2.2 <br>
    PyQt6-Qt6==6.3.0 <br>
    PyQt6-sip==13.3.1 <br>
    pyqt6-tools==6.1.0.3.2 <br>
    python-dateutil==2.8.2 <br>
    python-dotenv==0.20.0 <br>
    qt6-applications==6.1.0.2.2 <br>
    qt6-tools==6.1.0.1.2 <br>
    scipy==1.8.1 <br>
    six==1.16.0 <br>
  </ul>
</details>

## How to use
- Make sure you have Python and venv library installed and added to PATH
### Windows
- Run setup.ps1
### Other OS
- Create virtual environment in the base folder of an application and activate it using<br>
  > pip -m venv venv<br>
  > venv/Scripts/Activate.ps1<br>
- Make sure to have installed all of the depandancies from requirements.txt<br>
  > pip install -r requirements.txt
- Run main.py<br>
  > cd src<br>python main.py


### Alternatively (without virtual environment)
- Make sure to have installed all of the depandancies from requirements.txt<br>
  > pip install -r requirements.txt
- Run src/main.py (making sure that your base folder is /src)<br><br>

