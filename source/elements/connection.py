# -*- coding: utf-8 -*-
"""
connections.py
--------------

Třída Connection a její potomci pro spojení v 2D a 3D gridu.
"""


class Connection:
    """
    Jednoduchá třída pro reprezentaci spojení mezi dvěma body mřížky.
    """

    def __init__(self, point_a, point_b, dashed=False):
        self.point_a = point_a
        self.point_b = point_b
        self.dashed = dashed  # True = čárkovaná čára, False = plná čára (výchozí)

    def _get_coords(self, point):
        """
        Vrací unikátní identifikátor bodu pro porovnání a hash.
        V základní třídě jen vrací point.
        """
        return point

    def connects(self, a, b) -> bool:
        """Vrátí True, pokud tato čára spojuje body a–b (nezáleží na pořadí)."""
        return {self._get_coords(self.point_a), self._get_coords(self.point_b)} == {
            self._get_coords(a), self._get_coords(b)
        }

    def as_tuple(self):
        """
        Vrátí dvojici bodů jako frozenset (col,row[,lay]) pro porovnání a hash.
        Pořadí bodů nezáleží.
        """
        a = self._get_coords(self.point_a)
        b = self._get_coords(self.point_b)
        return frozenset([a, b])

    def make_data_connection_for_json(self):
        """
        vrátí conn ve formátu: [[a1, a2, ...], [b1, b2, ...], d], kde d nabývá 0 nebo 1 (nečárkovaná/čárkovaná)
        """
        if self.dashed:
            dashed = 1
        else:
            dashed = 0
        return [list(self._get_coords(self.point_a)), list(self._get_coords(self.point_b)), dashed]


    def __eq__(self, other):
        if not isinstance(other, Connection):
            return False
        return self.as_tuple() == other.as_tuple() and self.dashed == other.dashed

    def __hash__(self):
        return hash((self.as_tuple(), self.dashed))

    def __repr__(self):
        return f"[{self.point_a}, {self.point_b}, dashed={self.dashed}]"


class Connection3D(Connection):
    """
    Spojení dvou bodů v 3D mřížce.
    """

    def _get_coords(self, point):
        """
        Vrací jen (col, row, lay), aby porovnání fungovalo nezávisle na x/y.
        """
        # vždy tuple col,row,lay
        return (point.col, point.row, point.lay)


class Connection2D(Connection):
    """
    Spojení dvou bodů v 2D mřížce.
    """

    def _get_coords(self, point):
        """
        Vrací jen (col, row), aby porovnání fungovalo nezávisle na x/y.
        """
        return (point.col, point.row)
