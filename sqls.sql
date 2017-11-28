 -- obstacle for point
 select json_build_object('type', 'FeatureCollection','features',
                               json_agg(features)) from (select 'Feature' as type,
                              row_to_json((SELECT l FROM (SELECT osm_id AS feat_id) As l)) As properties,
                              ST_AsGeoJSON(ST_Transform(pl.way, 4326))::json as geometry
                                  from planet_osm_point as pl     where pl.natural = 'peak'
                                                         and
ST_DWithin(ST_Transform(pl.way, 4326)::geography, ST_GeomFromText('POINT(19.759110 48.829909)',4326)::geography, 100000)
                                   limit 200) as features


-- aero data in polygon
 select json_build_object('type', 'FeatureCollection','features', json_agg(features))
from (
    select 'Feature' as type, ST_AsGeoJSON(ST_Transform(pl.way,4326))::json as geometry,
    row_to_json((SELECT l FROM (SELECT osm_id AS feat_id) As l)) As properties
    from planet_osm_polygon as pl
    where pl.aeroway is not null
    and ST_Contains(ST_Transform(ST_GeomFromText('POLYGON((16.94092 47.7541,18.02856 47.78363,19.22212 47.97458,19.41086 49.29616,16.98937 49.57495,16.15215 48.70901,16.94092 47.7541))',4326),4326)::geometry, ST_Transform(pl.way, 4326)::geometry) )as features;


-- obstacle for route

 select json_build_object('type', 'FeatureCollection','features', json_agg(features))
from (
    select 'Feature' as type, ST_AsGeoJSON(ST_Transform(pl.way,4326))::json as geometry,
    row_to_json((SELECT l FROM (SELECT osm_id AS feat_id) As l)) As properties
     from planet_osm_point as pl  where pl.natural = 'peak' and
     ST_Contains(ST_Buffer(ST_Transform(ST_GeomFromText('LINESTRING(20.86428 48.6602, 21.35468 48.68824)',4326),4326)::geometry, 0.05), ST_Transform(pl.way, 4326)::geometry) limit 200 )as features;

--roads for route