LineageOS Mirrorbits API
=======================
Copyright (c) 2017 The LineageOS Project<br>


[![Docker Repository on Quay](https://quay.io/repository/lineageos/mirrorbits-api/status "Docker Repository on Quay")](https://quay.io/repository/lineageos/mirrorbits-api)

Development
---
1. Install Mirrorbits (https://github.com/etix/mirrorbits)
2. Install requirements with `pip install -r requirements.txt`
3. Run with `FLASK_APP=app.py flask run`. Access at http://localhost:5000/api/v1/


Production
---
1. Install Mirrorbits (https://github.com/etix/mirrorbits)
2. Install Docker (https://docs.docker.com/engine/installation/)
3. Run `docker run --net=host -d quay.io/lineageos/mirrorbits-api`

