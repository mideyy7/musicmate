from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
import secrets
import requests

from passlib.hash import bcrypt
import json
import os
import re

DATABASE_FILE = "users.json"


def load_users():
    if not os.path.exists(DATABASE_FILE):
        return {}
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(DATABASE_FILE, "w") as f:
        json.dump(users, f, indent=4)

USERS = load_users()  # Temp for usernames, will be linked to DB


app = FastAPI()

# Required for sessions
app.add_middleware(
    SessionMiddleware,
    secret_key="f7c0a3f5c6e1a9b4d2f6c7b8e4a1c6d0b9e5f4a6c8d1e3f5a7b9c2d4e9"
)

CAS_BASE = "https://studentnet.cs.manchester.ac.uk/authenticate/"
CALLBACK_URL = "https://tautomeric-alternately-polly.ngrok-free.dev/callback" # url of MM

# Start login
@app.get("/signup")
def login(request: Request):
    ticket = secrets.token_hex(16)
    request.session["csticket"] = ticket

    return RedirectResponse(
        f"{CAS_BASE}?url={CALLBACK_URL}"
        f"&csticket={ticket}&version=3&command=validate"
    )

# CAS callback
@app.get("/callback")
def callback(request: Request):
    session = request.session

    if "csticket" not in session:
        return HTMLResponse("Invalid session", status_code=400)

    username = request.query_params.get("username")
    fullname = request.query_params.get("fullname")

    if not username or not fullname:
        return HTMLResponse("Authentication failed", status_code=400)

    # Verify with CAS
    verify = requests.get(
        CAS_BASE,
        params={
            "url": CALLBACK_URL,
            "csticket": session["csticket"],
            "version": 3,
            "command": "confirm",
            "username": username,
            "fullname": fullname,
        },
        timeout=5,
    )

    if verify.text.strip() != "true":
        return HTMLResponse("CAS verification failed", status_code=403)

    # Log user in
    session["user"] = {
        "username": username,
        "fullname": fullname,
    }
    session.pop("csticket", None)

    if username in USERS:   # Change to actual DB
        session["user"] = USERS[username]
        return RedirectResponse("/dashboard")

    return RedirectResponse("/create-account")

def validate_password(password: str):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return "Password must contain at least one special character."
    return None  # valid


# Create account
@app.get("/create-account", response_class=HTMLResponse)
def create_account_page(request: Request, error: str = "", username: str = "", display_name: str = ""):
    cas_user = request.session.get("user")
    if not cas_user:
        return RedirectResponse("/")

    return HTMLResponse(f"""
    <h1>Create your account</h1>

    <p>Full name: <strong>{cas_user['fullname']}</strong></p>

    {f'<p style="color:red">{error}</p>' if error else ''}
    <form action="/create-account" method="post">
        <input name="username" placeholder="Username" value="{username}" required><br><br>
        <input name="display_name" placeholder="Display name" value="{display_name}" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <button type="submit">Create account</button>
    </form>
    """)

@app.post("/create-account")
def create_account(
    request: Request,
    username: str = Form(...),
    display_name: str = Form(...),
    password: str = Form(...)
):
    cas_user = request.session.get("user")
    if not cas_user:
        return RedirectResponse("/")

    if username in USERS:
        return create_account_page(request, error="Username already taken.", username=username, display_name=display_name)
    
    # Validate password
    error = validate_password(password)
    if error:
        return create_account_page(request, error=error, username=username, display_name=display_name)

    USERS[username] = {
        "username": username,
        "display_name": display_name,
        "fullname": cas_user["fullname"],
        "password_hash": bcrypt.hash(password),
    }

    save_users(USERS)

    # Log user in
    request.session["user"] = USERS[username]
    request.session.pop("cas_user", None)

    return RedirectResponse("/dashboard", status_code=302)

@app.post("/login_custom")
def login_custom(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = USERS.get(username)

    # Check user exists
    if not user or not bcrypt.verify(password, user["password_hash"]):
        return HTMLResponse(login_page(error="Invalid username or password"))

    # Log them in
    request.session["user"] = user

    return RedirectResponse("/dashboard", status_code=302)

def login_page(error: str = None):
    error_html = f"<p style='color:red;'>{error}</p>" if error else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login / Signup</title>    
        <style>
            body {{
                font-family: sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                gap: 20px;
            }}
            form {{
                display: flex;
                flex-direction: column;
                gap: 8px;
                border: 1px solid #ccc;
                padding: 20px;
                border-radius: 8px;
            }}
            input {{
                padding: 8px;
                font-size: 1rem;
            }}
            button {{
                font-size: 1.1rem;
                padding: 10px;
                cursor: pointer;
                background-color: #4B0082;
                color: white;
                border: none;
                border-radius: 5px; 
            }}
        </style>
    </head>
    <body>
        <h2>Sign In</h2>
        {error_html}
        <form action="/login_custom" method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign In</button>
        </form>

        <h2>Sign Up using UoM email</h2>
        <form action="/signup" method="get">
            <button type="submit">Sign Up with UoM</button>
        </form>
    </body>
    </html>
    """


# Protected page
@app.get("/dashboard")
def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/uom")

    return HTMLResponse(f"""
        <h1>Welcome {user['fullname']}</h1>
        <p>Username: {user['username']}</p>
        <a href="/logout">Log out</a>
    """)

# Logout
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(login_page())

