# Travelmug
Python web app on the go

This library is designed to be used by people who want to provide a quick and dirty UI to a python script, without having to write html/javascript or bother with a GUI framework.

## Quickstart

After installing travelmug, run the following script:

```python
import travelmug
mug = travelmug.TravelMug()

@mug.add
def addition(number_1, number_2):
    """Add 2 intergers"""
    return int(number_1) + int(number_2)

mug.run(debug=True)
```

and connect to localhost:5000 in your browser. Here is what the generated web page will look like:

![simpliest_travelmug](https://user-images.githubusercontent.com/5694419/31325733-34f050a2-ac75-11e7-8896-3f2095d6eb5a.png)

## More advanced usecases

Take a look at the demo directory.

## Install (devel version)

Clone the repository and use pip -e to install travelmug from the latest commit

```
git clone https://github.com/bperriot/travelmug.git
pip install -e travelmug
```


Once travelmug is published on PyPI, pip install travelmug will be possible, but for now the above method is the only one available.
