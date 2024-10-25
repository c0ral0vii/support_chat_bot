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