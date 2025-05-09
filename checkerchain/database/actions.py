from sqlalchemy import select, delete, update
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from checkerchain.database.model import Product, MinerPrediction
from .utils import with_db_session
import typing as ty


@with_db_session
def get_products(session: Session) -> ty.List[Product]:
    return session.query(Product).all()


@with_db_session
def get_unreviewed_products(session: Session):
    return session.query(Product).filter(Product.check_chain_review_done == False).all()


@with_db_session
def get_product(session: Session, **kwargs):
    return session.query(Product).filter_by(**kwargs).first()


@with_db_session
def add_product(
    session: Session,
    _id,
    name,
    trust_score=0.0,
    check_chain_review_done=False,
    mining_done=False,
    rewards_distributed=False,
):
    product = Product(
        _id=_id,
        name=name,
        trust_score=trust_score,
        check_chain_review_done=check_chain_review_done,
        mining_done=mining_done,
        rewards_distributed=rewards_distributed,
    )
    session.add(product)
    session.commit()


@with_db_session
def remove_product(session: Session, _id):
    session.execute(delete(Product).where(Product._id == _id))
    session.commit()


@with_db_session
def add_prediction(session: Session, product_id, miner_id, prediction):
    ups_stmt = sqlite_upsert(MinerPrediction).values(
        product_id=product_id,
        miner_id=int(miner_id),
        prediction=float(prediction),
    )
    query = ups_stmt.on_conflict_do_update(
        index_elements=[
            "product_id",
            "miner_id",
        ],
        set_=dict(
            miner_id=ups_stmt.excluded.miner_id, prediction=ups_stmt.excluded.prediction
        ),
    )
    session.execute(query)
    session.commit()


@with_db_session
def remove_prediction(session: Session, prediction_id):
    session.execute(delete(MinerPrediction).where(MinerPrediction.id == prediction_id))
    session.commit()


@with_db_session
def update_product_status(session: Session, _id, **kwargs):
    session.execute(update(Product).where(Product._id == _id).values(**kwargs))
    session.commit()


@with_db_session
def get_predictions_for_product(session: Session, product_id):
    return session.query(MinerPrediction).filter_by(product_id=product_id).all()


@with_db_session
def delete_a_product(session: Session, product_id):
    session.execute(
        delete(MinerPrediction).where(MinerPrediction.product_id == product_id)
    )
    session.execute(delete(Product).where(Product._id == product_id))
    session.commit()


@with_db_session
def db_get_unreviewd_products(session: Session):
    return session.query(Product).filter(Product.check_chain_review_done == False).all()
