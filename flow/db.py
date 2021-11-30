from sqlmodel import Session, SQLModel, create_engine

from flow.models import PostDB


class Storage:
    def __init__(self, db_path: str) -> None:
        self.engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(self.engine)

    def add_post(self, id: int):
        with Session(self.engine) as session:
            post = PostDB(id=id)
            session.add(post)
            session.commit()

    def post_in_db(self, id: int):
        with Session(self.engine) as session:
            return bool(session.get(PostDB, id))
