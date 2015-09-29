# coding:utf-8
from __future__ import unicode_literals

import imp
import os
f, fname, desc = imp.find_module("validater", [os.path.abspath("../")])
imp.load_module("validater", f, fname, desc)
