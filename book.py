import os
import re

import click
import frontmatter
from jinja2.loaders import FileSystemLoader
from latex import build_pdf
from latex.jinja2 import make_env

env = make_env(loader=FileSystemLoader('template/'))

base = env.get_template('base.tex')
recipe = env.get_template('recipe.tex')

itemization = env.get_template('itemize.tex')
enumeration = env.get_template('enumerate.tex')

OPTIONS = 'left=0pt,parsep=10pt'


def process_subsections(array, item, template=itemization):
    subsections = []

    for subsection in array:
        title = subsection['title']
        items = subsection[item]

        text = r'\textit{' + title + '}\n' + template.render(items=items, options=OPTIONS)

        subsections.append(text)

    return '\n\n'.join(subsections)


class Recipe(object):

    def __init__(self, filename):

        self.post = frontmatter.load(filename)
        self.recipe = self.post['recipe']

    @property
    def title(self):
        return self.post['title']

    @property
    def note(self):
        return self.post.content

    @property
    def servings(self):
        return self.recipe['servings']

    @property
    def prep(self):
        return self.recipe['prep']

    @property
    def cook(self):
        return self.recipe['cook']

    @property
    def ingredients(self):
        ingredients = self.recipe['ingredients']
        if isinstance(ingredients[0], str):
            return itemization.render(items=ingredients, options=OPTIONS)
        return process_subsections(ingredients, 'ingredients', itemization)

    @property
    def directions(self):
        directions = self.recipe['directions']
        if isinstance(directions[0], str):
            return enumeration.render(items=directions, options=OPTIONS)
        return process_subsections(directions, 'directions', enumeration)


@click.command()
@click.option('--posts-dir', '-p', default='_posts', help='Posts directory')
@click.option('--output', '-o', default='book.pdf', help='Output')
def create_book(posts_dir, output):
    posts = []
    for root, _, files in os.walk(posts_dir):
        posts.extend([os.path.join(root, f) for f in files])

    # Filter the non-posts
    posts = [p for p in posts if re.match(r'^(\w+\/)+\d{4}-\d{2}-\d{2}', p)]

    recipes = [Recipe(post) for post in posts]

    template = env.get_template('base.tex')
    book = template.render(recipes=recipes).replace('°', r'$^\circ$')

    # this builds a pdf-file inside a temporary directory
    pdf = build_pdf(book)

    pdf.save_to(output)


if __name__ == '__main__':
    create_book()
