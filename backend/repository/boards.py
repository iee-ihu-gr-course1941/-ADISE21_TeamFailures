from uuid import UUID, uuid4
from pydantic.networks import HttpUrl
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import Null, and_, or_
from sqlalchemy.sql.functions import mode
from sqlalchemy.sql.operators import isnot
from backend import schemas, models, database
from fastapi import HTTPException, status
from sqlalchemy.sql.expression import asc, desc, false, func
from typing import List
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
    # models.Boards.players.name. !=None).first()

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
            detail=f"Board with id {id} was not found",
        )
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
    checkWin(board_model)
    json_board = jsonable_encoder(board.first())
    return JSONResponse(content=json_board)


def checkWin(board):
    Win = False
    how = ''
    # check Rows
    try:
        for x in range(4):
            if board.board[x][0][0] == board.board[x][1][0] == board.board[x][2][0] == board.board[x][3][0]:
                Win = True
                how = ' Win by row'
    except:
        pass

    # # check Collumns
    try:
        for x in range(4):
            if board.board[0][x][0] == board.board[1][x][0] == board.board[2][x][0] == board.board[3][x][0]:
                Win = True
                how = 'Win by column'
    except:
        pass
    # # check Crosss1
    try:
        if board.board[0][0][0] == board.board[1][1][0] == board.board[2][2][0] == board.board[3][3][0]:
            Win = True
            how = 'Win by cross'
    except:
        pass
    # # check Cross2
    try:
        if board.board[3][0][0] == board.board[2][1][0] == board.board[1][2][0] == board.board[0][3][0]:
            Win = True
            how = 'Win by cross'
    except:
        pass
