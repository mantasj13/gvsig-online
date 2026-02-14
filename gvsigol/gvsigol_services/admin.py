from django.contrib import admin
from .models import (
    Workspace, 
    Datastore, 
    Layer, 
    LayerGroup,
    LayerReadGroup,
    LayerWriteGroup
)

@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_public']
    search_fields = ['name', 'description']
    list_filter = ['is_public']

@admin.register(Datastore)
class DatastoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'workspace', 'type', 'description']
    search_fields = ['name', 'description']
    list_filter = ['workspace', 'type']

@admin.register(Layer)
class LayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'datastore', 'type', 'visible', 'queryable']
    search_fields = ['name', 'title']
    list_filter = ['datastore', 'type', 'visible', 'queryable', 'cached']

@admin.register(LayerGroup)
class LayerGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'cached']
    search_fields = ['name', 'title']
    list_filter = ['cached']

@admin.register(LayerReadGroup)
class LayerReadGroupAdmin(admin.ModelAdmin):
    list_display = ['layer', 'group']
    list_filter = ['group']

@admin.register(LayerWriteGroup)
class LayerWriteGroupAdmin(admin.ModelAdmin):
    list_display = ['layer', 'group']
    list_filter = ['group']
