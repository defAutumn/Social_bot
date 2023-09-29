from sqlalchemy import ForeignKey, create_engine
from Bot.db import models
import config


engine = create_engine(
    url=config.postgres_url,
    echo=True
)


def main():
    models.PostTransport.metadata.create_all(bind=engine)
    models.PostLandscaping.metadata.create_all(bind=engine)
    models.PostGarbage.metadata.create_all(bind=engine)


if __name__ == '__main__':
    main()
