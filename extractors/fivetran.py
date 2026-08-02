# Fivetran integration for modern-elt-platform

import requests
import json

class FivetranClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://api.fivetran.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}:{self.api_secret}',
            'Content-Type': 'application/json'
        }

    def get_connectors(self):
        """List all connectors"""
        response = requests.get(
            f'{self.base_url}/connectors',
            headers=self.headers
        )
        return response.json()

    def get_connector(self, connector_id):
        """Get connector details"""
        response = requests.get(
            f'{self.base_url}/connectors/{connector_id}',
            headers=self.headers
        )
        return response.json()

    def create_connector(self, connector_config):
        """Create a new connector"""
        response = requests.post(
            f'{self.base_url}/connectors',
            headers=self.headers,
            json=connector_config
        )
        return response.json()

    def update_connector(self, connector_id, updates):
        """Update connector configuration"""
        response = requests.patch(
            f'{self.base_url}/connectors/{connector_id}',
            headers=self.headers,
            json=updates
        )
        return response.json()

    def delete_connector(self, connector_id):
        """Delete a connector"""
        response = requests.delete(
            f'{self.base_url}/connectors/{connector_id}',
            headers=self.headers
        )
        return response.json()

    def trigger_sync(self, connector_id):
        """Trigger a manual sync for a connector"""
        response = requests.post(
            f'{self.base_url}/connectors/{connector_id}/trigger',
            headers=self.headers
        )
        return response.json()

    def get_sync_logs(self, connector_id, limit=10):
        """Get sync logs for a connector"""
        response = requests.get(
            f'{self.base_url}/connectors/{connector_id}/sync-logs',
            headers=self.headers,
            params={'limit': limit}
        )
        return response.json()

    def get_schema_config(self, connector_id):
        """Get schema configuration for a connector"""
        response = requests.get(
            f'{self.base_url}/connectors/{connector_id}/schemas',
            headers=self.headers
        )
        return response.json()

    def update_schema_config(self, connector_id, schema_config):
        """Update schema configuration"""
        response = requests.patch(
            f'{self.base_url}/connectors/{connector_id}/schemas',
            headers=self.headers,
            json=schema_config
        )
        return response.json()
