from email.policy import default

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Numeric, String, Text, func, Integer, BigInteger
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
    ORDER = "Вопрос по заявке/заказу"
    PAYMENT = "Вопрос по взаиморасчётам"
    ACCOUNT = "Вопрос по личному кабинету"
    OTHER = "Другое"


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
    ERROR_REQUEST = "Ошибочный запрос, клиент относится к другому юр. лицу"

    NOT_SETUP = "Не установлено / Заказ не закрыт"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str] = mapped_column(String)
    number: Mapped[str] = mapped_column(nullable=True)

    requests: Mapped[list["Request"]] = relationship("Request", back_populates="user")


class Manager(Base):
    __tablename__ = "managers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    field: Mapped[str] = mapped_column(String(150), nullable=True)
    name: Mapped[str] = mapped_column(String, index=True)
    surname: Mapped[str] = mapped_column(String, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    category: Mapped[UserCategory] = mapped_column(SqlEnum(UserCategory, name="category"), nullable=False)
    free: Mapped[bool] = mapped_column(Boolean, default=True)

    vacation_start: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    vacation_end: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    number: Mapped[str] = mapped_column(String, nullable=True)

    requests: Mapped[list["Request"]] = relationship("Request", back_populates="manager")


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    manager_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("managers.user_id"), nullable=True)
    request_category: Mapped[RequestCategory] = mapped_column(SqlEnum(RequestCategory, name="request_category"))
    subcategory: Mapped[RequestSubCategory] = mapped_column(SqlEnum(RequestSubCategory, name="subcategory"),
                                                            default=RequestSubCategory.NOT_SETUP)

    manager_closed: Mapped[int] = mapped_column(BigInteger, nullable=True)

    close: Mapped[bool] = mapped_column(Boolean, default=False)
    contact_number_or_inn: Mapped[str] = mapped_column(String, nullable=True)


    user: Mapped["User"] = relationship("User", back_populates="requests")
    manager: Mapped["Manager"] = relationship("Manager", back_populates="requests")

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="request")
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="request")


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("requests.id"))
    rating_value: Mapped[int] = mapped_column(Integer, nullable=False)

    request: Mapped["Request"] = relationship("Request", back_populates="ratings")


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    from_: Mapped[int] = mapped_column(BigInteger, nullable=False)

    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("requests.id"))
    message: Mapped[str] = mapped_column(String(length=2500))

    request: Mapped["Request"] = relationship("Request", back_populates="messages")