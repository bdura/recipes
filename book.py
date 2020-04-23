import os
import re
import yaml

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
multicol = env.get_template('multicol.tex')


def process_directions(array, item, template=itemization):
    subsections = []

    for subsection in array:
        title = subsection['title']
        items = subsection[item]

        text = r'\textit{' + title + '}\n' \
               + template.render(items=items)

        subsections.append(text)

    return '\n\n\\vspace{.1cm}'.join(subsections)


def process_ingredients(array, item, template=itemization):
    subsections = []

    for subsection in array:
        title = subsection['title']
        items = subsection[item]

        text = r'\textit{' + title + '}\n' \
               + multicol.render(content=template.render(items=items))

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
        return '' #self.post.content

    @property
    def servings(self):
        return self.recipe.get('servings', '')

    @property
    def prep(self):
        return self.recipe.get('prep', '')

    @property
    def cook(self):
        return self.recipe.get('cook', '')

    @property
    def ingredients(self):
        ingredients = self.recipe['ingredients']
        if isinstance(ingredients[0], str):
            return multicol.render(content=itemization.render(items=ingredients))
        return process_ingredients(ingredients, 'ingredients', itemization)

    @property
    def directions(self):
        directions = self.recipe['directions']
        if isinstance(directions[0], str):
            return enumeration.render(items=directions)
        return process_directions(directions, 'directions', enumeration)


@click.command()
@click.option('--directory', '-d', default='_i18n', help='Posts directory')
@click.option('--lang', '-l', default='fr', help='Language')
@click.option('--output', '-o', default='./', help='Output')
@click.option('--to-pdf', is_flag=True, help='Whether to output the PFD directly')
def create_book(directory, lang, output, to_pdf):

    posts_dir = os.path.join(directory, lang)

    posts = []
    for root, _, files in os.walk(posts_dir):
        posts.extend([os.path.join(root, f) for f in files])

    # Filter the non-posts
    posts = [p for p in posts if re.match(r'^(\w+\/)+\d{4}-\d{2}-\d{2}', p)]

    recipes = [Recipe(post) for post in posts]

    with open(os.path.join(directory, f'{lang}.yml'), 'r') as f:
        i18n = yaml.load(f)['book']

    template = env.get_template('base.tex')
    book = template.render(recipes=recipes, i18n=i18n).replace('°', r'$^\circ$')

    filename = i18n["filename"]

    if to_pdf:
        # this builds a pdf-file inside a temporary directory
        pdf = build_pdf(book)

        pdf.save_to(os.path.join(output, f'{filename}.pdf'))
    else:
        with open(os.path.join(output, f'{filename}.tex'), 'w') as f:
            f.write(book)


if __name__ == '__main__':
    create_book()
