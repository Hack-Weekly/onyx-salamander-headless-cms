# Developer Guide

## Getting Started

### Installation

    git clone https://github.com/Hack-Weekly/onyx-salamander-headless-cms.git
    cd onyx-salamander-headless-cms
    pip3 -m venv env
    source env/bin/activate
    pip3 install -r requirements.txt

### Running App

`uvicorn main:app --reload`

### API 
API documentation is found at [http://localhost/docs](http://localhost/docs) or [http://localhost/redoc](http://localhost/redoc)