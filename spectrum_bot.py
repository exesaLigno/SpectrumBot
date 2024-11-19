from telebot.bot import TelegramBot
from telebot.user import User
from telebot.database import DBSettings
from telebot.events import Message, Callback
from spectrum import AudioSpectre, Scale, Limits
from time import time
from telebot.dumpable_dictionary import DDict

DBSettings.path = 'test.db'

telemetry = DDict('telemetry.json')

#cached_spectres = {}

with open('token.secret', 'r') as token_file:
    token_str = token_file.read().strip(' \n')

bot = TelegramBot(token=token_str)

@bot.registerHandler(type=Message, message_type=Message.Type.VOICE_MESSAGE)
def handleVoiceMessage(message: Message) -> None:

    if 'processings_count' in telemetry:
        telemetry['processings_count'] += 1
    else:
        telemetry['processings_count'] = 1

    if 'unique_users' in telemetry:
        if message.chat_id not in telemetry['unique_users']:
            telemetry['unique_users'].append(message.chat_id)
    else:
        telemetry['unique_users'] = [message.chat_id]
        

    notification = message.reply(text='Processing your audio')

    audio_file = message.getFile(message.media['file_id'])
    s = AudioSpectre(audio_file)
    photo = s.Spectre(scale=Scale.LINEAR, limits=Limits.FULL)

    spectre = notification.edit(text='Here is the spectre of provided audio', photo=photo, 
                                keyboard=[
                                    [('Switch to logarithmic scale', 'logscale')], 
                                    [('Fit to content', 'fit-content')]
                                ])
    
    #cached_spectres[spectre.message_id] = {'spectre': s, 'scale': Scale.LINEAR, 'limits': Limits.FULL}


@bot.registerHandler(type=Callback)
def handleCallback(callback: Callback):

    if callback.data in ['logscale', 'linscale', 'fit-content', 'full']:

        callback.answer('Switching to different scales and limits are not implemented!', show_alert=True)
        
        # s: AudioSpectre = cached_spectres[callback.message.message_id]['spectre']

        # if callback.data == 'logscale':
        #     cached_spectres[callback.message.message_id]['scale'] = Scale.LOGARITHMIC
            
        # elif callback.data == 'linscale':
        #     cached_spectres[callback.message.message_id]['scale'] = Scale.LINEAR

        # elif callback.data == 'fit-content':
        #     cached_spectres[callback.message.message_id]['limits'] = Limits.FIT_TO_DATA

        # elif callback.data == 'full':
        #     cached_spectres[callback.message.message_id]['limits'] = Limits.FULL
        
        # else:
        #     pass

        # photo = s.Spectre(scale=cached_spectres[callback.message.message_id]['scale'], 
        #                   limits=cached_spectres[callback.message.message_id]['limits'])
        
        # if cached_spectres[callback.message.message_id]['scale'] == Scale.LINEAR:
        #     scale_but = ('Switch to logarithmic scale', 'logscale')
        # else:
        #     scale_but = ('Switch to linear scale', 'linscale')

        # if cached_spectres[callback.message.message_id]['limits'] == Limits.FULL:
        #     limits_but = ('Fit to content', 'fit-content')
        # else:
        #     limits_but = ('Show full spectre', 'full')

        # keyboard = [[scale_but], [limits_but]]

        # callback.message.edit(text='Here is the spectre of provided audio', photo=photo, keyboard=keyboard)

    else:
        callback.answer('Internal error!', show_alert=True)

@bot.registerHandler(type=Message, message_type=Message.Type.COMMAND)
def handleCommand(message: Message) -> None:
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

bot.polling(supress_exceptions=True)
