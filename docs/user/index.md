# Developer Guide

## Getting Started

### Installation 

#### Installing From Scratch
    git clone https://github.com/Hack-Weekly/onyx-salamander-headless-cms.git
    cd onyx-salamander-headless-cms
    pip3 -m venv env
    source env/bin/activate
    pip3 install -r requirements.txt

#### Installing With Docker
    git clone https://github.com/Hack-Weekly/onyx-salamander-headless-cms.git
    cd onyx-salamander-headless-cms
    touch env
    docker-compose up --build

### Running App
#### Manually
`uvicorn main:app --reload`
#### CLI Quick Run
`./server.py`
#### With Docker
    docker-compose up

### API 
API documentation is found at [http://localhost/docs](http://localhost/docs) or [http://localhost/redoc](http://localhost/redoc)