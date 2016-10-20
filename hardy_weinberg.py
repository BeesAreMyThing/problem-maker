import random
import gui

BOX_TITLE = "BZ 111 Quiz Program"


def fuzzy_equal(user, real, fuzz=0.01):
    try:
        if real - fuzz <= user <= real + fuzz:
            return True
        else:
            return False
    except TypeError:
        return False


class ProblemValues(object):
    def __init__(self, p):
        if 0 < p > 1:
            raise ArithmeticError("P must be between 0 and 1")
        self.p = round(p, 2)
        self.q = round(1 - p, 2)
        self.p2 = round(self.p**2, 2)
        self.q2 = round(self.q**2, 2)
        self._2pq = round(2 * self.p * self.q, 2)

animals = ['bears', 'deer', 'rabbits', 'robins', 'hawks', 'sea stars',
           'sharks', 'dolphins', 'pufferfish', 'snakes', 'lizards', 'turtles']
phenotypes = [('black', 'white'), ('big', 'small'), ('fast', 'slow')]

terms = {'p': ['p', 'The frequency of dominant alleles',
               'The frequency of A alleles'],
         'q': ['q', 'The frequency of recessive alleles',
               'The frequency of a alleles'],
         'p2': ['p\u00b2', 'The frequency of homozygous dominant individuals',
                'The frequency of AA individuals'],
         'q2': ['q\u00b2', 'The frequency of homozygous recessive individuals',
                'The frequency of aa individuals'],
         '_2pq': ['2pq', 'The frequency of heterozygous individuals',
                  'The frequency of Aa individuals']}


class Question(object):
    def __init__(self):
        self.animal = random.choice(animals)
        trait = random.choice(phenotypes)
        self.trait_dom = trait[0]
        self.trait_rec = trait[1]
        self.values = vars(ProblemValues(p=random.uniform(0.05, 0.95)))
        self.term_type = random.randint(0, 2)   # variable, genotype, or zygous
        self.question = None
        self.solution = ''
        self.answers = [self.values[x] for x in ['p', 'q', 'p2', '_2pq', 'q2']]

    def ask(self):
        prompt = ('Assuming the population is at hardy-weinberg equilibrium, '
                  'report the requested values below as a '
                  'proportion, rounding to two decimal places.')
        question_dict = dict(zip(self.values.keys(),
                                 [terms[x][self.term_type] + ':'
                                  for x in self.values.keys()]))
        question_list = [question_dict[x]
                         for x in ['p', 'q', 'p2', '_2pq', 'q2']]

        loop = gui.QuestionLoop(title=BOX_TITLE,
                                prompt=self.question + '\n\n' + prompt,
                                questions=question_list,
                                correct_answers=self.answers,
                                solution=self.solution,
                                checker=self.answer_checker)
        return loop.main_loop()

    def answer_checker(self, raw_answers):
        formatted_answers = []
        for each in raw_answers:
            try:
                formatted_answers.append(float(each))
            except ValueError:
                formatted_answers.append(each)

        result = [fuzzy_equal(user, correct)
                  for user, correct in zip(formatted_answers, self.answers)]
        return result

    def solve_p_plus_q(self, solve_for):
        solve_dict = {'p': 'q', 'q': 'p'}
        try:
            given = solve_dict[solve_for]
        except KeyError:
            raise ValueError('Can only solve for p or q.')

        step = ('Solve for {0} using {1} = {2}:\n\t{0} + {1} = 1\n\t'
                '{0} = 1 - {1} = 1 - {2} = {3}'
                ''.format(solve_for, given,
                          self.values[given], self.values[solve_for]))
        return step

    def solve_square_or_root(self, solve_for):
        solve_dict = {'p': 'p2', 'p2': 'p', 'q': 'q2', 'q2': 'q'}
        try:
            given = solve_dict[solve_for]
        except KeyError:
            raise ValueError('Can only solve for p, q, p\u00b2, or q\u00b2.')
        if '2' in given:
            step = ('Solve for {0} using {0}\u00b2 = {1}:\n\t'
                    '{0} = \u221A({0}\u00b2)\n\t{0} = \u221A({1}) = {2}'
                    ''.format(solve_for, self.values[given],
                              self.values[solve_for]))
        else:
            step = ('Solve for {0}\u00b2 using {0} = {1}:\n\t'
                    '{0}\u00b2 = ({0})\u00b2\n\t{0}\u00b2 = ({1})\u00b2 = {2}'
                    ''. format(given, self.values[given],
                               self.values[solve_for]))
        return step

    def solve_2pq(self):
        step = ('Solve for 2pq using p = {0} and q = {1}:\n\t'
                '2pq = 2 x p x q\n\t2pq = 2 x {0} x {1} = 2 x {2} = {3}'
                ''.format(self.values['p'], self.values['q'],
                          round((self.values['p'] * self.values['q']), 2),
                          self.values['_2pq']))
        return step

    def check_equations(self):
        val = self.values
        step1 = ('Double-check allele frequencies:\n\tp + q = 1\n\t'
                 '{0} + {1} = {2}'.format(val['p'], val['q'],
                                          val['p'] + val['q']))
        step2 = ('Double-check genotype frequencies:\n\tp2 + 2pq + q2 = 1\n\t'
                 '{0} + {1} + {2} = {3}'
                 ''.format(val['p2'], val['_2pq'], val['q2'],
                           val['p2'] + val['_2pq'] + val['q2']))
        return '\n\n'.join([step1, step2])


