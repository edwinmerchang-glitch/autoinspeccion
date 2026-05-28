"""
views/usuarios.py
-----------------
Gestión de usuarios — solo visible para admins.
Permite crear, cambiar rol/contraseña, activar/desactivar y eliminar usuarios.
"""

import streamlit as st

from db.queries import (
    get_usuarios,
    create_usuario,
    update_usuario,
    delete_usuario,
    ensure_users_table,
)
from auth import current_user


def render() -> None:
    ensure_users_table()
    usuarios = get_usuarios()

    st.markdown("""
    <div class='page-header'>
      <div>
        <div class='ph-title'>👥 Gestión de Usuarios</div>
        <div class='ph-sub'>Agrega, edita o elimina usuarios con sus roles de acceso.</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Crear nuevo usuario ───────────────────────────────────────────────────
    with st.expander("➕ Agregar nuevo usuario", expanded=False):
        with st.form("form_nuevo_usuario", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns([2, 2, 1.5, 1])
            nuevo_user = c1.text_input("Usuario", placeholder="ej: jperez")
            nuevo_pass = c2.text_input("Contraseña", type="password", placeholder="mínimo 6 caracteres")
            nuevo_rol  = c3.selectbox("Rol", ["viewer", "admin"])
            c4.markdown("<br>", unsafe_allow_html=True)
            submitted = c4.form_submit_button("Crear", type="primary", use_container_width=True)

            if submitted:
                if not nuevo_user.strip():
                    st.error("El nombre de usuario es requerido.")
                elif len(nuevo_pass) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    ok = create_usuario(nuevo_user.strip().lower(), nuevo_pass, nuevo_rol)
                    if ok:
                        st.success(f"✅ Usuario **{nuevo_user}** creado con rol **{nuevo_rol}**.")
                        st.rerun()
                    else:
                        st.error(f"⚠️ El usuario **{nuevo_user}** ya existe.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Lista de usuarios ─────────────────────────────────────────────────────
    if len(usuarios) == 0:
        st.markdown("<div class='info-banner'>ℹ️ No hay usuarios registrados.</div>", unsafe_allow_html=True)
        return

    st.markdown("<div class='card'><div class='card-hd'>Usuarios registrados</div>", unsafe_allow_html=True)

    # Cabecera
    st.markdown("""
    <div style='display:grid;grid-template-columns:2fr 1.2fr 1fr 1.5fr 1fr 1fr;gap:.75rem;
         padding:.4rem 1rem;font-size:.68rem;font-weight:700;color:#94a3b8;
         text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid #f1f5f9;margin-bottom:.4rem;'>
      <span>Usuario</span><span>Rol</span><span>Estado</span>
      <span>Nueva contraseña</span><span></span><span></span>
    </div>""", unsafe_allow_html=True)

    editing_id  = st.session_state.get("edit_user_id")
    confirm_del = st.session_state.get("confirm_del_user")
    me          = current_user()

    for _, u in usuarios.iterrows():
        uid      = int(u["id"])
        is_me    = u["username"] == me
        activo   = bool(u["activo"])
        is_admin_user = u["role"] == "admin"

        role_badge = (
            "<span class='badge b-info'>🔑 Admin</span>"
            if is_admin_user else
            "<span class='badge b-gray'>👁️ Viewer</span>"
        )
        status_badge = (
            "<span class='badge b-ok'>Activo</span>"
            if activo else
            "<span class='badge b-fail'>Inactivo</span>"
        )

        c_user, c_rol, c_est, c_pass, c_save, c_del = st.columns([2, 1.2, 1, 1.5, 1, 1])

        with c_user:
            st.markdown(
                f"<div style='padding:.6rem 0;font-size:.85rem;font-weight:600;color:#0f172a;'>"
                f"{u['username']} {'<span style=\"font-size:.68rem;color:#94a3b8;\">(tú)</span>' if is_me else ''}</div>",
                unsafe_allow_html=True
            )

        with c_rol:
            new_role = st.selectbox(
                f"rol_{uid}", ["admin", "viewer"],
                index=0 if is_admin_user else 1,
                key=f"role_{uid}",
                label_visibility="collapsed",
                disabled=is_me,
            )

        with c_est:
            new_activo = st.toggle(
                "Activo", value=activo,
                key=f"activo_{uid}",
                disabled=is_me,
                label_visibility="collapsed",
            )

        with c_pass:
            new_pass = st.text_input(
                f"pass_{uid}", value="",
                placeholder="Nueva contraseña",
                type="password",
                key=f"pass_{uid}",
                label_visibility="collapsed",
            )

        with c_save:
            if st.button("💾 Guardar", key=f"save_{uid}", use_container_width=True):
                update_usuario(uid, new_pass if new_pass else None, new_role, int(new_activo))
                st.success(f"✅ {u['username']} actualizado.")
                st.rerun()

        with c_del:
            if is_me:
                st.markdown("<div style='padding:.6rem 0;font-size:.72rem;color:#94a3b8;'>No puedes eliminarte</div>", unsafe_allow_html=True)
            elif confirm_del == uid:
                dc1, dc2 = st.columns(2)
                if dc1.button("✓", key=f"del_yes_{uid}", use_container_width=True):
                    delete_usuario(uid)
                    st.session_state.pop("confirm_del_user", None)
                    st.rerun()
                if dc2.button("✗", key=f"del_no_{uid}", use_container_width=True):
                    st.session_state.pop("confirm_del_user", None)
                    st.rerun()
            else:
                if st.button("🗑️", key=f"del_{uid}", use_container_width=True):
                    st.session_state["confirm_del_user"] = uid
                    st.rerun()

        st.markdown("<div style='border-top:1px solid #f8fafc;margin:.1rem 0;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Leyenda de roles ──────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
         padding:1rem 1.25rem;margin-top:1rem;font-size:.78rem;color:#64748b;'>
      <div style='font-weight:700;margin-bottom:.5rem;'>Descripción de roles:</div>
      <div><strong>🔑 Admin</strong> — Acceso total: crear/editar auditorías, ver consolidado, gestionar usuarios.</div>
      <div style='margin-top:.25rem;'><strong>👁️ Viewer</strong> — Solo lectura: ve el consolidado y el dashboard, no puede editar.</div>
    </div>""", unsafe_allow_html=True)
