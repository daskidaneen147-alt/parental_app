# ============================================================
#  backend/auth.py  —  Login, Signup, Session management
# ============================================================

import hashlib
import secrets
from backend.database import fetch_one, execute_query

# ── Active session (in-memory while app is running) ────────
current_user = {
    "id":    None,
    "name":  "",
    "email": "",
    "role":  "",   # "parent" or "child"
}


def hash_password(password: str) -> str:
    """
    Convert plain password → secure hash.
    We add a random 'salt' so two identical passwords
    get different hashes (more secure).
    """
    salt   = "guardianEye_secure_salt_2024"   # In production: store per-user salt
    combo  = salt + password
    return hashlib.sha256(combo.encode()).hexdigest()


def signup_parent(name: str, email: str, password: str) -> dict:
    """
    Register a new parent account.
    Returns: {"success": True/False, "message": "..."}
    """
    # Check email not already used
    existing = fetch_one("SELECT id FROM parents WHERE email = ?", (email,))
    if existing:
        return {"success": False, "message": "Email already registered!"}

    # Basic validation
    if len(password) < 6:
        return {"success": False, "message": "Password must be 6+ characters."}
    if "@" not in email:
        return {"success": False, "message": "Please enter a valid email."}

    pw_hash = hash_password(password)
    execute_query(
        "INSERT INTO parents (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, pw_hash)
    )
    return {"success": True, "message": "Account created successfully!"}


def login_parent(email: str, password: str) -> dict:
    """
    Verify parent credentials.
    Returns: {"success": True/False, "message": "...", "user": {...}}
    """
    pw_hash = hash_password(password)
    user = fetch_one(
        "SELECT id, name, email FROM parents WHERE email = ? AND password_hash = ?",
        (email, pw_hash)
    )
    if not user:
        return {"success": False, "message": "Incorrect email or password."}

    # Save to session
    current_user.update({
        "id":    user["id"],
        "name":  user["name"],
        "email": user["email"],
        "role":  "parent",
    })
    return {"success": True, "message": f"Welcome back, {user['name']}!", "user": user}


def logout():
    """Clear the current session."""
    current_user.update({"id": None, "name": "", "email": "", "role": ""})


def get_current_user() -> dict:
    """Return who is logged in right now."""
    return current_user


def is_logged_in() -> bool:
    return current_user["id"] is not None