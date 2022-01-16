from uuid import UUID, uuid4
from pydantic.networks import HttpUrl
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.session import Session

from sqlalchemy.sql.functions import mode
from sqlalchemy.sql.operators import isnot
from backend import schemas, models, database
from fastapi import HTTPException, status


from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def create_board(request: schemas.Boards, db: Session):
    new_board = models.Boards(
        id=uuid4(),
        creator_id=request.creator_id,
        players=request.players,
        board=[[None, None, None, None],
               [None, None, None, None],
               [None, None, None, None],
               [None, None, None, None]],
        active_player=request.active_player,
        isFull=False,
        status="active"
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    json_board = jsonable_encoder(new_board)
    return JSONResponse(content=json_board)


def get_random_board(db: Session):
    # find a board with 1 player already inside
    board = db.query(models.Boards).filter(
        models.Boards.isFull == False).first()

    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There are no boards with 1 player",
        )
    json_board = jsonable_encoder(board)
    return json_board


def destroy(id: UUID, db: Session):
    board = db.query(models.Boards).filter(models.Boards.id == id)
    if not board.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with id {id} not found",
        )
    board.delete(synchronize_session=False)
    db.commit()
    return "done"


def get_boards(db: Session):
    boards = db.query(models.Boards).all()
    if not boards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"There are no boards"
        )
    return boards


def get_board(id: UUID, db: Session):
    board = db.query(models.Boards).filter(models.Boards.id == id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with the Uuid {id} is not available",
        )
    return board

# update Functions


def update_board_attributes(request, board, board_model):
    dimension = []
    if request.board:
        for index1, array in enumerate(request.board):
            for index2, item in enumerate(array):
                if item is not None and len(item) == 1:
                    dimension = [index1, index2]
        index = board_model.players.index(request.active_player)
        if board_model.board[dimension[0]][dimension[1]] is None:
            request.board[dimension[0]][dimension[1]
                                        ] = f'{index}{request.board[dimension[0]][dimension[1]]}'
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="You can play on this board position")
    for item in request:
        if item[1] is not None:
            board.update({item[0]: item[1]})

    return board


def get_board_length(board):
    length = 0
    for array in board:
        for item in array:
            if item != None:
                length += 1
    return length


def change_active_player(request, board, board_model):
    index = board_model.players.index(request.active_player)
    if index == 0:
        board.update({'active_player': board_model.players[1]})
    else:
        board.update({'active_player': board_model.players[0]})


def update(id: UUID, request: schemas.Boards, db: Session):
    board = db.query(models.Boards).filter(models.Boards.id == id)
    board_model = board.first()
    if not board_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with id {id} was not found or game is finished",
        )
    if board_model.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Game is finished. {board_model.status}. Please delete this board')
    if request.board:
        if request.active_player == board_model.active_player and (get_board_length(request.board)-get_board_length(board_model.board) == 1):
            update_board_attributes(request, board, board_model)
            change_active_player(request, board, board_model)
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail='Its not your turn or you changed more than one board values'
            )
    else:
        update_board_attributes(request, board, board_model)
    if len(board_model.players) == 2:
        board.update({"isFull": True})
    db.commit()
    win, how = checkResult(board_model)
    if win:
        board.update({"status": f'Winner is {request.active_player}'})
        return JSONResponse(content={"detail": "We have a winner", "how": how, "winner": request.active_player})
    else:
        if how == "Draw":
            board.update({"status": 'Game has finished in a draw'})
            return JSONResponse(content={"detail": "Its a draw"})
        else:
            json_board = jsonable_encoder(board.first())
            return JSONResponse(content=json_board)


# Πιονία
# 1 =  tall square hollow-top
# 2 =  tall square solid-top
# 3 =  tall circle hollow-top
# 4 =  tall circle solid-top

# 5 =  short square hollow-top
# 6 =  short square solid-top
# 7 =  short circle hollow-top
# 8 =  short circle solid-top

