# Earning_Calendar
This module is used to scarp earning information from both yahoo and nasdaq

The main function returns a pandas dataframe contains earning information


# Install
The package is currently not availble from PyPI, please download the folder directly and put it in the packages folder on your computer.

# Example
```
from earning import earning
data = earning(20160315,20160515)   
data.output()            
```
# Other Feathers
yahoo_date()  

nasdaq_date()

yahoo_table()

nasdaq_table()



