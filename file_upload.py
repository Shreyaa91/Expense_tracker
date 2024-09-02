from fastapi import UploadFile,APIRouter,Depends,HTTPException
from models import Database,Expense
from sqlalchemy.orm import Session
import os,csv
from datetime import datetime
from io import StringIO
from fastapi.responses import JSONResponse
from schemas import Validate

rout=APIRouter()
final_path=f'{os.getcwd()}/temp'

@rout.post('/create/expense/file')
def create_file(use:Validate,user_id:int,File_name:str,db:Session=Depends(Database().getdb)):
    check=db.query(Expense).filter(Expense.user_id==user_id).first()
    # if check:
    #     raise HTTPException(status_code=409,detail='user id exists')
    header=[field for field in Validate.__annotations__.keys()]
    exist=os.path.isfile(f"{final_path}/{user_id}{File_name}.csv")
    with open(f"{final_path}/{user_id}{File_name}.csv",mode='a',newline='') as f:
        writer=csv.writer(f)
        if not exist:
            writer.writerow(header)
        writer.writerow([
                        use.id,
                        use.date.strftime("%Y-%m-%d"),
                        use.amount,
                        use.description,
                        use.category])
        if not check:

            db.add(Expense(user_id=user_id,file_name=File_name))
            db.commit()
        return "Record added"
        
    
# @rout.post('/upload/expense/file')
# async def upload_file(id:int,upload:UploadFile,db:Session=Depends(Database().getdb)):
#     if not upload.filename.endswith('.csv'):
#         raise HTTPException(status_code=400,detail='Invalid file format')
#     with open(f"{final_path}/{id}{upload.filename}","wb") as f:
#         f.write(await upload.read())
#         value=Expense(user_id=id,file_name=upload.filename)
#         check=db.query(Expense).filter(Expense.user_id==id,Expense.file_name==upload.filename).first()
#         if not check:
#             db.add(value)
#             db.commit()
#             return "file added"
#         raise HTTPException(status_code=409,detail='File with same name exists')
        
  
@rout.get('/get/expense_file')
def get_expense(user_id:int,db:Session=Depends(Database().getdb)):
    check=db.query(Expense).filter(Expense.user_id==user_id).first()
    if not check:
        raise HTTPException(status_code=404,detail='User id does not exist')
    if not os.path.exists(f"{final_path}/{user_id}{check.file_name}.csv"):
        raise HTTPException(status_code=404,detail='File not found')
    with open(f"{final_path}/{user_id}{check.file_name}.csv",mode='r') as f:
        data=f.read()
        return JSONResponse(content={"File":data})


# @rout.put('/modify/file')
# async def update_file(id:int,upload:UploadFile,db:Session=Depends(Database().getdb)):
#     check=db.query(Expense).filter(Expense.user_id==id).first()
#     if not check:
#         raise HTTPException(status_code=404,detail='No such entry found')
#     if not os.path.exists(f"{final_path}/{id}{check.file_name}"):
#         raise HTTPException(status_code=404,detail='File not found')
#     with open(f"{final_path}/{id}{check.file_name}",mode='wb') as f:
#         f.write(await upload.read())
#         db.commit()
#         return "File updated"

@rout.put('/modify/file')
def update_field(user_id:int,use:Validate,db:Session=Depends(Database().getdb)):
    check=db.query(Expense).filter(Expense.user_id==user_id).first()
    if not check:
        raise HTTPException(status_code=404,detail='User id not found')
    with open(f"{final_path}/{user_id}{check.file_name}.csv",mode='r',newline='') as f:
        reader=csv.reader(f)
        headers=next(reader)
        found=0
        rows=[row for row in reader]
        for row in rows:
            if int(row[0])==use.id:
                row[1] = use.date.strftime('%Y-%m-%d')  # Update date
                row[2] = use.amount  # Update amount
                row[3] = use.description or ''  # Update description
                row[4] = use.category  # Update category
                found=1
                break
        if not found:
            raise HTTPException(status_code=404,detail='Record not found')
        with open(f"{final_path}/{user_id}{check.file_name}.csv",mode='w',newline='') as f:
            writer=csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            return "Record updated"
                
    
@rout.delete('/delete/record')
def delete_record(user_id:int,id:int,db:Session=Depends(Database().getdb)):
    check=db.query(Expense).filter(Expense.user_id==user_id).first()
    if not check:
        raise HTTPException(status_code=404,detail='User id not found')
    with open(f"{final_path}/{user_id}{check.file_name}.csv",mode='r',newline='') as f:
        reader=csv.reader(f)
        header=next(reader)
        rows=[]
        exists=False
        for row in reader:
            if row[0]==str(id):
                exists=True
            else:
                rows.append(row)
    if not exists:
        raise HTTPException(status_code=404,detail='Given record not found')
    with open(f"{final_path}/{user_id}{check.file_name}.csv",mode='w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    return {"message":"Record deleted"}
    
@rout.delete('/delete/file')
def delete_file(id:int,db:Session=Depends(Database().getdb)):
    check=db.query(Expense).filter(Expense.user_id==id).first()
    if not check:
        raise HTTPException(status_code=404,detail='user id not found')
    
    if not os.path.exists(f"{final_path}/{id}{check.file_name}.csv"):
        raise HTTPException(status_code=404,detail='file not present in the directory')
    os.remove(f"{final_path}/{id}{check.file_name}.csv")
    db.delete(check)
    db.commit()
    
    return {"message":"file deleted"}
            
            
            
        
    