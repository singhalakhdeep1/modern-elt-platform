# Soda integration for modern-elt-platform

from soda.scan import Scan

class SodaClient:
    def __init__(self, config_path='soda_configuration.yml'):
        self.config_path = config_path
        self.scan = None

    def create_scan(self, data_source_name):
        """Create a new Soda scan"""
        self.scan = Scan()
        self.scan.add_configuration_yaml_file(self.config_path)
        self.scan.set_data_source_name(data_source_name)
        return self.scan

    def add_checks_yaml(self, checks_path):
        """Add checks from a YAML file"""
        if self.scan:
            self.scan.add_sodacl_yaml_file(checks_path)
        return self.scan

    def add_check(self, check_definition):
        """Add a single check"""
        if self.scan:
            self.scan.add_sodacl_yaml_str(check_definition)
        return self.scan

    def execute(self):
        """Execute the scan and return results"""
        if self.scan:
            return self.scan.execute()
        return None

    def get_scan_results(self):
        """Get scan results"""
        if self.scan:
            return {
                'checks': self.scan.get_checks_results(),
                'metrics': self.scan.get_metrics_results(),
                'logs': self.scan.get_logs_text()
            }
        return None

    def get_failed_checks(self):
        """Get only failed checks"""
        results = self.get_scan_results()
        if results:
            return [check for check in results['checks'] if check.get('outcome') == 'fail']
        return []

    def get_passed_checks(self):
        """Get only passed checks"""
        results = self.get_scan_results()
        if results:
            return [check for check in results['checks'] if check.get('outcome') == 'pass']
        return []

    def get_warned_checks(self):
        """Get only warned checks"""
        results = self.get_scan_results()
        if results:
            return [check for check in results['checks'] if check.get('outcome') == 'warn']
        return []

    def create_row_count_check(self, table_name, min_rows=1, max_rows=None):
        """Create a row count check"""
        check = f"""
          checks for {table_name}:
            - row_count >= {min_rows}
        """
        if max_rows:
            check += f"""
            - row_count <= {max_rows}
        """
        return self.add_check(check)

    def create_schema_check(self, table_name, required_columns):
        """Create a schema check for required columns"""
        columns_str = ', '.join(required_columns)
        check = f"""
          checks for {table_name}:
            - schema:
                fail:
                    when required column missing:
                      - {columns_str}
        """
        return self.add_check(check)

    def create_freshness_check(self, table_name, timestamp_column, max_staleness_hours=24):
        """Create a freshness check"""
        check = f"""
          checks for {table_name}:
            - freshness({timestamp_column}) < {max_staleness_hours}h
        """
        return self.add_check(check)

    def create_null_check(self, table_name, column_name, max_null_percentage=0):
        """Create a null check"""
        check = f"""
          checks for {table_name}:
            - missing_count({column_name}) / row_count < {max_null_percentage}
        """
        return self.add_check(check)

    def create_duplicate_check(self, table_name, columns):
        """Create a duplicate check"""
        columns_str = ', '.join(columns)
        check = f"""
          checks for {table_name}:
            - duplicate_count({columns_str}) = 0
        """
        return self.add_check(check)
