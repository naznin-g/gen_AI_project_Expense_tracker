from test.test_main import client
from main import app
from fastapi import status
from router.auth import get_current_user
from database import SessionLocal  
from models import Transactions
from datetime import date
def override_get_current_user():
    return{'id':1,'username':'testuser'}
app.dependency_overrides[get_current_user]=override_get_current_user
def test_transaction():
   db= SessionLocal()
   try:
      db.query(Transactions).filter(Transactions.id==99).delete()
      db.commit()
      transaction=Transactions(
             id=99,
             title='testing',
             amount=1.0,
             type='income',
             category='testing',
             date=date.today(),
             owner_id=1
             )
      db.add(transaction)
      db.commit()
   finally:
      db.close()


# Get transaction test
def test_get_transactions():
   response=client.get('/transactions')
   assert response.status_code==status.HTTP_200_OK

# Get specific transaction test
def test_get_specific_transactions():
   test_transaction()
   response=client.get('/transaction/99')
   assert response.status_code==status.HTTP_200_OK


  
#Create transaction test
def test_create_transactions():
   request_data = {
        "title": "grocery",
        "amount": 50.0,
        "type": "income",
        "category": "food"
    }
      

   response=client.post('/transactions',json=request_data)
   assert response.status_code==status.HTTP_201_CREATED
   #assert response.json()== {'message':'Transaction created successfully'}


   
#Update transaction test

def test_update_transaction():
    test_transaction()
    
    update_data = {
        "title": "Updated Title",
        "category": "Bonus",
        
    }
    
    response = client.put("/transactions/99", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    #assert response.json()== {'message':'Transaction updated successfully'}

   
#Delete transaction test

def test_delete_transaction():
    test_transaction()
    
    response = client.delete("/transactions/99")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()== {'message':'Transaction deleted successfully'}
    response_get = client.get("/transaction/99")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND
    
    
    


