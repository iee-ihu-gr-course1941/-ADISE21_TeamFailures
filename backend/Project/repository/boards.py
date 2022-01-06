from sqlalchemy.orm.session import Session
from sqlalchemy.sql.functions import mode
from fastapi import HTTPException,status
from sqlalchemy.sql.expression import func
from typing import List
from fastapi import APIRouter,Depends
from .. import schemas,models

def create_board(request:schemas.Boards,db:Session):
    new_board=models.Board(
    id = db.query(func.max(models.Board.id)).scalar()+1,
    creator_id=request.creator_id)
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return request

def get_boards(db:Session):
    boards=db.query(models.Board).all()
    if not boards:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'There are no boards stored')
    return boards

def get_board(id:int,db:Session):
    board=db.query(models.Board).filter(models.Board.id==id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Board with id {id} was not found')
    return board