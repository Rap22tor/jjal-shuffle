# Jjal-Shuffle
Jjal-Shuffle (짤-Shuffle) is our idea for the Open Source Software course @ SeoulTech

## Description
The basic idea is inspired by a video on youtube, where any image's pixels can be rearranged into a persons face.
The goal of this project is to implement an application that allows a user to do something similar, but letting the
user choose any source image to any target image.

This serves as the base of our application, but since this is a popular project to do, we plan a few more features, such as:
- CLI support
- Image-to-ASCII Art
- and more...

## Development setup
Requires Python 3.10 or newer.

Clone the repository and create a virtual environment inside it:

```bash
git clone <repository-url>
cd jjal-shuffle
python -m venv .venv
```

Activate it:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# Linux / macOS / Git Bash
source .venv/bin/activate      # Git Bash on Windows: source .venv/Scripts/activate
```

Install the dependencies and run the tests:

```bash
pip install -r requirements-dev.txt
pytest
```

## Name
Since the goal of this project is to implement an open source application while still having fun, we thought the name
of should reflect this.

The name 짤-Shuffle came from the fact that both team members are doing this course in an exchange semester in Korea
and the litteral translation of "meme" being 짤. 

## Team
- Michael Dobeson
- Elias Baumgartner

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.