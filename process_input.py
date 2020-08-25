import scraper
import jisho
from dice import roll_dice as roll_dice
from hangman import StateMachine as HangmanStatemachine

channel_machines = {}


async def process(message):
    # ignore if input does not start with a dollar
    if not message.content.startswith('$'):
        return

    print(message)

    command_name, command = match_command(message.content[1:])
    if command:
        message.content = message.content[1 + len(command_name):].strip()
        await command(message)


def match_command(input_value):
    for command in commands.keys():
        if input_value.startswith(command):
            return command, commands[command]
    return None, None


async def nhk(message):
    news_title, news_url, news_body = scraper.get_latest_news()
    await message.channel.send(news_title + '\n' + news_url)
    await message.channel.send(news_body[:2000])


async def translate(message):
    word, readings, common, senses = jisho.get_translation(message.content)
    if word:
        composed_readings = ', '.join(readings)
        composed_senses = '\n'.join(
            [f"{sense['parts_of_speech'][0]}\n{', '.join(sense['english_definitions'])}" for sense in senses])
        composition = f"{word}\n{composed_readings}\n{composed_senses}"
        await message.channel.send(composition)


async def dice(message):
    outcome = roll_dice(message.content)
    await message.channel.send(outcome)


async def hangman(message):
    channel = message.channel
    if channel not in channel_machines:
        channel_machines[channel] = {}

    states = channel_machines[channel]
    if 'hangman' not in states:
        states['hangman'] = HangmanStatemachine(message.channel)
        await states['hangman'].run()

    else:
        hangman_state = states['hangman']
        continue_game = await hangman_state.next(message.content)
        if not continue_game:
            states.pop('hangman')
            if len(states) == 0:
                channel_machines.pop(channel)


commands = {
    'hello': (lambda x: x.channel.send('Hello!')),
    'nhk': nhk,
    'd': dice,
    't': translate,
    'h': hangman
}
