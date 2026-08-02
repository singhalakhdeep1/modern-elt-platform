# Airbyte integration for modern-elt-platform

import requests
import json

class AirbyteClient:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def get_workspaces(self):
        """List all workspaces"""
        response = requests.get(
            f'{self.api_url}/workspaces/list',
            headers=self.headers
        )
        return response.json()

    def get_sources(self, workspace_id):
        """List all sources in a workspace"""
        response = requests.post(
            f'{self.api_url}/sources/list',
            headers=self.headers,
            json={'workspaceId': workspace_id}
        )
        return response.json()

    def create_source(self, source_config):
        """Create a new source"""
        response = requests.post(
            f'{self.api_url}/sources/create',
            headers=self.headers,
            json=source_config
        )
        return response.json()

    def update_source(self, source_id, updates):
        """Update a source"""
        response = requests.post(
            f'{self.api_url}/sources/update',
            headers=self.headers,
            json={'sourceId': source_id, **updates}
        )
        return response.json()

    def delete_source(self, source_id):
        """Delete a source"""
        response = requests.post(
            f'{self.api_url}/sources/delete',
            headers=self.headers,
            json={'sourceId': source_id}
        )
        return response.json()

    def get_destinations(self, workspace_id):
        """List all destinations in a workspace"""
        response = requests.post(
            f'{self.api_url}/destinations/list',
            headers=self.headers,
            json={'workspaceId': workspace_id}
        )
        return response.json()

    def create_destination(self, destination_config):
        """Create a new destination"""
        response = requests.post(
            f'{self.api_url}/destinations/create',
            headers=self.headers,
            json=destination_config
        )
        return response.json()

    def get_connections(self, workspace_id):
        """List all connections"""
        response = requests.post(
            f'{self.api_url}/connections/list',
            headers=self.headers,
            json={'workspaceId': workspace_id}
        )
        return response.json()

    def create_connection(self, connection_config):
        """Create a new connection"""
        response = requests.post(
            f'{self.api_url}/connections/create',
            headers=self.headers,
            json=connection_config
        )
        return response.json()

    def trigger_sync(self, connection_id):
        """Trigger a sync for a connection"""
        response = requests.post(
            f'{self.api_url}/connections/sync',
            headers=self.headers,
            json={'connectionId': connection_id}
        )
        return response.json()

    def get_connection_status(self, connection_id):
        """Get connection status"""
        response = requests.post(
            f'{self.api_url}/connections/status',
            headers=self.headers,
            json={'connectionId': connection_id}
        )
        return response.json()
