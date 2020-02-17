# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 16:40:06 2020

@author: Hugo
"""

import os
import main

main.setup_environment_variables()
main.close_logger(os.environ.get("LOGGER_APP_NAME"))
