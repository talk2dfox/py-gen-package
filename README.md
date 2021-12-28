# py-gen-package
utility which generates an initial framework for a python package


Why?

* single-sourcing 
  * package name
  * version
  * description
* automating
  * package name
  * console script config
* testable setup.py

to achieve these goals, I found myself either
* repeatedly coding similar functions in different setup.py
* copying existing setup.py, but then having to customize for individual packages

Part of problem was that I was mixing project-specific configuration with generic code.

Idea was to create a standard setup.py which I could use unmodified for most projects (especially where I just
wanted to convert modules to packages as quickly as possible),
controlled by a relatively simple configuration file for customization.

For config
* restricting setup.py to standard library?
  * conflicting information on whether this is necessarsy.  I see some references to setup_requires, but 
    * it is not used/documented in the python packaging authority guide or sample package
    * some suggestions that pip ignores (may or may not be up-to-date)
* if we restrict to standard library
  * yaml is out
  * hjson (https://hjson.github.io/) is out (sigh)
* want it to be human editable
  * XML is out
* that leaves
  * ini/config parser 
    * more editable
    * but only two mapping layers, when many arguments to setuptools.setup involve nested directories
  * json
    * less editable (wish we could use hjson)
    * no comments (but I've got a workaround that is good enough for my purposes)


ini
* is more editable, but only two mapping layers
json is 


  * doesn't seem to match natural hierarchy and dictionaries in setuptools.setup arguments


(setup_requires exists, but can't find documentation an d



Initially decided to use tar to copy package-framework template to the root of a new package.  

Design of package-framework is intentionally opinionated, to minimize the need to customize:

per https://blog.ionelmc.ro/2014/05/25/python-packaging/
* src packages 
* pytest tests outside installed packages
* autodetect package modules






