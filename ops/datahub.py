# DataHub integration for modern-elt-platform

from datahub.ingestion.graph.client import DataHubGraph
from datahub.emitter.mce_builder import make_dataset_urn
from datahub.ingestion.emit.metadata_emitter import DatahubRestEmitter

class DataHubClient:
    def __init__(self, server_url, token=None):
        self.server_url = server_url
        self.token = token
        self.graph = DataHubGraph(server_url, token=token)
        self.emitter = DatahubRestEmitter(server_url, token=token)

    def get_dataset(self, platform, name, env='PROD'):
        """Get dataset metadata"""
        urn = make_dataset_urn(platform, name, env)
        return self.graph.get_dataset(urn)

    def list_datasets(self, platform=None, env='PROD'):
        """List datasets, optionally filtered by platform"""
        return self.graph.get_datasets(platform=platform, env=env)

    def emit_dataset(self, dataset_urn, aspect_name, aspect_value):
        """Emit dataset aspect"""
        return self.emitter.emit_mce(
            aspect_name=aspect_name,
            aspect_value=aspect_value,
            entity_urn=dataset_urn
        )

    def create_dataset(self, platform, name, description='', env='PROD'):
        """Create a new dataset"""
        urn = make_dataset_urn(platform, name, env)
        # Emit dataset properties aspect
        from datahub.metadata.schema_classes import DatasetPropertiesClass
        properties = DatasetPropertiesClass(
            description=description,
            name=name
        )
        return self.emit_dataset(urn, 'datasetProperties', properties)

    def update_dataset_description(self, platform, name, description, env='PROD'):
        """Update dataset description"""
        from datahub.metadata.schema_classes import DatasetPropertiesClass
        urn = make_dataset_urn(platform, name, env)
        properties = DatasetPropertiesClass(
            description=description,
            name=name
        )
        return self.emit_dataset(urn, 'datasetProperties', properties)

    def add_lineage(self, upstream_urn, downstream_urn):
        """Add lineage between datasets"""
        from datahub.metadata.schema_classes import UpstreamClass
        upstream = UpstreamClass(dataset=upstream_urn, type='TRANSFORMED')
        return self.emit_dataset(
            downstream_urn,
            'upstream',
            {'upstreams': [upstream]}
        )

    def get_lineage(self, dataset_urn):
        """Get lineage for a dataset"""
        return self.graph.get_lineage(dataset_urn)

    def search_entities(self, query, entity_type='dataset', limit=10):
        """Search for entities"""
        return self.graph.search(
            query=query,
            entity_type=entity_type,
            limit=limit
        )

    def get_schema(self, dataset_urn):
        """Get schema metadata for a dataset"""
        return self.graph.get_schema(dataset_urn)

    def emit_schema(self, dataset_urn, schema_fields):
        """Emit schema metadata"""
        from datahub.metadata.schema_classes import SchemaMetadataClass, SchemaFieldClass
        fields = [
            SchemaFieldClass(
                field_path=field['name'],
                type=field['type'],
                native_type=field.get('native_type', 'string'),
                description=field.get('description', '')
            )
            for field in schema_fields
        ]
        schema = SchemaMetadataClass(
            schemaName='default',
            fields=fields
        )
        return self.emit_dataset(dataset_urn, 'schemaMetadata', schema)

    def get_ownership(self, dataset_urn):
        """Get ownership information"""
        return self.graph.get_ownership(dataset_urn)

    def emit_ownership(self, dataset_urn, owners):
        """Emit ownership information"""
        from datahub.metadata.schema_classes import OwnershipClass, OwnerClass, OwnershipTypeClass
        owner_list = [
            OwnerClass(
                owner=owner['urn'],
                type=OwnershipTypeClass(owner.get('type', 'TECHNICAL_OWNER'))
            )
            for owner in owners
        ]
        ownership = OwnershipClass(owners=owner_list)
        return self.emit_dataset(dataset_urn, 'ownership', ownership)

    def get_tags(self, dataset_urn):
        """Get tags for a dataset"""
        return self.graph.get_tags(dataset_urn)

    def emit_tags(self, dataset_urn, tags):
        """Emit tags for a dataset"""
        from datahub.metadata.schema_classes import GlobalTagsClass, TagAssociationClass
        tag_associations = [
            TagAssociationClass(tag=tag)
            for tag in tags
        ]
        tags_obj = GlobalTagsClass(tags=tag_associations)
        return self.emit_dataset(dataset_urn, 'globalTags', tags)
