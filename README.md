# DFA MINIMIZATION TOOL

## Project description:

This project was created for my Theory of automata class, it is designed to be a web based tool used in minimization DFA's, it shows steps taken in minimizing given DFA's. 
Users are to input DFA's in JSON format (this feature will be changed soon) and it will output a DFA in JSON format as well(This will also be changed soon to allow for others to use and understand the produt)

## Main features:
Takes DFA in JSON format in as input.
Django reads the inputted JSON and then builds an internal DFA.
Runs table filling algorithm to find equivalent states.
Show steps taken in the process as well as results.
Display the final Minimized DFA in JSON format.

## Technical stack:
1. Language: HTML, CSS, JavaScript and Python with Django
2. Platform: Github

## Goals for the project:
1. Expand my knowledge of DFAs and DFA minimization.
2. Learn how to apply that knowledge in code.
3. Break each step in DFA minimization into separate parts so users can follow along.
4. Learn how DFA equivalence and partitioning works.


## Running locally (configuration)

Settings come from environment variables, not from source code:

```bash
export DJANGO_DEBUG=1                 # local development only
cd dfatool && python manage.py runserver
# in another terminal, serve the page (browsers block file:// requests to the API):
python -m http.server 5500            # then open http://localhost:5500/index.html
```

For anything other than local use, set `DJANGO_SECRET_KEY` to a long random value, leave `DJANGO_DEBUG` unset, and set `DJANGO_ALLOWED_HOSTS` and `DJANGO_CORS_ORIGINS` for your domain.
The API accepts DFAs of up to 200 states and 50 symbols.
