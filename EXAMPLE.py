from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from Bot.db import models



engine = create_engine(
    url='postgresql://postgres:Otu4AT4BtklAc96UGnDr@containers-us-west-46.railway.app:6195/railway',
    echo=True
)

def main():
    models.PostTransport.metadata.create_all(bind=engine)
    models.PostLandscaping.metadata.create_all(bind=engine)
    models.PostGarbage.metadata.create_all(bind=engine)

if __name__ == '__main__':
    main()