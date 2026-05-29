"""
auth.py
-------
Autenticación con roles (admin / viewer).
Los usuarios se guardan en la tabla `usuarios` de SQLite.
Fallback a st.secrets si la tabla está vacía (primer arranque).
"""

import streamlit as st


def _get_user_from_db(username: str) -> dict | None:
    try:
        from db.queries import get_usuario_by_username, ensure_users_table
        ensure_users_table()
        return get_usuario_by_username(username)
    except Exception:
        return None


def _get_user_from_secrets(username: str) -> dict | None:
    try:
        users = dict(st.secrets.get("users", {}))
        data  = users.get(username.strip().lower())
        if data:
            return {"username": username, "password": data["password"], "role": data["role"]}
    except Exception:
        pass
    return None


def _seed_admin_from_secrets() -> None:
    """Al primer arranque, crea el admin desde secrets si la tabla está vacía."""
    try:
        from db.queries import ensure_users_table, get_usuarios, create_usuario
        ensure_users_table()
        df = get_usuarios()
        if len(df) == 0:
            users = dict(st.secrets.get("users", {}))
            for uname, data in users.items():
                create_usuario(uname, data["password"], data["role"])
            # Fallback si no hay secrets
            if not users:
                create_usuario("admin", "admin123", "admin")
    except Exception:
        pass


def require_login() -> None:
    if st.session_state.get("authenticated"):
        return

    _seed_admin_from_secrets()

    st.title("🏥 Autoinspección Locatel")
    st.caption("Sistema de autoinspección para tiendas Locatel")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("### Ingresa tus credenciales")
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🔐 Ingresar", type="primary", use_container_width=True)

        if submitted:
            user = _get_user_from_db(username) or _get_user_from_secrets(username)
            if user and user["password"] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"]      = username.strip().lower()
                st.session_state["role"]          = user["role"]
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

        st.caption("Contacta al administrador si no tienes acceso.")
        st.caption("Creado por Edwin Merchán.")

    st.stop()


def is_admin() -> bool:
    return st.session_state.get("role") == "admin"


def current_user() -> str:
    return st.session_state.get("username", "")


def logout() -> None:
    for key in ["authenticated", "username", "role", "page"]:
        st.session_state.pop(key, None)
    st.rerun()
