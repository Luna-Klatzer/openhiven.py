# Troubleshooting

---

!!! Warning

    **This documentation page is not finished yet! Information can be outdated or entirely not available!**

!!! Bug "Important"

    Before even starting troubleshooting and testing, it is strongly recommended to activate logging as already shown in
    [Logging](../getting_started/logging.html)!

## Issues Downloading the Module

If you encounter issues or warnings with downloading OpenHiven.py, there can be multiple reasons for that.
Here is a small list of known issues and possible solutions to solve them:

- ??? error "Failed to build wheel" 
  
        This error is a very popular in the Python area where since PEP 427 wheels are used to install python packages
        more efficiently and effectively! This can be caused by many different issues but here are some possible 
        solutions to them:
        
        * If `wheel` or `setuptools` are missing or outdated install the most recent version of them and also `pip` 
          just to be sure using:
          ```bash
          pip install --upgrade pip setuptools wheel
          ```
        * If you are using linux or the gcc-compiler try installing the newest version of the gcc compiler which should 
          automatically be used for the building of the wheels. For Linux refer to your Package Manager or Respositor 
          manager where you can install gcc
        
        * If you are using Windows check if the Microsoft C++ Build Tools are working properly

- ??? warning "Using legacy 'setup.py install' for {package}, since package 'wheel' is not installed."

        This warning is caused due to no installation of the package wheel which is required to build and install packages
        using wheel with pip.
        To solve simple install wheel using:
        
        ```bash
        pip install wheel
        ```

## Unexpected behavior

If you encounter unexpected behavior and functionality that is not working like wanted this can either be of a bug of
OpenHiven.py, Connection Problem, Hiven Server error or an issue due to the configuration. 

If you receive results different from those in the documentation, we first 
recommend you looking into the logs and activate `DEBUG` mode to see extended 
logs about the Bot.

If you are using a function, or a method that executes a request there might be an issue with the HTTP request. 
If this is not the case try to look into the input, debug the program and inspect data
for possible issues.

If there are no issues found with the data and everything seems fine, please open an issue on
the [GitHub page](https://github.com/Luna-Klatzer/openhiven.py/issues) for further investigation. We will try to help 
you and also possibly find the error that caused that issue.
