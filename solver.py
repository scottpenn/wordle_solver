import pandas as pd
import pickle
import string

words = pd.read_pickle('data/words.pkl')

with open('data/letter_dict.pkl', 'rb') as file:
    letter_dict = pickle.load(file)

with open('data/position_dict.pkl', 'rb') as file:
    position_dict = pickle.load(file)

total_words = words.shape[0]

guessed_letters = set()
guessed_positions = set()

def get_guess_input():
    print('\nPlease enter your guess.\n')
        
    guess = input('Guess: ')
    while len(guess) != 5 or guess not in words.index:
        print("\nThat is not a valid guess.\n")
        guess = input('Guess: ')
        
    return guess

def guess_word(e):

    num_valid = words['valid'].sum()
    
    if num_valid == 1:
        solution = words[words['valid']].index[0]
        print('\nThere is only 1 valid word remaining.\n')
        print(f'Guess "{solution}" to solve the puzzle!')
        return solution, num_valid
    else:
        print(f'\nThere are {num_valid} valid words remaining.\n')
              
    words['score'] = words['letter_score'] + words['position_score']
    words['score'].where(words['valid'], words['score'] * e, inplace=True)

    best_words = words[words['score'] > 0].sort_values(['score', 'tiebreaker'], ascending=False)

    print('Here are the best guesses:')
    for i, (word, score) in enumerate(zip(best_words.index[:5], best_words.score[:5])):
        print(f'  {i + 1}. "{word}" with a score of {score:.2f}.')
        
    return get_guess_input(), num_valid

def get_evaluation_input(tutorial=False):
    print('\nPlease enter the evaluation result.\n')
    
    if tutorial:
        print('Green = g, Yellow = y, Black = b')
        print('e.g. for "Black Black Yellow Green Black" please type "bbygb"\n')
        
    result = input('Evaluation Result: ')
    while len(result) != 5 or not set(result).issubset({'g', 'y', 'b'}):
        print("\nThat is not a valid evaluation result.\n")
        print('Green = g, Yellow = y, Black = b')
        print('e.g. for "Black Black Yellow Green Black" please type "bbygb"\n')
        result = input('Evaluation Result: ')
        
    return result

def process_result(i):
    result = get_evaluation_input(tutorial=True) if i == 0 else get_evaluation_input()
    
    for i, color in enumerate(result):
        position = i + 1
        letter = guess[i]
        match color:
            case 'g':
                words['valid'].mask(words[position] != letter, False, inplace=True)
            case 'y':
                words['valid'].mask(words[f'{position}{letter}'] > 0, False, inplace=True)
                words['valid'].where((words[[1, 2, 3, 4, 5]] == letter).any(axis=1), False, inplace=True) 
            case 'b':
                if guess.count(letter) > 1:
                    words['valid'].mask(words[f'{position}{letter}'] > 0, False, inplace=True)
                else:
                    words['valid'].mask(words[letter] > 0, False, inplace=True)
                    
    return result

def adjust_scores():
    for i, letter in enumerate(guess):
        position = f'{i + 1}{letter}'
        if letter not in guessed_letters:
            guessed_letters.add(letter)
        if position not in guessed_positions:
            guessed_positions.add(position)
        
    valid_words = words[words['valid']]

    total_valid_words = valid_words.shape[0]
    total_valid_letters = total_valid_words * 5

    words['letter_score'] = 0
    for letter in string.ascii_lowercase:
        if letter not in guessed_letters:
            letter_dict[letter] = valid_words[letter].sum() / total_valid_letters * 10
        else:
            letter_dict[letter] = 0   
        words['letter_score'] += words[letter].astype('bool') * letter_dict[letter]

    words['position_score'] = 0
    for position in range(1, 6):
        for letter in string.ascii_lowercase:
            key = f'{position}{letter}'
            if key not in guessed_positions:
                position_dict[key] = valid_words[key].sum() / total_valid_words * 10
            else:
                position_dict[key] = 0
            words['position_score'] += words[key].astype('bool') * position_dict[key]

print('Hello! I will attempt to solve today\'s Wordle puzzle.')

for i in range(5):
    exploration_factors = [1.0, 0.75, 0.5, 0.25, 0]
    guess, valid = guess_word(exploration_factors[i])
    if valid == 1:
        break

    result = process_result(i)
    if result == 'ggggg':
        print('\nCongratulations! You solved today\'s puzzle!')
        
        print('...actually, it was me.')
        break

    adjust_scores()