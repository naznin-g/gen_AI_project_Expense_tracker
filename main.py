from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
import models
from models import Transactions
from datetime import date 
from database import engine, SessionLocal
from fastapi.responses import JSONResponse
from typing import Optional, Annotated, Literal
from router import auth
from fastapi import status
from router.auth import get_current_user
app=FastAPI()
class Transaction(BaseModel):
    
    title: str
    amount: float=Field(gt=0)
    type: Literal["income","expense"]
    category: str
    
class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(default=None)
    amount: Optional[float] = Field(gt=0, default=None)
    type: Optional[Literal["income","expense"]] = Field(default=None)
    category: Optional[str] = Field(default=None)
    
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router, prefix="/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


#2.Get All Transactions
@app.get('/transactions')
def read_transaction(user: user_dependency, db : db_dependency):

    if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')
    
    return db.query(Transactions).filter(Transactions.owner_id == user.get('id')).all()

#3. Get Transaction By ID
@app.get('/transaction/{transaction_id}')
def read_specific_transaction(user: user_dependency, db:db_dependency,transaction_id:int):
   if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')
   specific_transaction=db.query(Transactions).filter(Transactions.id==transaction_id, 
         Transactions.owner_id == user.get('id')).first()
   if specific_transaction is not None:
       return specific_transaction
   else:
       raise HTTPException(status_code=404, detail='Transaction not found')
#status_code=status.HTTP_201_CREATED
# 1.Create Transaction
@app.post('/transactions',status_code=status.HTTP_201_CREATED)
def create_transactions(user: user_dependency, db : db_dependency, new_transaction : Transaction):

    if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')
    
    created_transaction = Transactions(**new_transaction.model_dump(), owner_id = user.get('id'),
                                     date=date.today())
    db.add(created_transaction)
    db.commit()
    db.refresh(created_transaction)
    
    

    return(created_transaction) 
    
    


# 4. Update Transaction
@app.put('/transactions/{transaction_id}')
def update_transaction(user: user_dependency, db : db_dependency, transaction_id : int, update_transaction : TransactionUpdate):

    if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')
    updated_transaction = db.query(Transactions).filter(
    Transactions.owner_id == user.get('id'),
    Transactions.id == transaction_id).first()
    
    if updated_transaction is  None:
        raise HTTPException(status_code=404, detail='Transaction not found')
    
    update_data = update_transaction.model_dump(exclude_unset=True)

    for key,value in update_data.items():
        setattr(updated_transaction,key,value)
    
    db.commit()
    db.refresh(updated_transaction)
    return updated_transaction
    #return JSONResponse(status_code=200, content={'message' : 'Transaction updated successfully'})

# 5.Delete transaction
@app.delete('/transactions/{transaction_id}')
def delete_transaction(user: user_dependency, db : db_dependency, transaction_id : int):

    if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')

    transaction = db.query(Transactions).filter(Transactions.owner_id == user.get('id'),
                                                Transactions.id == transaction_id).first()
    if transaction is  None:
        raise HTTPException(status_code=404, detail='Transaction not found')
    
    db.delete(transaction)
    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'Transaction deleted successfully'})

#Transaction Filtering 
@app.get('/transactions/filter')
def filter_transactions(user:user_dependency, db:db_dependency, 
                type:Optional[Literal["income","expense"]]=None, 
                category:Optional[str]=None,
                minimum_amount: Optional[float] = None,
                maximum_amount: Optional[float] = None,
    ):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')
    query=db.query(Transactions).filter(Transactions.owner_id==user.get('id'))

    if type is not None:
        query=query.filter(Transactions.type==type)
    if category is not None:
        query=query.filter(Transactions.category.ilike(f"%{category}%"))
    return query.all()

