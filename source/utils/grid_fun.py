# -*- coding: utf-8 -*-
"""
grid_fun.py
----------
Sjednocené funkce pro práci s gridy (2D i 3D) v Cubiq🧊.

Obsahuje:
    - kontrolu kolinearity a překrývání úseček
    - slučování kolineárních úseček
    - ověřování řešení (2D i 3D)
    - mazání a změnu typu spojení (dashed/plná)
"""

import math

from utils.grid_math import merge_all, merge_segments_nd, distance_to_line


# ==================================================
# ŘEŠENÍ A KONTROLA
# ==================================================

def check_3d_solution(user_connections, solutions):
    """Ověří, zda uživatelská spojení odpovídají alespoň jednomu řešení 3D úlohy."""

    def merge_to_set(connections):
        return set(merge_all(connections,
                             lambda a, b: merge_segments_nd(a, b, lambda p: (p.col, p.row, p.lay), type(a))))

    user_set = merge_to_set(user_connections)

    for solution in solutions:
        sol_set = merge_to_set(solution)
        if user_set == sol_set:
            return True
    return False


def check_2d_solution(user_connections, solution_connections):
    """Ověří, zda uživatelská spojení odpovídají řešení 2D úlohy."""

    def merge_to_set(connections):
        return set(merge_all(connections,
                             lambda a, b: merge_segments_nd(a, b, lambda p: (p.col, p.row), type(a))))

    user_set = merge_to_set(user_connections)
    sol_set = merge_to_set(solution_connections)

    if user_set == sol_set:
        return True
    else:
        return False


# ==================================================
# MAZÁNÍ A PŘEPÍNÁNÍ DASHED (společné pro 2D i 3D)
# ==================================================

def delete_connection(connections, mouse_pos, max_dist=6):
    """
    Smaže spojení, pokud je kurzor blízko čáry.

    Args:
        connections (list): seznam spojení (2D nebo 3D)
        mouse_pos (tuple[int,int]): pozice kurzoru
        max_dist (float): vzdálenost tolerance kliknutí
    """
    nearest_connection = None
    nearest_distance = max_dist

    for conn in connections:
        dist = distance_to_line(mouse_pos, (conn.point_a.x, conn.point_a.y), (conn.point_b.x, conn.point_b.y))
        if dist < nearest_distance:
            nearest_distance = dist
            nearest_connection = conn

    if nearest_connection:
        connections.remove(nearest_connection)


def change_dashed_of_connection(connections, mouse_pos, max_dist=6):
    """
    Přepne dashed/plnou čáru u spojení, které je kurzoru nejbližší.

    Args:
        connections (list): seznam spojení (2D nebo 3D)
        mouse_pos (tuple[int,int]): pozice kurzoru
        max_dist (float): maximální vzdálenost pro aktivaci
    """
    nearest_connection = None
    nearest_distance = max_dist

    for conn in connections:
        dist = distance_to_line(mouse_pos, (conn.point_a.x, conn.point_a.y), (conn.point_b.x, conn.point_b.y))
        if dist < nearest_distance:
            nearest_distance = dist
            nearest_connection = conn

    if nearest_connection:
        nearest_connection.dashed = not nearest_connection.dashed


def merge_if_double_connections_2d(connections):
    return merge_all(connections,
                     lambda a, b: merge_segments_nd(a, b, lambda p: (p.col, p.row), type(a)))


def merge_if_double_connections_3d(connections):
    return merge_all(connections,
                     lambda a, b: merge_segments_nd(a, b, lambda p: (p.col, p.row, p.lay), type(a)))
