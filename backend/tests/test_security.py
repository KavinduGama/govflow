from app.models import ChatSession
from tests.conftest import auth_header


# ---------- Admin routes ----------

def test_admin_requires_login(client):
    assert client.get("/api/v1/admin/dashboard").status_code == 401
    assert client.post("/api/v1/admin/scrape-sync").status_code == 401


def test_admin_rejects_citizens(client, make_user):
    citizen = make_user("citizen@example.com")
    assert client.get("/api/v1/admin/dashboard", headers=auth_header(citizen)).status_code == 403
    assert client.post("/api/v1/admin/scrape-sync", headers=auth_header(citizen)).status_code == 403


def test_admin_allows_admins(client, make_user):
    admin = make_user("admin@example.com", role="admin")
    res = client.get("/api/v1/admin/dashboard", headers=auth_header(admin))
    assert res.status_code == 200
    assert "services" in res.json()


def test_invalid_token_is_rejected(client):
    res = client.get("/api/v1/admin/dashboard", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401


# ---------- Auth payload ----------

def test_me_includes_role(client, make_user):
    admin = make_user("admin@example.com", role="admin")
    assert client.get("/api/v1/auth/me", headers=auth_header(admin)).json()["role"] == "admin"


def test_new_users_are_citizens(client):
    res = client.post("/api/v1/auth/register", json={
        "name": "New", "email": "new@example.com", "password": "Password123",
    })
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "citizen"


# ---------- Chat thread ownership ----------
# These requests are rejected before the agent runs, so no OpenAI call is made.

def owned_thread(db_session, owner):
    db_session.add(ChatSession(thread_id="owned-thread", title="Mine", user_id=owner.id))
    db_session.commit()


def test_other_user_cannot_continue_thread(client, db_session, make_user):
    owner = make_user("owner@example.com")
    intruder = make_user("intruder@example.com")
    owned_thread(db_session, owner)

    res = client.post("/api/v1/chat", json={"thread_id": "owned-thread", "message": "hi"},
                      headers=auth_header(intruder))
    assert res.status_code == 404


def test_anonymous_cannot_continue_owned_thread(client, db_session, make_user):
    owned_thread(db_session, make_user("owner@example.com"))
    res = client.post("/api/v1/chat", json={"thread_id": "owned-thread", "message": "hi"})
    assert res.status_code == 404


def test_chat_rejects_oversized_message(client):
    res = client.post("/api/v1/chat", json={"thread_id": "t1", "message": "x" * 2001})
    assert res.status_code == 422


# ---------- Rate limiting ----------

def test_login_is_rate_limited(client):
    credentials = {"email": "nobody@example.com", "password": "wrong-password"}
    statuses = [client.post("/api/v1/auth/login", json=credentials).status_code for _ in range(11)]
    assert statuses[:10] == [401] * 10  # wrong password, but allowed to try
    assert statuses[10] == 429          # 11th attempt within a minute is blocked
