"""Overture address points for Rhode Island -> data/ri/addresses_ri.parquet

Places the official records that carry no point (RIGIS's licensed markets) and researched addresses the map listings lack.
Adapted from ga-eats/pipeline/fetch_extras.py (itself from co-eats).
"""
import os, time
import duckdb

RELEASE = "2026-10-21.0"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "ri")
t = time.time()
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
addr = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=addresses/type=address/*.parquet"
con.execute(f"""COPY (SELECT number, street, unit, postcode, postal_city, address_levels[1].value AS state, address_levels[-1].value AS muni,
  ST_Y(geometry) lat, ST_X(geometry) lon FROM read_parquet('{addr}', hive_partitioning=1)
  WHERE country = 'US' AND bbox.xmin BETWEEN -71.95 AND -71.05 AND bbox.ymin BETWEEN 41.08 AND 42.05)
  TO '{OUT}/addresses_ri.parquet' (FORMAT PARQUET)""")
print(con.execute(f"select count(*), count(*) filter (where state='RI') from '{OUT}/addresses_ri.parquet'").fetchall(), round(time.time() - t), "s")
