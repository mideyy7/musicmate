#Folder structure and their purpose

backend/
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── core/
│   │   ├── config.py          # App settings (env vars, constants)
│   │   └── database.py        # SQLite connection & session
│   │
│   ├── models/
│   │   └── user.py            # SQLAlchemy models
│   │
│   ├── schemas/
│   │   └── user.py            # Pydantic schemas
│   │
│   ├── crud/
│   │   └── user.py            # DB operations (create/read/update/delete)
│   │
│   ├── api/
│   │   ├── deps.py            # Dependencies (DB session, auth)
│   │   └── routes/
│   │       └── user.py        # API routes
|   |        |___ spotify.py     #API routes for spotify
│   │
│   └── __init__.py
│
│----── services/                   # External APIs & business logic
│      └── spotify.py              # Spotify API logic (OAuth, requests)
├── db/
│   └── app.db                 # SQLite database file
│
├── tests/
│   └── test_users.py          # API tests
│
├── .env                       # Environment variables
├── requirements.txt
└── README.md
