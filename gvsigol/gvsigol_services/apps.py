

from django.apps import AppConfig

class GvsigolServicesConfig(AppConfig):
    name = 'gvsigol_services'
            
    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Layer'))
        
        # Connect GeoServer user/role sync signal handlers
        try:
            from gvsigol_auth.signals import (
                role_added, role_deleted,
                user_updated, user_roles_updated, user_deleted
            )
            from gvsigol_services.geoserver_usersync import (
                on_role_added, on_role_deleted,
                on_user_updated, on_user_roles_updated, on_user_deleted
            )
            role_added.connect(on_role_added)
            role_deleted.connect(on_role_deleted)
            user_updated.connect(on_user_updated)
            user_roles_updated.connect(on_user_roles_updated)
            user_deleted.connect(on_user_deleted)
        except Exception as e:
            import logging
            logging.getLogger("gvsigol").warning(
                f"Could not connect GeoServer user sync signals: {e}"
            )
