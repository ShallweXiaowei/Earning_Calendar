# earning
This module is used to scarp earning information from both yahoo and nasdaq

The main function returns a pandas dataframe contains earning information


# Install
```
pip install earning
```

# Example
```
from earning import earning
data = earning(20160315,20160515)   
data.output()            
```
# Other Features
yahoo_date()  

nasdaq_date()

yahoo_table()

nasdaq_table()



