import duckdb

conn = duckdb.connect(
    'data-warehouse/warehouse.duckdb',
    read_only=False
)