from telebot.bot import TelegramBot
from telebot.user import User
from telebot.database import DBSettings
from telebot.events import Message
from spectrum import AudioSpectre

DBSettings.path = 'test.db'

with open('token.secret', 'r') as token_file:
    token_str = token_file.read().strip(' \n')

bot = TelegramBot(token=token_str)

@bot.registerHandler(type=Message, message_type=Message.Type.VOICE_MESSAGE)
def handleVoiceMessage(message: Message) -> None:
    print(f'Handled voice message from {message.from_id}')
    audio_file = message.getFile(message.media['file_id'])
    s = AudioSpectre(audio_file)
    message.answer(text='Here is the spectre of provided audio', photo=s.Spectre)
    

@bot.registerHandler(type=Message, message_type=Message.Type.COMMAND)
def handleCommand(message: Message, cmd: str, args: list[str]) -> None:
    print(f'Handled command {cmd} with argumens {args} from {message.from_id}')

bot.polling()
