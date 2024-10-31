from telebot.bot import TelegramBot
from telebot.user import User
from telebot.database import DBSettings
from telebot.events import Message
from spectrum import AudioSpectre
from time import time

DBSettings.path = 'test.db'

with open('token.secret', 'r') as token_file:
    token_str = token_file.read().strip(' \n')

bot = TelegramBot(token=token_str)

@bot.registerHandler(type=Message, message_type=Message.Type.VOICE_MESSAGE)
def handleVoiceMessage(message: Message) -> None:
    notification = message.reply(text='Processing your audio')
    audio_file = message.getFile(message.media['file_id'])
    s = AudioSpectre(audio_file)
    photo = s.Spectre
    message.reply(text='Here is the spectre of provided audio', photo=photo)
    notification.delete()

@bot.registerHandler(type=Message, message_type=Message.Type.COMMAND)
def handleCommand(message: Message, *cmd: list[str]) -> None:
    if message.command[0] == '/help' or message.command[0] == '/start':
        message.answer(text=f'Just send audio-message to this bot and enjoy spectrum of provided audio. In future bot would provide detailed information about provided audio.')

    elif message.command[0] == '/settings':
        message.answer(text=f'Settings is not implemented yet!')
    
    else:
        message.answer(text=f'Unknown command "{message.command[0]}"')
    
# @bot.registerHandler(type=Message, message_type=Message.Type.COMMAND)
# def handleCommand(message: Message, cmd: str, args: list[str]) -> None:
#     print(f'Handled command {cmd} with argumens {args} from {message.from_id}')

# @bot.registerHandler(type=Message, message_type=Message.Type.VOICE_MESSAGE)
# def PreHandleVoiceMessage(message: Message) -> None:
#     print(f'Proc')

bot.polling()
