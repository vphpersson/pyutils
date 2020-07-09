from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Any, Dict, Set
from enum import Enum, auto
from contextlib import suppress


class Direction(Enum):
    NORTH_WEST = auto()
    NORTH = auto()
    NORTH_EAST = auto()
    EAST = auto()
    SOUTH_EAST = auto()
    SOUTH = auto()
    SOUTH_WEST = auto()
    WEST = auto()


class TileValue(Enum):
    UNOCCUPIED = auto()


@dataclass(frozen=True)
class GridCoordinate:
    row_index: int
    column_index: int


class Grid:
    def __init__(grid_self, size: int):

        grid_self._grid: List[List[Tile]] = []
        grid_self.occupied_tile_coordinate_to_occupied_tile: Dict[GridCoordinate, Tile] = {}

        class Tile:

            def __init__(tile_self, coordinate: GridCoordinate, value: Any = TileValue.UNOCCUPIED):
                tile_self.coordinate = coordinate
                tile_self._value = value

            @property
            def is_occupied(self) -> bool:
                return self._value is not TileValue.UNOCCUPIED

            @property
            def value(tile_self) -> Any:
                return tile_self._value

            @value.setter
            def value(tile_self, set_value: Any):
                if not tile_self.is_occupied:
                    if set_value is TileValue.UNOCCUPIED:
                        return
                    grid_self.occupied_tile_coordinate_to_occupied_tile[tile_self.coordinate] = tile_self
                    tile_self._value = set_value
                else:
                    if set_value is TileValue.UNOCCUPIED:
                        del grid_self.occupied_tile_coordinate_to_occupied_tile[tile_self.coordinate]
                    tile_self._value = set_value

            def clear_value(tile_self) -> None:
                tile_self._value = TileValue.UNOCCUPIED

            def moore_neighborhood(tile_self) -> List[Tuple[Tile, Direction]]:

                tile_direction_pairs = []
                for direction in Direction:
                    with suppress(IndexError):
                        tile_direction_pairs.append((tile_self.get_adjacent(direction=direction), direction))

                return tile_direction_pairs

            def von_neumann_neighborhood(tile_self) -> List[Tuple[Tile, Direction]]:

                tile_direction_pairs = []
                for direction in {Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST}:
                    with suppress(IndexError):
                        tile_direction_pairs.append((tile_self.get_adjacent(direction=direction), direction))

                return tile_direction_pairs

            def get_adjacent(tile_self, direction: Direction, distance: int = 1) -> Tile:
                if direction is Direction.NORTH_WEST:
                    row_index = tile_self.coordinate.row_index - distance
                    column_index = tile_self.coordinate.column_index - distance
                elif direction is Direction.NORTH:
                    row_index = tile_self.coordinate.row_index - distance
                    column_index = tile_self.coordinate.column_index
                elif direction is Direction.NORTH_EAST:
                    row_index = tile_self.coordinate.row_index - distance
                    column_index = tile_self.coordinate.column_index + distance
                elif direction is Direction.EAST:
                    row_index = tile_self.coordinate.row_index
                    column_index = tile_self.coordinate.column_index + distance
                elif direction is Direction.SOUTH_EAST:
                    row_index = tile_self.coordinate.row_index + distance
                    column_index = tile_self.coordinate.column_index + distance
                elif direction is Direction.SOUTH:
                    row_index = tile_self.coordinate.row_index + distance
                    column_index = tile_self.coordinate.column_index
                elif direction is Direction.SOUTH_WEST:
                    row_index = tile_self.coordinate.row_index + distance
                    column_index = tile_self.coordinate.column_index - distance
                elif direction is Direction.WEST:
                    row_index = tile_self.coordinate.row_index
                    column_index = tile_self.coordinate.column_index - distance
                else:
                    raise ValueError('Not a direction')

                if row_index < 0 or column_index < 0:
                    raise IndexError('Negative index')

                return grid_self._grid[row_index][column_index]

        for row_index in range(size):
            row: List[Tile] = []
            for column_index in range(size):
                row.append(Tile(coordinate=GridCoordinate(row_index=row_index, column_index=column_index)))

            grid_self._grid.append(row)

    def pre_frontier_moore(self):
        return tuple(
            occupied_tile
            for occupied_tile in self.occupied_tile_coordinate_to_occupied_tile.values()
            for neighbor_tile, _ in occupied_tile.moore_neighborhood()
            if not neighbor_tile.is_occupied
        )

    def frontier_moore(self):
        frontier_coordinates: Set[GridCoordinate] = set(
            neighbor_tile.coordinate
            for occupied_tile in self.occupied_tile_coordinate_to_occupied_tile.values()
            for neighbor_tile, _ in occupied_tile.moore_neighborhood()
            if not neighbor_tile.is_occupied
        )

        return tuple(self.get_coordinate_tile(coordinate=coordinate) for coordinate in frontier_coordinates)

    def pre_frontier_von_neumann(self):
        return tuple(
            occupied_tile
            for occupied_tile in self.occupied_tile_coordinate_to_occupied_tile.values()
            for neighbor_tile, _ in occupied_tile.von_neumann_neighborhood()
            if not neighbor_tile.is_occupied
        )

    def frontier_von_neumann(self):
        frontier_coordinates: Set[GridCoordinate] = set(
            neighbor_tile.coordinate
            for occupied_tile in self.occupied_tile_coordinate_to_occupied_tile.values()
            for neighbor_tile, _ in occupied_tile.von_neumann_neighborhood()
            if not neighbor_tile.is_occupied
        )

        return tuple(self.get_coordinate_tile(coordinate=coordinate) for coordinate in frontier_coordinates)

    def get_tile(self, row_index: int, column_index: int) -> 'Tile':
        return self._grid[row_index][column_index]

    def get_coordinate_tile(self, coordinate: GridCoordinate) -> 'Tile':
        return self.get_tile(row_index=coordinate.row_index, column_index=coordinate.column_index)

    def get_value(self, row_index: int, column_index: int) -> Any:
        return self.get_tile(row_index=row_index, column_index=column_index).value

    def get_coordinate_value(self, coordinate: GridCoordinate) -> Any:
        return self.get_value(row_index=coordinate.row_index, column_index=coordinate.column_index)

    def set_value(self, row_index: int, column_index: int, value: Any) -> None:
        self.get_tile(row_index=row_index, column_index=column_index).value = value

    def set_coordinate_value(self, coordinate: GridCoordinate, value: Any) -> None:
        self.set_value(row_index=coordinate.row_index, column_index=coordinate.column_index, value=value)

    def clear_value(self, row_index: int, column_index: int) -> None:
        self.get_tile(row_index=row_index, column_index=column_index).clear_value()

    def clear_coordinate_value(self, coordinate: GridCoordinate) -> None:
        self.get_tile(row_index=coordinate.row_index, column_index=coordinate.column_index).clear_value()

    @property
    def size(self) -> int:
        return len(self._grid)

    def __iter__(self):
        return (tile for row in self._grid for tile in row)
