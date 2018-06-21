#!/bin/bash
for dd in `ls -l | grep -v media | grep -v README.md | grep -v  cywareusers | grep -v db.sqlite3| grep -v manage.py | grep -v migrate.sh |awk '{print $9}'`;do python manage.py makemigrations $dd; done
python manage.py migrate
