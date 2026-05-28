"""
auth.py
-------
Sistema de autenticación simple con roles (admin / viewer).
Los usuarios y contraseñas se definen en .streamlit/secrets.toml.

Uso:
    from auth import require_login, is_admin

    require_login()          # muestra login si no hay sesión activa
    if is_admin(): ...       # solo admins pueden editar
"""

import streamlit as st


def _get_users() -> dict:
    """Lee usuarios desde st.secrets. Retorna dict {username: {password, role}}."""
    try:
        return dict(st.secrets.get("users", {}))
    except Exception:
        # Fallback para desarrollo local sin secrets.toml
        return {
            "admin": {"password": "admin123", "role": "admin"},
        }


def require_login() -> None:
    """
    Bloquea la app hasta que el usuario inicie sesión.
    Llama esto al principio de app.py, antes de renderizar cualquier contenido.
    """
    if st.session_state.get("authenticated"):
        return

    # Centrar el formulario
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center;padding:2rem 0 1rem;'>
          <div style='font-size:2rem;'>🏥</div>
          <div style='font-size:1.4rem;font-weight:800;color:#0f172a;letter-spacing:-.02em;margin-top:.5rem;'>
            Autoinspección Locatel
          </div>
          <div style='font-size:.85rem;color:#64748b;margin-top:.25rem;'>
            Ingresa tus credenciales para continuar
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

        if submitted:
            users = _get_users()
            user_data = users.get(username.strip().lower())
            if user_data and user_data["password"] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"]      = username.strip().lower()
                st.session_state["role"]          = user_data["role"]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

        st.markdown("""
        <div style='text-align:center;font-size:.72rem;color:#94a3b8;margin-top:1rem;'>
          Contacta al administrador si no tienes acceso.
        </div>
        """, unsafe_allow_html=True)

    st.stop()


def is_admin() -> bool:
    """Retorna True si el usuario autenticado tiene rol admin."""
    return st.session_state.get("role") == "admin"


def current_user() -> str:
    """Retorna el nombre del usuario autenticado."""
    return st.session_state.get("username", "")


def logout() -> None:
    """Cierra la sesión del usuario actual."""
    for key in ["authenticated", "username", "role", "page"]:
        st.session_state.pop(key, None)
    st.rerun()
