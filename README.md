# API Showcase

A simple project to showcase my skills at creating and maintaining simple API.

## Quick run

Run `setup.py` to set the project up. Only local env has been tested. Configuration is taken from fastapi-template and I have strong feeling that deployment has been vibecoded (based on the amount of tweaks I had to do for the local setup):
```bash
uv run setup.py
```

Get the project running with docker:
```bash
docker compose up
```

Tests are ran automatically. Check out `localhost:8000/docs` for the Swagger docs.
Also there are structured logs in the [ src/app/core/logs ]

## Project structure
The app is pretty simple so I decided not to implement full onion architecture, but still there are presentation and repository layers.
Database is the main point of truth, you can check out schemas, constraints and triggers in the [src/app/migrations/versions/555d2a91c348_init_db.py]
The schema is straight from the requirements, trigger was a bit tricky.

The repository that communicate with database is in the [src/app/repositories/department.py]
I do not prefer using plain ORM, so most of the requests to the database are sqlalchemy SQL requests. Also the error handling is tightly coupled with database, decoupling would require implementation of the domain layer.

The api and error handlers are in the [ src/app/presentation/v1/department ].

There are a lot of notes here and there in the code which explain my decisions, feel free to browse.
