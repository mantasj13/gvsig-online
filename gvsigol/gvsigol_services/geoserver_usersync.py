"""
GeoServer User/Role Sync Module

Syncs Django users and roles to GeoServer via its REST API.
This replaces the LDAP-based sync when LDAP is not configured.
"""

import logging
import requests
from django.conf import settings
from gvsigol_auth.auth_backend import get_roles, to_provider_rolename

logger = logging.getLogger("gvsigol")


def _get_servers():
    """Get all GeoServer server configurations from DB"""
    from gvsigol_services.models import Server, Node
    servers = []
    for s in Server.objects.all():
        master_node = None
        for n in Node.objects.filter(server=s):
            if n.is_master:
                master_node = n.url
                break
        if not master_node:
            master_node = s.frontend_url
        servers.append({
            'url': master_node + "/rest",
            'user': s.user,
            'password': s.password,
        })
    return servers


def _gs_request(method, path, gs, json=None):
    """Make authenticated request to GeoServer REST API"""
    url = gs['url'] + path
    try:
        resp = getattr(requests, method)(
            url,
            json=json,
            auth=(gs['user'], gs['password']),
            headers={"Content-Type": "application/json"},
            timeout=10,
            verify=False
        )
        return resp
    except Exception as e:
        logger.error(f"GeoServer REST API error: {method.upper()} {url}: {e}")
        return None


def sync_role(role_name):
    """Create a role in GeoServer if it doesn't exist"""
    gs_role = to_provider_rolename(role_name, provider='geoserver')
    for gs in _get_servers():
        resp = _gs_request('post', f'/security/roles/role/{gs_role}', gs)
        if resp is not None:
            if resp.status_code in (200, 201):
                logger.info(f"Created GeoServer role: {gs_role}")
            elif resp.status_code == 409:
                logger.debug(f"GeoServer role already exists: {gs_role}")
            else:
                logger.warning(f"Failed to create GeoServer role {gs_role}: {resp.status_code} {resp.text}")


def delete_role(role_name):
    """Delete a role from GeoServer"""
    gs_role = to_provider_rolename(role_name, provider='geoserver')
    for gs in _get_servers():
        resp = _gs_request('delete', f'/security/roles/role/{gs_role}', gs)
        if resp is not None:
            if resp.status_code in (200, 204):
                logger.info(f"Deleted GeoServer role: {gs_role}")
            else:
                logger.warning(f"Failed to delete GeoServer role {gs_role}: {resp.status_code}")


def sync_user(username, password=None):
    """Create or update a user in GeoServer"""
    for gs in _get_servers():
        # Check if user exists
        resp = _gs_request('get', f'/security/usergroup/user/{username}', gs)
        if resp is not None and resp.status_code == 200:
            # User exists - update password if provided
            if password:
                data = {"user": {"userName": username, "password": password, "enabled": True}}
                resp = _gs_request('post', f'/security/usergroup/user/{username}', gs, json=data)
                if resp is not None and resp.status_code in (200, 201):
                    logger.info(f"Updated GeoServer user password: {username}")
                else:
                    logger.warning(f"Failed to update GeoServer user {username}: {resp.status_code if resp else 'no response'}")
        else:
            # User doesn't exist - create
            if not password:
                logger.warning(f"Cannot create GeoServer user {username}: no password provided")
                return
            data = {"user": {"userName": username, "password": password, "enabled": True}}
            resp = _gs_request('post', '/security/usergroup/users', gs, json=data)
            if resp is not None:
                if resp.status_code in (200, 201):
                    logger.info(f"Created GeoServer user: {username}")
                elif resp.status_code == 409:
                    logger.debug(f"GeoServer user already exists: {username}")
                else:
                    logger.warning(f"Failed to create GeoServer user {username}: {resp.status_code} {resp.text}")


def delete_user(username):
    """Delete a user from GeoServer"""
    for gs in _get_servers():
        resp = _gs_request('delete', f'/security/usergroup/user/{username}', gs)
        if resp is not None:
            if resp.status_code in (200, 204):
                logger.info(f"Deleted GeoServer user: {username}")
            else:
                logger.warning(f"Failed to delete GeoServer user {username}: {resp.status_code}")


