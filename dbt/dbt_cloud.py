# dbt Cloud integration for modern-elt-platform

import requests
import json

class DbtCloudClient:
    def __init__(self, account_id, api_token, base_url='https://cloud.getdbt.com/api/v2'):
        self.account_id = account_id
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Token {api_token}',
            'Content-Type': 'application/json'
        }

    def list_projects(self):
        """List all dbt Cloud projects"""
        response = requests.get(
            f'{self.base_url}/accounts/{self.account_id}/projects/',
            headers=self.headers
        )
        return response.json()

    def get_project(self, project_id):
        """Get project details"""
        response = requests.get(
            f'{self.base_url}/accounts/{self.account_id}/projects/{project_id}/',
            headers=self.headers
        )
        return response.json()

    def list_environments(self, project_id):
        """List environments for a project"""
        response = requests.get(
            f'{self.base_url}/accounts/{self.account_id}/projects/{project_id}/environments/',
            headers=self.headers
        )
        return response.json()

    def list_jobs(self, project_id):
        """List jobs for a project"""
        response = requests.get(
            f'{self.base_url}/accounts/{self.account_id}/projects/{project_id}/jobs/',
            headers=self.headers
        )
        return response.json()

    def trigger_job(self, job_id, cause='API trigger'):
        """Trigger a dbt job run"""
        response = requests.post(
            f'{self.base_url}/accounts/{self.account_id}/jobs/{job_id}/run/',
            headers=self.headers,
            json={'cause': cause}
        )
        return response.json()

    def get_run(self, run_id):
        """Get details of a specific run"""
        response = requests.get(
            f'{self.base_url}/accounts/{self.account_id}/runs/{run_id}/',
            headers=self.headers
        )
        return response.json()

    def list_runs(self, job_id=None, limit=25):
        """List runs, optionally filtered by job"""
        params = {'limit': limit}
        if job_id:
            params['job_definition_id'] = job_id
        
        response = requests.get(
            f'{self.base_url}/accounts/{self.account_id}/runs/',
            headers=self.headers,
            params=params
        )
        return response.json()

    def cancel_run(self, run_id):
        """Cancel a running job"""
        response = requests.post(
            f'{self.base_url}/accounts/{self.account_id}/runs/{run_id}/cancel/',
            headers=self.headers
        )
        return response.json()

    def get_artifacts(self, run_id):
        """Get artifacts from a run"""
        response = requests.get(
            f'{self.base_url}/accounts/{self.account_id}/runs/{run_id}/artifacts/',
            headers=self.headers
        )
        return response.json()

    def get_run_results(self, run_id):
        """Get run results"""
        response = requests.get(
            f'{self.base_url}/accounts/{self.account_id}/runs/{run_id}/run_results/',
            headers=self.headers
        )
        return response.json()
