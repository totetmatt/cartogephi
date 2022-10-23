# Cartogephi

## Setup 
* `git clone` this project or download source
* `pip install -r requirements.txt`

## How to
* Export your graph as `.gexf` and as `.png`. The exported `png` should be at a square format (`height=width`)
* Copy or save the `.gexf` and `.png` into the cartogephi directory.
* Open a terminal and run `python cartogephi.py gexf_file.gexf img_file.png`
  * Check option available with `python cartogephi.py -h`
* Run `python -m http.server` and go to `http://localhost:8000/`

## Tips
* You might need to export your `png` in a very large resolution. To reduce a little the size of the file, [`optipng`](https://optipng.sourceforge.net/) is advised to use. 
  * `optipng -o 5 myimage.png` 