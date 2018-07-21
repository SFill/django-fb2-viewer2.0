from bs4 import BeautifulSoup as BSoup
import os
from login_sample.settings import MEDIA_ROOT


class Origin(object):
    def __init__(self, soup):
        self._soup = soup
        self._text = ''
        self._tags = []

    @property
    def org_tag(self):
        self._org_tag = None
        return self._org_tag

    @property
    def tag(self):
        return None

    @property
    def atr(self):
        return None

    def v2(self):
        return self._tags

    def _change_tag(self):
        if self.tag is not None:
            for chunk in self._soup.find_all(self.org_tag):
                chunk.name = self.tag
                if self.atr is not None:
                    for item, key in self.atr.items():
                        try:
                            chunk[item] = key
                        except KeyError:
                            pass
                        continue
                self._tags.append(chunk)


class Section(Origin):
    def __init__(self, soup, title):
        super().__init__(soup)
        self.title = title
        self._dir_path = None
        self._paths = None
        self._make_directory()
        self._change_tag()

    @property
    def org_tag(self):
        self._org_tag = 'section'
        return self._org_tag

    @property
    def tag(self):
        self._tag = 'div'
        return self._tag

    @property
    def atr(self):
        return {'style': 'overflow:scroll; width: 400px; height: 400px; padding: 10px; margin: auto; background: #fc0; ',
                'align': 'left'
                }

    def _make_directory(self):
        directory = os.path.dirname(MEDIA_ROOT)
        if os.path.exists(directory):
            self._title_path = os.path.join(MEDIA_ROOT, self.title)
            if not os.path.exists(self._title_path):
                os.mkdir(os.path.join(MEDIA_ROOT, self.title))
            os.chdir(self._title_path)

    def make_section_file(self, section, number):
        self._soup.body.contents = section
        self._dir_path = self._title_path+'/{0}.fb2'.format(number)
        with open(self._dir_path, 'w', encoding='utf-8') as f:
            f.write(self._soup.prettify())

    def _change_tag(self):
        self._body = (i for i in self._soup.find('body').children if i.name != 'title')
        j = 0
        if self.tag is not None:
            for i in self._body:
                try:
                    if i.name == 'section':
                        self.make_section_file(i, j)
                        i.name = 'div'
                        try:
                            i.title.name = 'h3'
                        except AttributeError:
                            pass
                        if self.atr is not None:
                            for item, key in self.atr.items():
                                try:
                                    i[item] = key
                                except KeyError:
                                    continue
                        self._tags.append((i.prettify(), "{0}/{1}.fb2".format(self.title, j)))
                        j += 1
                except IndexError:
                    break

    def get_paths(self):
        return self._paths


class DocumentInfo:
    def __init__(self, info):
        self._info = info
        self._tag = 'body'
        self._tags = []
        self._find_tag()

    def _find_tag(self):
        if self._info:
            self._tags = self._info.find_all(self._tag)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._tags)


class AuthorInfo(DocumentInfo):
    def _find_tag(self):
        self._tag = 'author'
        if self._info:
            self._tags = self._info.find(self._tag).children


class GenresInfo(DocumentInfo):
    def _find_tag(self):
        self._tag = 'genre'
        if self._info:
            self._tags = iter(self._info.find_all(self._tag))


class Fb2(object):
    def __init__(self, file, title):
        self.file = file
        self._info = ''
        self._root = None
        self.tags = []
        self._section = Section(self.root, title)
        self._all_doc = self._section.v2()
        self._general_path = self._section.get_paths()

    @property
    def root(self):
        if self._root is None:
            for chunk in self.file:
                self._info += chunk
            self._root = BSoup(self._info, 'xml')
        return self._root

    def description(self):
        self._descr = self.root.find('description')

        self._genrs = ', '.join([name.string for name in GenresInfo(self._descr)]) + '.'
        print('Genres:', self._genrs)

        self._author = ' '.join([part_of_name.string for part_of_name in AuthorInfo(self._descr) if part_of_name.name != 'id'])
        print('Author:', self._author)

    def section(self):
        return self._all_doc

    def get_general_path(self):
        return self._general_path



