#!/bin/bash

alembic upgrade head
python -m app.main