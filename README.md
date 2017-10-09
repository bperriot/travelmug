# travelmug
Python web app on the go

This library is designed to be used by people who want to provide a quick and dirty UI to a python script, without having to write html/javascript or bother with a GUI framework.

## Quickstart

```python
import travelmug
mug = travelmug.TravelMug()

@mug.add
def addition(number_1, number_2):
    """Add 2 intergers"""
    return int(number_1) + int(number_2)

mug.run(debug=True)
```
