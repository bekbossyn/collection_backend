#!/usr/bin/env bash
source '/home/dev/env_collection_backend/bin/activate'
pip install -r requirements.txt
python ocean.py collectstatic --noinput
python ocean.py migrate --noinput

