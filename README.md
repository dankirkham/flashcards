# Python Flashcards CLI program

## Usage

1. Create a markdown table with Question and Answer columns.
```markdown
| Question                                                   | Answer               |
|------------------------------------------------------------|----------------------|
| What is the air speed velocity of an unladed swallow?      | African or European? |
| What is 2+2?                                               | 4                    |
| What is the meaning of life, the universe, and everything? | 42                   |
```

2. Create folder for cards database.
```bash
mkdir ~/.flashcards
```

3. Install requirements.
```bash
pip3 install -r requirements.txt
```

4. Run flashcards program with your cards markdown file.
```bash
python3 -m flashcards cards.md
```
