from aiogram.fsm.state import StatesGroup, State


class SetLanguage(StatesGroup):
    ChooseLanguage = State()


class CreateOrder(StatesGroup):
    WriteName = State()
    WritePhoneManager = State()
    WritePhoneReceiver = State()
    WriteAddress = State()
    ChooseBodyType = State()
    WriteDescription = State()
    WriteWeight = State()
    WritePallets = State()
    WriteDeliveryTimeDate = State()
    WriteDeliveryTimeHours = State()
    WriteComment = State()
    FormConfirmation = State()
