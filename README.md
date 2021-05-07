# pyutils

A collections of various useful utilities.

## CLI showcase

### make_dataclass.py

#### Usage

```
$ ./make_dataclass.py --help

usage: make_dataclass.py [-h] [--class-name CLASS_NAME] [input_file]

Turn a JSON object into a Python `dataclass` definition.

positional arguments:
  input_file            A file from which to read a JSON object (default: <_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>)

optional arguments:
  -h, --help            show this help message and exit
  --class-name CLASS_NAME
                        The name of the dataclass to be produced. (default: A)
```

#### Example

```
$ ./make_dataclass.py data.json --class-name 'GameInfo'
```

data.json

```javascript
{
  "name": "Live Chess",
  "gameId": 13026220933,
  "startDate": 1619287458,
  "player1Name": "virrevvv",
  "player2Name": "kattsaros",
  "timeControl": "600",
  "tcnMoves": "mC0Kbs5QfH9ziq",
  "moveTimestamps": "5998,5970,5975,5864,5908,5789,5806,5369",
  "initialSetup": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "variant": "Standard Chess",
  "player1ResultID": 1,
  "player2ResultID": 6,
  "round": "-",
  "firstMovePly": 1,
  "variantId": 1,
  "whiteRating": 982,
  "blackRating": 779,
  "endTime": "11:04:18 PDT"
}
```

Output:

```python
@dataclass
class GameInfo:
    name: str
    game_id: int
    start_date: int
    player1_name: str
    player2_name: str
    time_control: str
    tcn_moves: str
    move_timestamps: str
    initial_setup: str
    variant: str
    player1_result_id: int
    player2_result_id: int
    round: str
    first_move_ply: int
    variant_id: int
    white_rating: int
    black_rating: int
    end_time: str
```

:thumbsup:
