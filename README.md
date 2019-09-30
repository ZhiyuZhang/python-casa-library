# python-casa-library
for casa/python usage.

# Instructions
To use the some scripts in this repositories, you should have casa '[Analysis Utilites](https://casaguides.nrao.edu/index.php/Analysis_Utilities)' available locally

## Install
Many scripts in this repositories can be used by 'Copy-and-Paste'. To use some of them as external functions, you need first put the parent directory into your system path. Editing your initialization file of casa in $HOME/.casa/init.py and adding:

```python
system.path.append("/PATH_TO_THIS_DIRECTORY/")
```

Then you can use them by importing them
