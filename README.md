# Multi-Threaded-BruteForcer [![python](https://img.shields.io/badge/Python-2.7-green.svg?style=style=flat-square)](https://www.python.org/downloads/)  [![python](https://img.shields.io/badge/Python-3-green.svg?style=style=flat-square)](https://www.python.org/downloads/)  [![version](https://img.shields.io/badge/Version-Beta-blue.svg?style=style=flat-square)](https://twitter.com/nas_bench)

Multi-Threaded-BruteForcer is a script that automates a brute-force attack on a login page.

## Functionalities

* ```Multi threaded requests```
* ```Dictionary based attacks```
* ```Login's with CSRF tokens```

## Requirements

Install requirements :

```bash
pip install -r Requirements.txt
```

## Usage

To get a list of the options to use :

```bash
python BruteForcer.py -h
```

To run the script (Example) :

```bash
python BruteForcer.py -u http://localhost/login.php -correct "Welcome" -wrong "Wrong username/password" -user admin --dict "pass.txt" -g -userField username -passField password
```
