"""
lts_rules.py
The city-agnostic LTS scoring engine. Takes a single street edge's
attributes (already normalized by the city config) and returns an LTS
score 1-4.

IMPORTANT: This is an ADAPTED ruleset based on Furth & Mekuria (2012) /
Furth's published v2.0 criteria tables. The original tables are published
as images, not machine-readable data, so these are documented numeric
approximations of the published bands.

Thresholds are now parameterized (not hardcoded) so we can run a
sensitivity analysis -- see src/sensitivity_analysis.py -- to test how
much the output distribution shifts when we move the LTS-1 boundary.
Defaults below match the original values used in the main pipeline.
"""

def score_segment(facility_type, speed_kmh, lanes, has_parking, is_oneway,
                   lts1_speed=30, lts2_speed=40, lts3_speed=50):
    """
    facility_type: one of 'protected', 'bike_lane', 'mixed'
    speed_kmh: numeric speed (already converted to km/h by the caller)
    lanes: total OSM lane count for the way
    has_parking: bool, whether adjacent on-street parking is present
    is_oneway: bool
    lts1_speed / lts2_speed / lts3_speed: the speed breakpoints (km/h)
    used for the mixed-traffic and no-parking bike-lane thresholds.
    Parameterized for sensitivity testing.

    Returns: int, LTS score 1-4
    """
    effective_lanes = lanes * 2 if is_oneway else lanes

    if facility_type == "protected":
        return 1

    if facility_type == "bike_lane":
        if has_parking:
            if speed_kmh <= lts2_speed and effective_lanes <= 2:
                return 2
            elif speed_kmh <= lts3_speed and effective_lanes <= 4:
                return 3
            else:
                return 4
        else:
            if speed_kmh <= lts1_speed and effective_lanes <= 2:
                return 1
            elif speed_kmh <= lts2_speed and effective_lanes <= 2:
                return 2
            elif speed_kmh <= lts3_speed and effective_lanes <= 4:
                return 3
            else:
                return 4

    # mixed traffic
    if speed_kmh <= lts1_speed and effective_lanes <= 2:
        return 1
    elif speed_kmh <= lts2_speed and effective_lanes <= 2:
        return 2
    elif speed_kmh <= lts3_speed and effective_lanes <= 4:
        return 3
    else:
        return 4