class GivenPorQ(Question):
    def __init__(self):
        super().__init__()
        self.given = random.choice(['p', 'q'])
        self.question = ("In a population of {0}, being {1} is "
                         "dominant over being {2}. {3} is {4}."
                         "".format(self.animal, self.trait_dom, self.trait_rec,
                                   terms[self.given][self.term_type],
                                   self.values[self.given]))
        self.solution = self.solve()

    def solve(self):
        solve_dict = {'p': 'q', 'q': 'p'}
        solve_for = solve_dict[self.given]

        steps = [self.solve_p_plus_q(solve_for),
                 self.solve_square_or_root('p2'),
                 self.solve_square_or_root('q2'),
                 self.solve_2pq(), self.check_equations()]
        return '\n\n'.join(steps)


class GivenP2orQ2(Question):
    def __init__(self):
        super().__init__()
        self.given = random.choice(['p2', 'q2'])
        self.question = ("In a population of {0}, being {1} is "
                         "dominant over being {2}. {3} is {4}."
                         "".format(self.animal, self.trait_dom, self.trait_rec,
                                   terms[self.given][self.term_type],
                                   self.values[self.given]))
        self.solution = self.solve()

    def solve(self):
        solve_for1 = self.given[0]   # p or q
        solve_dict2 = {'p': 'q', 'q': 'p'}
        solve_for2 = solve_dict2[solve_for1]
        steps = [self.solve_square_or_root(solve_for1),
                 self.solve_p_plus_q(solve_for2),
                 self.solve_square_or_root(solve_for2 + '2'),
                 self.solve_2pq(), self.check_equations()]
        return '\n\n'.join(steps)


class GivenTwo(Question):
    def __init__(self):
        super().__init__()
        self.given = ['p2', 'q2', '_2pq']
        self.given.remove(random.choice(self.given))
        self.question = (
            "In a population of {0}, being {1} is dominant over being {2}. "
            "{3} is {4}. {5} is {6}."
            "".format(self.animal, self.trait_dom, self.trait_rec,
                      terms[self.given[0]][self.term_type],
                      self.values[self.given[0]],
                      terms[self.given[1]][self.term_type],
                      self.values[self.given[1]]))
        self.solution = self.solve()

    def solve_from_two(self, solve_for):
        givens = ['p2', '_2pq', 'q2']
        givens.remove(solve_for)
        as_text = {'p2': 'p\u00b2', '_2pq': '2pq', 'q2': 'q\u00b2'}
        step = ('Solve for {0} using {1} = {2} and {3} = {4}:\n\t'
                'p\u00b2 + 2pq + q\u00b2 = 1\n\t'
                '{0} = 1 - {1} - {3} = 1 - {2} - {4}\n\t'
                '{0} = 1 - {5} = {6}'
                ''.format(as_text[solve_for], as_text[givens[0]],
                          self.values[givens[0]], as_text[givens[1]],
                          self.values[givens[1]],
                          round(self.values[givens[0]] +
                                self.values[givens[1]], 2),
                          self.values[solve_for]))
        return step

    def solve(self):
        options = ['p2', '_2pq', 'q2']
        for each in self.given:
            options.remove(each)
        step = [self.solve_from_two(options[0]),
                self.solve_square_or_root('p'), self.solve_square_or_root('q'),
                self.check_equations()]
        return '\n\n'.join(step)


