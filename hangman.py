import requests
from bs4 import BeautifulSoup

class StateMachine:

    def __init__(self, channel):
        self.gameState = Setup()
        self.channel = channel

    async def run(self):
        while True:
            self.gameState, status = await self.gameState.run(self.channel)
            if status == 'stop':
                return False
            if status == 'break':
                return True

    async def next(self, input_value):
        self.gameState, status = await self.gameState.next(input_value)
        return await self.run()


class GameState:
    def __init__(self, hangman_state=None):
        if hangman_state:
            self.hangman_state = hangman_state
        else:
            self.hangman_state = Hangman()


class Setup(GameState):
    def __init__(self):
        hangman_state = Hangman()
        super().__init__(hangman_state)

    async def run(self, channel):
        await channel.send("Starting new hangman game")
        return AwaitResponse(self.hangman_state), 'continue'


class ProcessInput(GameState):
    def __init__(self, hangman_state, input):
        super().__init__(hangman_state)
        self.input = input

    async def run(self, channel):
        if len(self.input) == 0:
            return AwaitResponse(self.hangman_state), 'continue'
        elif self.input == 'restart':
            return Setup(), 'continue'
        elif self.input == 'quit':
            return LoseState(self.hangman_state), 'continue'
        else:
            correct = self.hangman_state.guess(self.input)
            if correct:
                await channel.send('correct!')
            else:
                await channel.send(f'wrong! {self.hangman_state.num_errors}/{self.hangman_state.max_errors} errors')

        if self.hangman_state.win():
            return WinState(self.hangman_state), 'continue'
        elif self.hangman_state.lose():
            return LoseState(self.hangman_state), 'continue'
        else:
            return AwaitResponse(self.hangman_state), 'continue'


class AwaitResponse(GameState):
    def __init__(self, hangman_state):
        super().__init__(hangman_state)

    async def run(self, channel):
        word = self.hangman_state.format_word()
        letters = self.hangman_state.format_letters()
        if letters:
            await channel.send(f"{word}    ~~{letters}~~")
        else:
            await channel.send(word)
        return AwaitResponse(self.hangman_state), 'break'

    async def next(self, input_value):
        return ProcessInput(self.hangman_state, input_value), 'continue'


class WinState(GameState):
    def __init__(self, hangman_state):
        super().__init__(hangman_state)

    async def run(self, channel):
        composition = f"You won! With {self.hangman_state.num_guesses} guesses and {self.hangman_state.num_errors} errors.\n" \
                f"The word was \"{self.hangman_state.word}\"\n"\
                f"{self.hangman_state.definition}"
        await channel.send(composition)

        return None, 'stop'


class LoseState(GameState):
    def __init__(self, hangman_state):
        super().__init__(hangman_state)

    async def run(self, channel):
        composition = f"You lost after {self.hangman_state.num_guesses} guesses.\n" \
                      f"The word was \"{self.hangman_state.word}\"\n" \
                      f"{self.hangman_state.definition}"
        await channel.send(composition)
        return None, 'stop'


class Hangman:

    def __init__(self):
        self.word, self.definition = self.generate_word()
        self.num_guesses = 0
        self.num_errors = 0
        self.max_errors = 6
        self.letters_guessed = {' '}
        self.false_letters = set()

    def format_word(self):
        return ' '.join([c if c in self.letters_guessed else '\_' for c in self.word])

    def format_letters(self):
        return ' '.join(sorted(self.false_letters))

    def generate_word(self):
        r = requests.get("https://www.wordgenerator.net/application/p.php?id=dictionary_words&type=2&spaceflag=false")
        soup = BeautifulSoup(r.text)
        ps = soup.find_all('p')
        word = ps[0].text.lower()
        definition = ps[1].text.lower()
        return word, definition


    def guess(self, input_value):
        self.num_guesses = self.num_guesses + 1
        if len(input_value) == 1:
            return self.guess_letter(input_value)
        else:
            return self.guess_word(input_value)

    def guess_letter(self, letter):
        if letter in self.word and letter not in self.letters_guessed:
            self.letters_guessed.add(letter)
            return True
        else:
            self.num_errors += 1
            if letter not in self.letters_guessed:
                self.false_letters.add(letter)
            return False

    def guess_word(self, word):
        if word == self.word:
            for c in word:
                self.letters_guessed.add(c)
            return True
        else:
            self.num_errors += 1
            return False

    def win(self):
        for c in self.word:
            if c not in self.letters_guessed:
                return False
        return True

    def lose(self):
        return self.num_errors >= self.max_errors

    def progress(self):
        self.gameState.update()
