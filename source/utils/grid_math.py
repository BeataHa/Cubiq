# -*- coding: utf-8 -*-
"""
grid_math.py
----------
Pomocné funkce pro aplikaci Cubiq🧊.

Obsahuje pomocné nástroje pro gridy 2D i 3D.
(neřeší pygame ani vykreslování)
"""

import math


# ==================================================
# OBECNÁ GEOMETRIE (2D i 3D)
# ==================================================

def distance_nd(a: tuple, b: tuple) -> float:
    """
    Eukleidovská vzdálenost dvou bodů v N dimenzích.
    """
    return math.sqrt(sum((b[i] - a[i]) ** 2 for i in range(len(a))))


def distance_to_line(mouse_pos: tuple,
                     line_point_a: tuple,
                     line_point_b: tuple) -> float:
    """
    Vrátí vzdálenost kurzoru od úsečky mezi dvěma body.
    Používá se pro mazání spojení.
    """
    mouse_x, mouse_y = mouse_pos
    ax, ay = line_point_a
    bx, by = line_point_b

    ab_vector_x = bx - ax
    ab_vector_y = by - ay
    am_vector_x = mouse_x - ax
    am_vector_y = mouse_y - ay

    ab_length_squared = ab_vector_x ** 2 + ab_vector_y ** 2
    if ab_length_squared == 0:
        # ochrana proti dělení nulou
        return math.hypot(mouse_x - ax, mouse_y - ay)

    projection = ((am_vector_x * ab_vector_x) +
                  (am_vector_y * ab_vector_y)) / ab_length_squared
    projection_adjusted = max(0, min(1, projection))

    nearest_x = ax + projection_adjusted * ab_vector_x
    nearest_y = ay + projection_adjusted * ab_vector_y

    return math.hypot(mouse_x - nearest_x, mouse_y - nearest_y)


def are_colinear_nd(*points: tuple) -> bool:
    """
    Zjistí, zda body leží na jedné přímce (2D i 3D).
    """
    if len(points) < 3:
        return True

    def vector(a, b):
        return tuple(b[i] - a[i] for i in range(len(a)))

    def is_multiple(v1, v2):
        ratios = []
        for a, b in zip(v1, v2):
            if a == 0:
                if b != 0:
                    return False
            else:
                ratios.append(b / a)
        return len(set(ratios)) <= 1

    base = vector(points[0], points[1])
    for p in points[2:]:
        if not is_multiple(base, vector(points[0], p)):
            return False
    return True


# ==================================================
# OPERACE SE SPOJENÍMI (ND)
# ==================================================

def overlaps_nd(conn1, conn2, get_coords):
    """
    Zjistí, zda se dvě úsečky v gridu překrývají (2D i 3D).
    """
    p1 = get_coords(conn1.point_a)
    p2 = get_coords(conn1.point_b)
    p3 = get_coords(conn2.point_a)
    p4 = get_coords(conn2.point_b)

    def find_point_in_between(point_a, point_b):
        # bod mezi existuje jen pokud se souřadnice liší o 2
        for x, y in zip(point_a, point_b):
            if abs(x - y) not in (0, 2):
                return None

        return tuple((x + y) // 2 for x, y in zip(point_a, point_b))

    # speciální případ, pro bod
    if (p1 == p2) and ((p1 == p3 or p1 == p4) or (p1 == find_point_in_between(p3, p4))):
        return True
    elif (p3 == p4) and ((p3 == p1 or p3 == p2) or (p3 == find_point_in_between(p1, p2))):
        return True

    if not are_colinear_nd(p1, p2, p3, p4):
        return False

    # musí sdílet alespoň jeden bod
    if not (p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4):
        return False

    # ignorujeme jednoprvkové úsečky
    return distance_nd(p1, p2) > 1 or distance_nd(p3, p4) > 1


def merge_segments_nd(conn1, conn2, get_coords, ConnectionClass):
    """
    Pokusí se sloučit dvě úsečky ND (2D nebo 3D) do jedné delší,
    pokud leží na jedné přímce a mají stejný typ čáry (plná/čárkovaná).
    Pokud se liší dashed stav a překrývají, zachová aktuálnější (conn2).
    """
    # body jako n-tice pro výpočty
    p1 = get_coords(conn1.point_a)
    p2 = get_coords(conn1.point_b)
    p3 = get_coords(conn2.point_a)
    p4 = get_coords(conn2.point_b)

    # mapa n-tice → původní objekt
    point_map = {p1: conn1.point_a, p2: conn1.point_b, p3: conn2.point_a, p4: conn2.point_b}

    # speciální případ: jedna z nich je tečka
    if overlaps_nd(conn1, conn2, get_coords):
        if (p1 == p2) and (p3 != p4):
            return conn2
        elif (p1 != p2) and (p3 == p4):
            return conn1

    # speciální případ: různé dashed
    if conn1.dashed != conn2.dashed:
        if overlaps_nd(conn1, conn2, get_coords):
            d1 = distance_nd(p1, p2)
            d2 = distance_nd(p3, p4)

            if d1 > d2:
                # najdi společné body
                remaining_points = [pt for pt in [p1, p2] if pt not in [p3, p4]] + \
                                   [pt for pt in [p3, p4] if pt not in [p1, p2]]
                if len(remaining_points) == 2:
                    conn1.point_a = point_map[remaining_points[0]]
                    conn1.point_b = point_map[remaining_points[1]]
                return conn2, conn1
            elif d1 < d2:
                return conn2
            else:
                return None
        else:
            return None

    # klasické sloučení
    points = [conn1.point_a, conn1.point_b, conn2.point_a, conn2.point_b]
    coords = [get_coords(p) for p in points]

    if not are_colinear_nd(*coords):
        return None

    # najdi dva nejvzdálenější body
    max_dist = -1
    max_pair = None
    for i in range(4):
        for j in range(i + 1, 4):
            dist = distance_nd(coords[i], coords[j])
            if dist > max_dist:
                max_dist = dist
                max_pair = (points[i], points[j])

    return ConnectionClass(max_pair[0], max_pair[1], dashed=conn1.dashed)


def merge_all(connections, merge_fn):
    """
    Projde seznam spojení a opakovaně je slučuje pomocí merge_fn.
    """
    i = 0
    while i < len(connections):
        j = i + 1
        while j < len(connections):
            merged = merge_fn(connections[i], connections[j])
            if merged:
                connections.pop(j)
                connections.pop(i)

                if isinstance(merged, tuple):
                    connections.extend(merged)
                else:
                    connections.append(merged)

                i = -1  # restart cyklu
                break
            j += 1
        i += 1
    return connections


# ==================================================
# KONKRÉTNÍ 2D / 3D FUNKCE
# ==================================================

def distance_in_2d(a: tuple, b: tuple) -> float:
    return distance_nd(a, b)


def distance_in_3d(a: tuple, b: tuple) -> float:
    return distance_nd(a, b)
