#!/bin/bash
source venv/bin/activate
gunicorn --config gunicorn-cfg.py run:app