def checkResult(board):
    Win = False
    how = ''
    tall_piece = ["1", "2", "3", "4"]
    short_piece = ["5", "6", "7", "8"]
    circle_piece = ["3", "4", "7", "8"]
    square_piece = ["1", "2", "5", "6"]
    hollow_top_piece = ["1", "3", "5", "7"]
    solid_top_piece = ["2", "4", "6", "8"]
    # check Rows
    try:
        for x in range(4):
            if board.board[x][0][0] == board.board[x][1][0] == board.board[x][2][0] == board.board[x][3][0]:
                Win = True
                how = ' Win by row by color'
            # Check if the tall piece
            elif (board.board[x][0][1] in tall_piece) and (board.board[x][1][1] in tall_piece) and (board.board[x][2][1] in tall_piece) and (board.board[x][3][1] in tall_piece):
                Win = True
                how = ' Win by row by tall piece'
            # Check short piece
            elif (board.board[x][0][1] in short_piece) and (board.board[x][1][1] in short_piece) and (board.board[x][2][1] in short_piece) and (board.board[x][3][1] in short_piece):
                Win = True
                how = ' Win by row by short piece'
            # Check circle piece
            elif (board.board[x][0][1] in circle_piece) and (board.board[x][1][1] in circle_piece) and (board.board[x][2][1] in circle_piece) and (board.board[x][3][1] in circle_piece):
                Win = True
                how = ' Win by row by circle piece'
            # Check square piece
            elif (board.board[x][0][1] in square_piece) and (board.board[x][1][1] in square_piece) and (board.board[x][2][1] in square_piece) and (board.board[x][3][1] in square_piece):
                Win = True
                how = ' Win by row by square piece'
            # Check hollow top piece
            elif (board.board[x][0][1] in hollow_top_piece) and (board.board[x][1][1] in hollow_top_piece) and (board.board[x][2][1] in hollow_top_piece) and (board.board[x][3][1] in hollow_top_piece):
                Win = True
                how = ' Win by row by hollow top piece'
            # Check solid top piece
            elif (board.board[x][0][1] in solid_top_piece) and (board.board[x][1][1] in solid_top_piece) and (board.board[x][2][1] in solid_top_piece) and (board.board[x][3][1] in solid_top_piece):
                Win = True
                how = ' Win by row by solid top piece'
    except:
        pass

    # # check Collumns
    try:
        for x in range(4):
            if board.board[0][x][0] == board.board[1][x][0] == board.board[2][x][0] == board.board[3][x][0]:
                Win = True
                how = 'Win by column by color'
                # Check if the tall piece
            elif (board.board[0][x][1] in tall_piece) and (board.board[1][x][1] in tall_piece) and (board.board[2][x][1] in tall_piece) and (board.board[3][x][1] in tall_piece):
                Win = True
                how = ' Win by column by tall piece'
                # Check short piece
            elif (board.board[0][x][1] in short_piece) and (board.board[1][x][1] in short_piece) and (board.board[2][x][1] in short_piece) and (board.board[3][x][1] in short_piece):
                Win = True
                how = ' Win by column by short piece'
                # Check circle piece
            elif (board.board[0][x][1] in circle_piece) and (board.board[1][x][1] in circle_piece) and (board.board[2][x][1] in circle_piece) and (board.board[3][x][1] in circle_piece):
                Win = True
                how = ' Win by column by circle piece'
                # Check square piece
            elif (board.board[0][x][1] in square_piece) and (board.board[1][x][1] in square_piece) and (board.board[2][x][1] in square_piece) and (board.board[3][x][1] in square_piece):
                Win = True
                how = ' Win by column by square piece'
                # Check hollow top piece
            elif (board.board[0][x][1] in hollow_top_piece) and (board.board[1][x][1] in hollow_top_piece) and (board.board[2][x][1] in hollow_top_piece) and (board.board[3][x][1] in hollow_top_piece):
                Win = True
                how = ' Win by column by hollow top piece'
                # Check solid top piece
            elif (board.board[0][x][1] in solid_top_piece) and (board.board[1][x][1] in solid_top_piece) and (board.board[2][x][1] in solid_top_piece) and (board.board[3][x][1] in solid_top_piece):
                Win = True
                how = ' Win by column by solid top piece'
    except:
        pass
    # # check Crosss1
    try:
        if board.board[0][0][0] == board.board[1][1][0] == board.board[2][2][0] == board.board[3][3][0]:
            Win = True
            how = 'Win by cross by color'
            # Check if the tall piece
        elif (board.board[0][0][1] in tall_piece) and (board.board[1][1][1] in tall_piece) and (board.board[2][2][1] in tall_piece) and (board.board[3][3][1] in tall_piece):
            Win = True
            how = ' Win by cross by tall piece'
        elif (board.board[0][0][1] in short_piece) and (board.board[1][1][1] in short_piece) and (board.board[2][2][1] in short_piece) and (board.board[3][3][1] in short_piece):
            Win = True
            how = ' Win by cross by short piece'
            # Check circle piece
        elif (board.board[0][0][1] in circle_piece) and (board.board[1][1][1] in circle_piece) and (board.board[2][2][1] in circle_piece) and (board.board[3][3][1] in circle_piece):
            Win = True
            how = ' Win by cross by circle piece'
            # Check square piece
        elif (board.board[0][0][1] in square_piece) and (board.board[1][1][1] in square_piece) and (board.board[2][2][1] in square_piece) and (board.board[3][3][1] in square_piece):
            Win = True
            how = ' Win by cross by square piece'
            # Check hollow top piece
        elif (board.board[0][0][1] in hollow_top_piece) and (board.board[1][1][1] in hollow_top_piece) and (board.board[2][2][1] in hollow_top_piece) and (board.board[3][3][1] in hollow_top_piece):
            Win = True
            how = ' Win by cross by hollow top piece'
            # Check solid top piece
        elif (board.board[0][0][1] in solid_top_piece) and (board.board[1][1][1] in solid_top_piece) and (board.board[2][2][1] in solid_top_piece) and (board.board[3][3][1] in solid_top_piece):
            Win = True
            how = ' Win by cross by solid top piece'
    except:
        pass
    # # check Cross2
    try:
        if board.board[3][0][0] == board.board[2][1][0] == board.board[1][2][0] == board.board[0][3][0]:
            Win = True
            # Check if the tall piece
        elif (board.board[3][0][1] in tall_piece) and (board.board[2][1][1] in tall_piece) and (board.board[1][2][1] in tall_piece) and (board.board[0][3][1] in tall_piece):
            Win = True
            how = ' Win by cross by tall piece'
        elif (board.board[3][0][1] in short_piece) and (board.board[2][1][1] in short_piece) and (board.board[1][2][1] in short_piece) and (board.board[0][3][1] in short_piece):
            Win = True
            how = ' Win by cross by short piece'
            # Check circle piece
        elif (board.board[3][0][1] in circle_piece) and (board.board[2][1][1] in circle_piece) and (board.board[1][2][1] in circle_piece) and (board.board[0][3][1] in circle_piece):
            Win = True
            how = ' Win by cross by circle piece'
            # Check square piece
        elif (board.board[3][0][1] in square_piece) and (board.board[2][1][1] in square_piece) and (board.board[1][2][1] in square_piece) and (board.board[0][3][1] in square_piece):
            Win = True
            how = ' Win by cross by square piece'
            # Check hollow top piece
        elif (board.board[3][0][1] in hollow_top_piece) and (board.board[2][1][1] in hollow_top_piece) and (board.board[1][2][1] in hollow_top_piece) and (board.board[0][3][1] in hollow_top_piece):
            Win = True
            how = ' Win by cross by hollow top piece'
            # Check solid top piece
        elif (board.board[3][0][1] in solid_top_piece) and (board.board[2][1][1] in solid_top_piece) and (board.board[1][2][1] in solid_top_piece) and (board.board[0][3][1] in solid_top_piece):
            Win = True
            how = ' Win by cross by solid top piece'
    except:
        pass
    if Win:
        return Win, how
    elif (not Win) and (get_board_length(board.board) == 16):
        how = 'Draw'
        return Win, how
    else:
        return False, how
