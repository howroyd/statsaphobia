import enum


@enum.unique
class MapID(enum.IntEnum):
    """Map IDs used in the save file to the maps' names."""

    SUNNY_REST = 0
    SUNNY = 1
    BLEASDALE = 2
    WOODWIND = 3
    MAPLE = 4
    EDGEFIELD = 5
    GRAFTON = 6
    PRISON = 7
    ASYLUM = 8
    RIDGEVIEW = 9
    HIGHSCHOOL = 10
    TANGLEWOOD = 11
    WILLOW = 12
    # ??? = 13 # Possibly just a logical gap/sentinel? Maybe the tutorial?
    POINT_HOPE = 14
