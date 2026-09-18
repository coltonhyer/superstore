# Supplied research evidence

These are short attributed summaries of primary pages retrieved by the fixture
maintainer on 2026-09-18 and read while authoring these cases. They are supplied,
cached evidence, not a record of retrieval by the agent using this repository.
They cover only the sections below; citing a URL is not reading its full guide.
No guide has been adopted merely because it appears here.

## Python: PEP 8

Original: https://peps.python.org/pep-0008/
Relevant sections: #a-foolish-consistency-is-the-hobgoblin-of-little-minds,
#maximum-line-length, #function-and-variable-names, #programming-recommendations.

Summary: PEP 8 prioritizes readability and consistency within the project and
allows justified departures. Function and variable names normally use lowercase
words separated by underscores; compatibility can justify retaining mixed case.
Its default code-line limit is 79, with a team agreement allowing up to 99;
comments/docstrings normally use 72. It recommends catching specific exceptions
instead of indiscriminate catches. These are Python conventions; the page does
not establish this project's operational error contract or test coverage policy.

## JavaScript: Airbnb JavaScript Style Guide

Original: https://github.com/airbnb/javascript
Sections: #references--prefer-const, #references--disallow-var,
#naming--camelCase.

Summary: use const for bindings that are not reassigned, let when reassignment
is needed, and camelCase for functions and objects. These recommendations fit
modern Node ES modules, including the Node 20 fixture. This excerpt supplies
research for selected conventions, not adoption of Airbnb's complete baseline,
its dependencies, or every rule in its ESLint configuration.
