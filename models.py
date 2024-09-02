from sqlalchemy import Column,Integer,String,create_engine
from sqlalchemy.orm import declarative_base,sessionmaker,scoped_session
from sqlalchemy.exc import SQLAlchemyError
from utils import url

Base=declarative_base()

class Expense(Base):
    __tablename__='expenses'
    user_id=Column(Integer,primary_key=True,autoincrement=True,index=True)
    file_name=Column(String,nullable=False)
    
class Database:
    _instance=None
    engine=None
    session=None
    def __new__(cls):
        if cls._instance is None:
            
            cls._instance=super(Database,cls).__new__(cls)
            try:
                cls.engine=create_engine(url)
                cls.session_local=scoped_session(sessionmaker(autoflush=False,bind=cls.engine))
                Base.metadata.create_all(bind=cls.engine)
            except SQLAlchemyError:
                cls._instance=None
                
                
        return cls._instance
    
    def getdb(self):
        db=self.session_local()
        try:
            yield db
        
        finally:
            db.close() 
        
