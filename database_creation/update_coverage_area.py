import os
import osmnx as ox
import psycopg2
import overpy

import json
from dotenv import load_dotenv
from shapely.geometry import Polygon, MultiPolygon, mapping

from connection_to_db import CONN_CENTRAL

load_dotenv()
api = overpy.Overpass()

# Načítanie DB parametrov z .env
DB_NAME = os.getenv("POSTGRES_DB_CENTRAL", "central_db")
DB_USER = os.getenv("POSTGRES_USER_CENTRAL", "central_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD_CENTRAL", "central_password")


def get_boundary(place_name):
    gdf = ox.geocode_to_gdf(place_name)
    if gdf.empty:
        raise ValueError(f"Nenašiel sa polygon pre {place_name}")
    polygon = gdf.loc[0, 'geometry']
    geojson = mapping(polygon)
    return geojson


def update_coverage_area(conn, name, geojson):
    with conn.cursor() as cur:
        geojson_text = json.dumps(geojson)
        cur.execute("""
            UPDATE data_sources
            SET coverage_area = ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326),
                updated_at = now()
            WHERE name = %s;
        """, (geojson_text, name))
        if cur.rowcount == 0:
            print(f"Upozornenie: nenájdený záznam pre '{name}', nie je aktualizované coverage_area.")
    conn.commit()

def get_city_boundary(name="Most"):
    api = overpy.Overpass()
    query = f"""
    [out:json];
    area["boundary"="administrative"]["admin_level"="4"]["name"="Česko"]->.cz;
    (
      relation["name"="{name}"]["admin_level"="8"]["boundary"="administrative"](area.cz);
      relation["name"="{name}"]["admin_level"="7"]["boundary"="administrative"](area.cz);
    );
    out body;
    >;
    out skel qt;
    """
    result = api.query(query)

    if not result.relations:
        raise ValueError(f"Nenašiel sa vzťah pre mesto {name}")

    rel = result.relations[0]
    coords = []
    for member in rel.members:
        if isinstance(member, overpy.RelationWay):
            way = member.resolve()
            if way:
                ring = [(float(node.lon), float(node.lat)) for node in way.nodes]
                if len(ring) >= 3:
                    coords.append(ring)

    if not coords:
        raise ValueError("Neboli nájdené žiadne súradnice pre polygon.")

    polygons = [Polygon(ring) for ring in coords if len(ring) >= 3]
    if not polygons:
        raise ValueError("Žiadne platné polygóny")

    polygon = MultiPolygon(polygons) if len(polygons) > 1 else polygons[0]
    return mapping(polygon)

def main():


    try:
        print("Získavam hranice Brna...")
        brno = get_boundary("Brno, Czechia")
        update_coverage_area(CONN_CENTRAL, "brno", brno)
        print("Brno coverage_area aktualizované.")

        print("Získavam hranice Jihomoravského kraja...")
        jmk = get_boundary("Jihomoravský kraj, Czechia")
        update_coverage_area(CONN_CENTRAL, "jmk", jmk)
        print("Jihomoravský kraj coverage_area aktualizované.")

        print("Získavam hranice ORP Most...")
        orp_most = get_city_boundary("Most")
        update_coverage_area(CONN_CENTRAL, "orp_most", orp_most)
        print("ORP Most coverage_area aktualizované.")
    finally:
        CONN_CENTRAL.close()


if __name__ == "__main__":
    main()