class PopSizeQuestion(Question):
    def __init__(self):
        super().__init__()
        self.pop_size = random.choice([1000, 2000, 5000, 10000])


class GivenSqWithPop(PopSizeQuestion):
    def __init__(self):
        super().__init__()
        self.given = random.choice(['p2', 'q2'])
        if self.given == 'p2':
            self.given_trait = self.trait_dom
        if self.given == 'q2':
            self.given_trait = self.trait_rec
        self.question = (
            "In population of {0} {1}, being {2} is in completely"
            " dominant over being {3}. {4} {1} are {5}."
            "".format(self.pop_size, self.animal,
                      self.trait_dom, self.trait_rec,
                      int(self.values[self.given] * self.pop_size),
                      self.given_trait))
        self.solution = self.solve()

    def solve(self):
        solve_dict = {'p': 'q', 'q': 'p'}
        step = [self.solve_geno_from_pop(),
                self.solve_square_or_root(self.given[0]),
                self.solve_p_plus_q(solve_dict[self.given[0]]),
                self.solve_square_or_root(solve_dict[self.given[0]] + '2'),
                self.solve_2pq(), self.check_equations()]
        return '\n\n'.join(step)

    def solve_geno_from_pop(self):
        solve_dict = {'q2': 'aa', 'p2': 'AA'}
        geno = solve_dict[self.given]
        step = ('Solve for {0} frequency:\n\t'
                'There are {1} {2}s in the population.\n\t{3} are {4} ({0}).'
                '\n\t{5}\u00b2 = {3} / {1}\n\t{5}\u00b2 = {6}'
                ''.format(geno, self.pop_size, self.animal,
                          int(self.values[self.given] * self.pop_size),
                          self.given_trait, self.given[0],
                          self.values[self.given]))
        return step


class GivenPQWithPop(PopSizeQuestion):
    def __init__(self):
        super().__init__()
        self.given = random.choice(['p', 'q'])
        if self.given == 'p':
            self.given_trait = self.trait_dom
        if self.given == 'q':
            self.given_trait = self.trait_rec
        self.question = (
            "In population of {0} {1}, being {2} is dominant over being {3}. "
            "There are {4} {5} alleles in the population."
            "".format(self.pop_size, self.animal,
                      self.trait_dom, self.trait_rec,
                      int(self.values[self.given] * self.pop_size * 2),
                      self.given_trait))
        self.solution = self.solve()

    def solve(self):
        solve_dict = {'p': 'q', 'q': 'p'}
        step = [self.solve_alleles_from_pop(),
                self.solve_p_plus_q(solve_dict[self.given]),
                self.solve_square_or_root('p2'),
                self.solve_square_or_root('q2'),
                self.solve_2pq(), self.check_equations()]
        return '\n\n'.join(step)

    def solve_alleles_from_pop(self):
        step = (
            'Solve for {0} allele frequency:\n\tThere are {1} {2} in the '
            'population.\n\tEach individual has 2 alleles.\n\t'
            '{1} {2}s x 2 alleles = {3} alleles in the population\n\t'
            '{4} = {0} alleles / alleles in the population\n\t{4} = '
            '{5} {0} alleles / {3} alleles in the population\n\t{4} = {6}'
            ''. format(self.given_trait, self.pop_size, self.animal,
                       self.pop_size * 2, self.given,
                       int(self.values[self.given] * self.pop_size * 2),
                       self.values[self.given]))
        return step


question_types = [GivenPorQ, GivenPQWithPop, GivenP2orQ2, GivenSqWithPop,
                  GivenTwo, GivenTwo]


def run():
    resp = 'New Question'
    while resp == 'New Question':
        question = random.choice(question_types)()
        resp = question.ask()
    return 'Main Menu'

if __name__ == "__main__":
    run()