def assign_user_roles(username, roles):
    """Assign roles to a user in GeoServer (additive)"""
    for gs in _get_servers():
        for role_name in roles:
            gs_role = to_provider_rolename(role_name, provider='geoserver')
            # Ensure role exists
            _gs_request('post', f'/security/roles/role/{gs_role}', gs)
            # Assign role to user
            resp = _gs_request('post', f'/security/roles/role/{gs_role}/user/{username}', gs)
            if resp is not None:
                if resp.status_code in (200, 201):
                    logger.info(f"Assigned role {gs_role} to user {username}")
                elif resp.status_code == 409:
                    logger.debug(f"User {username} already has role {gs_role}")
                else:
                    logger.warning(f"Failed to assign role {gs_role} to {username}: {resp.status_code}")


def sync_user_roles(username, roles):
    """
    Sync roles for a user in GeoServer.
    Removes roles not in the list, adds missing ones.
    """
    for gs in _get_servers():
        # Get current roles
        resp = _gs_request('get', f'/security/roles/user/{username}', gs)
        current_gs_roles = set()
        if resp is not None and resp.status_code == 200:
            try:
                data = resp.json()
                current_gs_roles = set(data.get('roles', []))
            except:
                pass

        target_gs_roles = set(to_provider_rolename(r, provider='geoserver') for r in roles)

        # Remove extra roles
        for role in current_gs_roles - target_gs_roles:
            _gs_request('delete', f'/security/roles/role/{role}/user/{username}', gs)
            logger.info(f"Removed role {role} from user {username}")

        # Add missing roles
        for role in target_gs_roles - current_gs_roles:
            # Ensure role exists
            _gs_request('post', f'/security/roles/role/{role}', gs)
            resp = _gs_request('post', f'/security/roles/role/{role}/user/{username}', gs)
            if resp is not None and resp.status_code in (200, 201):
                logger.info(f"Assigned role {role} to user {username}")


def full_sync(default_password=None):
    """
    Sync ALL existing Django users and roles to GeoServer.
    
    Parameters
    ----------
    default_password: str or None
        Password to set for users that need to be created in GeoServer.
        If None, users are created without password update (they must
        already exist or will need password set later).
    """
    from django.contrib.auth.models import User
    from gvsigol_auth.models import Role

    logger.info("Starting full GeoServer user/role sync...")

    # 1. Sync all roles
    for role in Role.objects.all():
        sync_role(role.name)
    logger.info("Roles synced.")

    # 2. Sync all users
    for user in User.objects.filter(is_active=True):
        sync_user(user.username, password=default_password)
        # Get user's roles and assign them
        try:
            roles = get_roles(user)
            if roles:
                assign_user_roles(user.username, roles)
        except Exception as e:
            logger.error(f"Error syncing roles for user {user.username}: {e}")

    logger.info("Full GeoServer sync completed.")


# Signal handlers

def on_role_added(sender, **kwargs):
    """Signal handler for role_added"""
    role_name = kwargs.get('role')
    if role_name:
        try:
            sync_role(role_name)
        except Exception as e:
            logger.error(f"Error syncing new role to GeoServer: {e}")


def on_role_deleted(sender, **kwargs):
    """Signal handler for role_deleted"""
    role_name = kwargs.get('role')
    if role_name:
        try:
            delete_role(role_name)
        except Exception as e:
            logger.error(f"Error deleting role from GeoServer: {e}")


def on_user_updated(sender, **kwargs):
    """Signal handler for user_updated"""
    username = kwargs.get('username')
    password = kwargs.get('password')
    roles = kwargs.get('roles')
    if username:
        try:
            sync_user(username, password=password)
            if roles:
                assign_user_roles(username, roles)
        except Exception as e:
            logger.error(f"Error syncing user to GeoServer: {e}")


def on_user_roles_updated(sender, **kwargs):
    """Signal handler for user_roles_updated"""
    username = kwargs.get('username')
    roles = kwargs.get('roles')
    if username and roles is not None:
        try:
            sync_user_roles(username, roles)
        except Exception as e:
            logger.error(f"Error syncing user roles to GeoServer: {e}")


def on_user_deleted(sender, **kwargs):
    """Signal handler for user_deleted"""
    username = kwargs.get('username')
    if username:
        try:
            delete_user(username)
        except Exception as e:
            logger.error(f"Error deleting user from GeoServer: {e}")
