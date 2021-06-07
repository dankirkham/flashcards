"""Spaced-repetition flashcards CLI program."""

import argparse
import hashlib
import cmd
import json
from pathlib import Path
from supermemo2 import SMTwo
from tinydb import TinyDB, Query

class Quiz(cmd.Cmd):
    prompt = "fc> "

    def __init__(self, cards, rankings):
        super(Quiz, self).__init__()
        self.cards = cards
        self.rankings = rankings

        self._next_card()

    def _next_card(self):
        card_found = False
        for idx, card in enumerate(self.cards):
            rankings = self.rankings.search(Query().fingerprint == card["fingerprint"])
            if len(rankings) == 0:
                # print("Found unreviewed card.")
                self.card_idx = idx
                card_found = True
                break

        if not card_found:
            # Find the lowest ranked one in the db
            hardest = sorted(self.rankings.all(), key=lambda k: k['easiness'])
            hardest = hardest[0]
            self.card_idx = self.cards.index(next((x for x in self.cards if hardest["fingerprint"] == x["fingerprint"])))
            # print("Found hardest card.")

        print(self.cards[self.card_idx]["question"])

    def _rank(self, val):
        card = self.cards[self.card_idx]
        rankings = self.rankings.search(Query().fingerprint == card["fingerprint"])
        review = None
        if len(rankings) > 0:
            r = json.loads(json.dumps(rankings[0]))
            review = SMTwo(r["easiness"], r["interval"], r["repetitions"]).review(val)
        else:
            review = SMTwo.first_review(val)

        ranking = {}
        ranking["easiness"] = review.easiness
        ranking["interval"] = review.interval
        ranking["repetitions"] = review.repetitions
        # ranking["review_date"] = review.review_date
        ranking["fingerprint"] = card["fingerprint"]

        print("Easiness: {}, Interval: {}, Repetitions: {}".format(ranking["easiness"], ranking["interval"], ranking["repetitions"]))

        if len(rankings) > 0:
            self.rankings.update(ranking, Query().fingerprint == card["fingerprint"])
        else:
            self.rankings.insert(ranking)

        self._next_card()

    def do_1(self, arg):
        self._rank(1)

    def do_2(self, arg):
        self._rank(2)

    def do_3(self, arg):
        self._rank(3)

    def do_4(self, arg):
        self._rank(4)

    def do_5(self, arg):
        self._rank(5)

def load_cards(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        state = "header"

        cards = []

        for line in lines:
            tokens = list(map(lambda x: x.strip(), line.split("|")))
            question = tokens[1]
            answer = tokens[2]

            if state == "header":
                if question.lower() == "question" and answer.lower() == "answer":
                    state = "separator"
            elif state == "separator":
                state = "question"
            else: # question
                s256 = hashlib.sha256()
                s256.update(question.encode("utf-8"))
                s256.update(answer.encode("utf-8"))
                fingerprint = s256.hexdigest()
                cards.append({
                    "question": question,
                    "answer": answer,
                    "fingerprint": fingerprint})

        return cards

def load_db(filename):
    base = filename.split(".")[0]
    return TinyDB(str(Path.home()) + "/.flashcards/" + base + ".json")

def main():
    """Main entry point, parse args, load db, and start REPL."""

    parser = argparse.ArgumentParser()
    parser.add_argument("cards", help="markdown file with table of flashcards")

    args = parser.parse_args()

    cards = load_cards(args.cards)
    rankings = load_db(args.cards)

    Quiz(cards, rankings).cmdloop()

    # first review
    # using quality=4 as an example, read below for what each value from 0 to 5 represents
    # review date would default to date.today() if not provided
    review = SMTwo.first_review(4, "2021-3-14")
    # review prints SMTwo(easiness=2.36, interval=1, repetitions=1, review_date=datetime.date(2021, 3, 15))

    # second review
    review = SMTwo(review.easiness, review.interval, review.repetitions).review(4, "2021-3-14")
    # review prints similar to example above.


if __name__ == "__main__":
    main()
