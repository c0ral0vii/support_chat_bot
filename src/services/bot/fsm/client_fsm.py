from aiogram.fsm.state import State, StatesGroup


class ClientForm(StatesGroup):
    contract_number_or_inn = State()
    surname = State()
    organization_name = State()
    phone_number = State()

    texts = {
        'AuthForm:name': 'Введите имя заново:',
        'AuthForm:surname': 'Введите фамилию заново:',
        'AuthForm:organization_name': 'Введите организацию заново:',
        'AuthForm:phone_number': 'Этот стейт последний, поэтому...',
    }


class RequestSend(StatesGroup):
    request = State()
    manager = State()
    client = State()


class VacationForm(StatesGroup):
    from_ = State()
    to_ = State()
    phone = State()

    texts = {
        "VacationForm:from_": "Введите С какого числа у вас отпуск в таком формате: 31.12.2024",
        "VacationForm:to_": "Введите ПО какое число у вас отпуск в таком формате: 31.12.2024",
        "VacationForm:phone": "Введите номер телефона для связи в таком формате, без пробелов: +X XXX XXX XXXX"
    }