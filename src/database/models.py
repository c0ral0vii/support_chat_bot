from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Numeric, String, Text, func, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from enum import Enum
from sqlalchemy import Enum as SqlEnum


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class UserCategory(str, Enum):
    EXECUTIVE_DIRECTOR = "executive_director"
    ACCOUNT_MANAGER = "account_manager"
    SENIOR_CLO_MANAGER = "senior_clo_manager"
    CLO_MANAGER = "clo_manager"


class RequestCategory(str, Enum):
    ORDER = "order"
    PAYMENT = "payment"
    ACCOUNT = "account"
    OTHER = "other"


class RequestSubCategory(str, Enum):
    RESET_NP_AND_CHANGE_PAYER = "Заявка на обнуление НП и смену плательщика"
    CREATE_INVOICE_OR_REQUEST = "Создание накладной/заявки"
    CHANGE_RECIPIENT_CONTACTS = "Смена контактных данных получателя"
    CHANGE_DELIVERY_MODE_OR_PICKUP = "Смена режима доставки, смена ПВЗ"
    ORDER_FORWARDING = "Пересыл заказа"
    CARGO_SEARCH = "Поиск груза"
    CONSULTATION_ON_TS_AND_DELIVERY = "Консультация по ТС и срокам доставки"
    PROVIDE_DOCUMENTS = "Предоставление документов, подтверждающих доставку/отправку"
    CUSTOM_SUBCATEGORY = "Свой вариант подкатегории запроса"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)

    requests: Mapped["Request"] = relationship("Requests", back_populates="user")


class Manager(Base):
    __tablename__ = "managers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    category: Mapped[UserCategory] = mapped_column(SqlEnum(UserCategory, name="category"))


    requests: Mapped["Request"] = relationship("Requests", back_populates="manager")


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"))
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("managers.user_id"))
    category: Mapped[UserCategory] = mapped_column(SqlEnum(RequestCategory, name="category"))
    subcategory: Mapped[UserCategory] = mapped_column(SqlEnum(RequestSubCategory, name="subcategory"), default=RequestSubCategory.CUSTOM_SUBCATEGORY)

    user: Mapped["User"] = relationship("User", back_populates="requests")
    manager: Mapped["Manager"] = relationship("Manager", back_populates="requests")

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="requests")
    ratings: Mapped["Rating"] = relationship("Rating", back_populates="request")


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"))
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("managers.user_id"))
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("requests.id"))
    rating_value: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="ratings")
    request: Mapped["Request"] = relationship("Requests", back_populates="ratings")


class Message(Base):
    __tablename__ = 'messages'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    manager: Mapped[int] = mapped_column(Integer, ForeignKey("managers.id"))

    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("requests.id"))
    message: Mapped[str] = mapped_column(String(length=2500))
