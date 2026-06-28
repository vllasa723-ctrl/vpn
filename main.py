import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import google.generativeai as genai

TOKEN = "8746891105:AAHToDt57KKDRjN5amJT8160cOHZdvkbKoI"
genai.configure(api_key="AQ.Ab8RN6KuCwM0uL6IHWKOo1Bq3ckcPQxyIpyaSW2lB1qU64cHwQ")

bot = Bot(token=TOKEN)
dp = Dispatcher()

SYS_PROMPT = "Вы — альтернативная платформа character.ai, но с доступным NSFW."
MODEL_NAME = "models/gemma-4-31b-it"

class ChatState(StatesGroup):
    waiting = State()
    chatting = State()

histories = {}
last_msgs = {}

async def is_group(message: types.Message):
    return message.chat.type in ["group", "supergroup"]

@dp.message(Command("start", "clear"))
async def start_cmd(message: types.Message, state: FSMContext):
    if not await is_group(message):
        return
    key = f"{message.chat.id}_{message.from_user.id}"
    histories[key] = []
    last_msgs[key] = []
    await state.set_state(ChatState.waiting)

@dp.message(Command("regenerate"))
async def regenerate_cmd(message: types.Message, state: FSMContext):
    if not await is_group(message):
        return
    try:
        await message.delete()
    except:
        pass
    
    key = f"{message.chat.id}_{message.from_user.id}"
    h = histories.get(key, [])
    lm = last_msgs.get(key, [])
    
    if len(h) >= 2 and len(lm) >= 2:
        u_msg, b_msg = lm[-2], lm[-1]
        try:
            await bot.delete_message(message.chat.id, u_msg)
            await bot.delete_message(message.chat.id, b_msg)
        except:
            pass
            
        user_text = h[-2]["parts"][0]
        histories[key] = h[:-2]
        last_msgs[key] = lm[:-2]
        await process_chat(message.chat.id, message.from_user.id, user_text, u_msg)

@dp.message(ChatState.waiting, F.text)
async def set_char(message: types.Message, state: FSMContext):
    if not await is_group(message):
        return
    key = f"{message.chat.id}_{message.from_user.id}"
    histories[key] = [{"role": "model", "parts": [message.text]}]
    await state.set_state(ChatState.chatting)

@dp.message(ChatState.chatting, F.text)
async def chat_msg(message: types.Message, state: FSMContext):
    if not await is_group(message):
        return
    await process_chat(message.chat.id, message.from_user.id, message.text, message.message_id)

async def process_chat(chat_id: int, uid: int, text: str, user_msg_id: int):
    key = f"{chat_id}_{uid}"
    h = histories.get(key, [])
    h.append({"role": "user", "parts": [text]})
    
    model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=SYS_PROMPT)
    
    try:
        chat = model.start_chat(history=h[:-1])
        resp = await chat.send_message_async(text)
        ans = resp.text
    except Exception as e:
        h.pop()
        await bot.send_message(chat_id, str(e))
        return

    h.append({"role": "model", "parts": [ans]})
    histories[key] = h
    
    b_msg = await bot.send_message(chat_id, ans)
    
    lm = last_msgs.get(key, [])
    lm.extend([user_msg_id, b_msg.message_id])
    last_msgs[key] = lm

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
