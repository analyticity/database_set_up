# Výraz na vyhľadanie aktívneho jamu
GET_ACTIVE_JAM = """
SELECT id, update_count, jam_level_avg, jam_level_max,
       speed_kmh_avg, speed_kmh_min,
       jam_length_avg, jam_length_max,
       speed_avg, speed_max,
       delay_avg, delay_max
FROM jams
WHERE uuid = %s AND published_at = %s
"""

# Výraz na UPDATE existujúceho jamu
UPDATE_EXISTING_JAM = """
UPDATE jams SET
    jam_level_avg = %s,
    jam_level_max = GREATEST(jam_level_max, %s),
    speed_kmh_avg = %s,
    speed_kmh_min = LEAST(speed_kmh_min, %s),
    jam_length_avg = %s,
    jam_length_max = GREATEST(jam_length_max, %s),
    speed_avg = %s,
    speed_max = GREATEST(speed_max, %s),
    delay_avg = %s,
    delay_max = GREATEST(delay_max, %s),
    update_count = %s,
    last_updated = %s
WHERE uuid = %s AND active = TRUE
"""

# Výraz na INSERT nového jamu
INSERT_NEW_JAM = """
INSERT INTO jams (
    id, uuid, country, city, turn_type, street,
    end_node, start_node, road_type, blocking_alert_uuid,
    jam_level_max, jam_level_avg,
    speed_kmh_min, speed_kmh_avg,
    jam_length_max, jam_length_avg,
    speed_max, speed_avg,
    delay_max, delay_avg,
    update_count, jam_line,
    published_at, last_updated, active
) VALUES (
    %(id)s, %(uuid)s, %(country)s, %(city)s, %(turn_type)s, %(street)s,
    %(end_node)s, %(start_node)s, %(road_type)s, %(blocking_alert_uuid)s,
    %(jam_level_max)s, %(jam_level_avg)s,
    %(speed_kmh_min)s, %(speed_kmh_avg)s,
    %(jam_length_max)s, %(jam_length_avg)s,
    %(speed_max)s, %(speed_avg)s,
    %(delay_max)s, %(delay_avg)s,
    %(update_count)s, ST_GeogFromText(%(jam_line)s),
    %(published_at)s, %(last_updated)s, %(active)s
)
"""

# Výraz na INSERT segmentov (bulk)
INSERT_SEGMENTS = """
INSERT INTO segments (jam_id, from_node, to_node, segment_id, is_forward)
VALUES %s
"""


# Výraz na vyhľadanie alertu podľa UUID a published_at
GET_ALERT_BY_UUID_AND_TIMESTAMP = """
SELECT 1 FROM alerts
WHERE uuid = %s AND published_at = %s
"""

# Výraz na vloženie nového alertu
INSERT_NEW_ALERT = """
INSERT INTO alerts (
    uuid, country, city, type, subtype, street,
    report_rating, confidence, reliability, road_type, magvar,
    report_by_municipality_user, report_description,
    location, published_at, last_updated, active
) VALUES (
    %(uuid)s, %(country)s, %(city)s, %(type)s, %(subtype)s, %(street)s,
    %(report_rating)s, %(confidence)s, %(reliability)s, %(road_type)s, %(magvar)s,
    %(report_by_municipality_user)s, %(report_description)s,
    ST_GeogFromText(%(location)s), %(published_at)s, %(last_updated)s, %(active)s
)
ON CONFLICT (uuid, published_at) DO UPDATE SET
    confidence = EXCLUDED.confidence,
    reliability = EXCLUDED.reliability,
    report_rating = EXCLUDED.report_rating,
    last_updated = EXCLUDED.last_updated
"""
