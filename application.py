from flask import Flask, render_template
import os
import string
import random
from elo import rate_1vs1 
import pickle
from math import log

DOG_FOLDER = os.path.join('static', 'dog_photo')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = DOG_FOLDER

folders = {string.capwords(f.split('-')[1].replace('_',' ')):f for f in os.listdir(DOG_FOLDER)}
try:
    scores = pickle.load(open('scores.p', 'rb'))
except:
    scores = {breed:1000. for breed in folders}
breed1, breed2 = None, None

def pick_breeds(scores):
    if random.random() < 0.5:
        idx = int(log(random.random())/log(0.8))
        idx = min(idx, len(scores))
        a = list(sorted(scores, key=scores.get, reverse=True))[idx]
    else:
        a = random.choice(list(scores.keys()))
    b = a
    while b == a:
        if random.random() < 0.5:
            idx = int(log(random.random())/log(0.8))
            idx = min(idx, len(scores))
            b = list(sorted(scores, key=scores.get, reverse=True))[idx+1]
        else:
            b = random.choice(list(scores.keys()))
    if random.random() < 0.5:
        a, b = b, a
    return a, b

def pick_photo(breed):
    folder = os.path.join(DOG_FOLDER, folders[breed])
    photo = random.choice(os.listdir(folder))
    return os.path.join(folder, photo)

def update_scores(winner, loser):
    scores[winner], scores[loser] = rate_1vs1(scores[winner], scores[loser])
    pickle.dump(scores, open('scores.p', 'wb'))

@app.route('/neither')
def neither():
    if breed1 and breed2:
        scores[breed1] -= 5
        scores[breed2] -= 5
    return show_index()

@app.route('/left')
def left_win():
    if breed1 and breed2:
        update_scores(breed1, breed2)
    return show_index()

@app.route('/right')
def right_win():
    if breed1 and breed2:
        update_scores(breed2, breed1)
    return show_index()

@app.route('/')
def show_index():
    global breed1
    global breed2
    breed1, breed2 = pick_breeds(scores)
    dog_file1, dog_file2 = pick_photo(breed1), pick_photo(breed2)
    return render_template("index.html",
                           dog_image1 = dog_file1,
                           dog_image2 = dog_file2,
                           dog_breed1 = breed1,
                           dog_breed2 = breed2,
                           top_dogs = sorted(((v, k) for k, v in scores.items()),
                                               reverse=True)[:10],
                           bottom_dogs = sorted(((v, k) for k, v in scores.items()),
                                                  reverse=False)[:10])

@app.route('/rank')
def show_rank():
    dogs = []
    for score, breed in sorted(((v, k) for k, v in scores.items()), reverse=True):
        dogs.append((int(score), breed, pick_photo(breed), pick_photo(breed), pick_photo(breed)))
    return render_template("rank.html",
                           dogs = dogs)

if __name__ == "__main__":
    app.run()
