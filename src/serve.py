#!/usr/bin/python3
"""serve.py

A handy script for running the development server.

usage:
    ./serve.py
    python3 serve.py

"""
import uvicorn
import onyx.settings as settings

# This section only runs if main.py is called directly
if __name__ in '__main__':
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT,
                reload=settings.DEBUG, log_level=settings.LOG_LEVEL)
    