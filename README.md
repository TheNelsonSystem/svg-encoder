# svg-encoder
A tool for converting .svg files into various useful base64 encodings. It outputs raw base64, data URIs, percent-encoded base64, and percent-encoded data URIs into a text file for convenient use.

# How to Install
Steps:
- Ensure that Python 3.7 or higher is installed to ensure the program works as intended
- Clone the project, or simply download the svg-encoder.py file

No additional steps are required.

# How to Use
Run the script like so: ```python  svg-encoder.py "INPUT_DIR"```, where ```"INPUT_DIR"``` is the path containing the .svg files you wish to encode. 

Of course, ensure the terminal you are using is within the file directory containing the svg-encoder.py file. If not, just provide the path to the svg-encoder.py within the script: ```python  PATH_TO_SVG/svg-encoder.py "INPUT_DIR"```

By default, the encoded results will be stored within text files sharing the name of the .svg file inside a folder named "svg_encoded". From here, you can copy and use the encoded results as you see fit.

This program also contains various flags which can be of some use...

## Avaliable Optional Flags
- ```-h --help```:: show the help message and quit the script
- ```-o, --output OUTPUT```:: change the output directory
- ```-r, --recursive```:: enable recursive scanning
- ```-f, --override```:: enable overridding of existing encoded .txt files


