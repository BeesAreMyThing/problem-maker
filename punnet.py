import random
import math
import itertools
import collections

import gui
import main

# TODO add spell check to phenotype questions?

BOX_TITLE = "BZ 111 Quiz Program"

TRAITS = [
    # Complete dominant
    ['hair color', {'B': 'brown hair', 'b': 'blond hair'}],
    ['eye color', {'G': 'green eyes', 'g': 'blue eyes'}],
    ['hand size', {'H': 'large hands', 'h': 'small hands'}],
    ['toe length', {'T': 'long toes', 't': 'stubby toes'}],
    ['finger hairiness', {'F': 'hairy fingers', 'f': 'hairless fingers'}],

    # Co-dominant
    ['blood type', {'AA': 'blood type A', 'BB': 'blood type B',
                    'AB': 'blood type AB'}],
    ['spot color', {'RR': 'red spots', 'YY': 'yellow spots',
                    'RY': 'yellow spots with red dots'}],
    ['hair color', {'WW': 'white hair', 'PP': 'purple hair',
                    'PW': 'white hair with purple streaks'}],
    ['skin color', {'GG': 'green skin', 'SS': 'silver skin',
                    'GS': 'green skin with silver spots'}],

    # Incomplete dominant
    ['spot color', {'YY': 'yellow spots', 'yy': 'red spots',
                    'Yy': 'orange spots'}],
    ['hand size', {'HH': 'large hands', 'hh': 'small hands',
                   'Hh': 'medium hands'}],
    ['toe length', {'TT': 'long toes', 'tt': 'stubby toes',
                    'Tt': 'medium toes'}],
    ['eye color', {'BB': 'blue eyes', 'Bb': 'purple eyes', 'bb': 'red eyes'}]
]


def convert_traits(given_traits):
    """ For each in given_trait, calculate dominance type and alleles
    :param given_traits: list of trait dictionaries
    :return: list of trait dictionaries
    """
    trait_list = []
    for trait_name, pheno_dict in given_traits:
        new_pheno_dict = pheno_dict.copy()
        alleles = list(set([let for key in pheno_dict.keys() for let in key]))
        if len(alleles) != 2:
            raise ValueError('Each trait should only have two alleles. Not: ',
                             alleles)
        if any([' and ' in each for each in pheno_dict.values()]):
            # " and " is used to split user answers when
            # multiple traits are present
            raise ValueError('No phenotype may contain the word " and ":',
                             pheno_dict)
        if any([len(each) > 35 for each in pheno_dict.values()]):
            # Entry boxes currently hold 75 characters without needing wrapping
            # A max length of 35 allows for two 35 char traits and an ' and '
            raise ValueError('No phenotype may be longer than 35 characters',
                             pheno_dict)

        # determine dom_type
        if alleles[0].upper() != alleles[1].upper():
            dom_type = 'co-dom'
        else:
            if len(pheno_dict.values()) == 2:
                dom_type = 'complete'
                dom = alleles[0].upper()
                rec = alleles[0].lower()
                new_pheno_dict = {dom + dom: pheno_dict[dom],
                                  dom + rec: pheno_dict[dom],
                                  rec + rec: pheno_dict[rec]}
            else:
                dom_type = 'incomplete'
        this_dict = {'name': trait_name, 'alleles': alleles,
                     'dom_type': dom_type, 'phenos': new_pheno_dict}
        trait_list.append(this_dict)
    return trait_list

TRAITS = convert_traits(TRAITS)
DOMINANCE_TYPES = ['complete dominance', 'incomplete dominance',
                   'co-dominance']


Person = collections.namedtuple('Person', ['genotype', 'phenotype', 'gametes'])


def gcd_list(a_list):
    """Find the greatest common denominator of a list of numbers

    :param a_list: a list of integers
    :return: integer
    """
    result = a_list[0]
    for i in range(1, len(a_list)):
        result = math.gcd(result, a_list[i])
    return result


def reduce_ratio(ratio_list):
    """Find the most reduced possible ratio

    :param ratio_list: list of tuples (string, integer)
    :return: list of tuples (string, integer)
    """
    gcd = gcd_list([x[1] for x in ratio_list])
    new_list = []
    for each, count in ratio_list:
        new_list.append((each, int(count / gcd)))
    return new_list


def case_match(target_string, case_type):
    """Convert target_string to same case as the case_type

    :param target_string: string
    :param case_type: string (single character)
    :return: string
    """
    if case_type.isupper():
        return target_string.upper()
    else:
        return target_string.lower()


def select_genotype(trait):
    """Randomly choose a genotype from trait

    :param trait: trait dictionary
    :return: string (genotype)
    """
    possibles = list(trait['phenos'].keys())
    hetero = None
    for geno in possibles:
        if geno[0] != geno[1]:
            hetero = geno
    if hetero:
        possibles.append(hetero)
    chosen = random.choice(possibles)
    return chosen


class PunnetSet(object):
    def __init__(self, loci_num):
        self.loci_num = loci_num
        self.trait1 = random.choice(TRAITS)
        if self.loci_num == 1:
            self.trait2 = None
            self.traits = [self.trait1]
        elif self.loci_num == 2:
            self.trait2 = self.get_trait2()
            self.traits = [self.trait1, self.trait2]
        else:
            raise ValueError('Loci number must be 1 or 2.')
        try:
            self.all_phenos = {key: value for each_dict in [self.trait1,
                                                            self.trait2]
                               for key, value in each_dict['phenos'].items()}
        except TypeError:
            self.all_phenos = self.trait1['phenos']

        self.mom = self.make_person()
        self.dad = self.make_person()
        self.kids = self.make_offspring()
        self.kid_geno = self.genotypic_ratio()
        self.kid_pheno = self.phenotypic_ratio()
        self.kid_pheno_reduced = reduce_ratio(self.kid_pheno)
        self.kid_geno_reduced = reduce_ratio(self.kid_geno)

        self.info_type = self.choose_info_type()
        self.info = self.make_trait_info() + '\n\n' + self.make_parent_info()

        self.gamete_solution()

        self.square = self.make_geno_square()

    def get_trait2(self):
        """Randomly select a second trait with a different name than trait 1

        :return: trait dictionary
        """
        trait2 = random.choice(TRAITS)
        want_same_dom_type = random.choice([True, False])
        if want_same_dom_type:
            while self.trait1['name'] == trait2['name'] or (
                    any([x in self.trait1['alleles']
                         for x in trait2['alleles']])) or (
                    self.trait1['dom_type'] != trait2['dom_type']):
                trait2 = random.choice(TRAITS)
        else:
            while self.trait1['name'] == trait2['name'] or (
                    any([x in self.trait1['alleles']
                         for x in trait2['alleles']])) or (
                    self.trait1['dom_type'] == trait2['dom_type']):
                trait2 = random.choice(TRAITS)
        return trait2

    def correct_grammar(self, genotype, is_gamete=False, target_trait=None):
        """Reorder genotype to be trait1 and dominants first

        :param genotype: string
        :param is_gamete: boolean
        :param target_trait: boolean
        :return: string
        """
        if target_trait is not None and len(genotype) > 2:
            raise ValueError("Trait cannot be specified with multiple loci.")
        try:
            if is_gamete:
                if len(genotype) == 2:
                    let1, let2 = genotype
                    if let1 in self.trait1['alleles']:
                        return let1 + let2
                    else:
                        return let2 + let1
                else:
                    return genotype
            else:
                if len(genotype) % 2 != 0 or genotype == '':
                    return genotype
                genotype = ''.join(genotype)
                if target_trait is None:
                    target_trait = self.trait1
                locus1 = [let for let in genotype
                          if let in target_trait['alleles']]
                options1 = [''.join(pair)
                            for pair in itertools.permutations(locus1)]
                geno1 = [geno for geno in options1
                         if geno in target_trait['phenos'].keys()][0]
                if len(genotype) > 2:
                    locus2 = [let for let in genotype
                              if let in self.trait2['alleles']]
                    options2 = [''.join(pair)
                                for pair in itertools.permutations(locus2)]
                    geno2 = [geno for geno in options2
                             if geno in self.trait2['phenos'].keys()][0]
                    return geno1 + geno2
                else:
                    return geno1
        except IndexError:
            return genotype

    def make_geno_square(self):
        if self.trait2 is None:
            num = 2
        else:
            num = 4
        mom = list(self.mom.gametes) * int(num/len(self.mom.gametes))
        dad = list(self.dad.gametes) * int(num/len(self.dad.gametes))
        mom.insert(0, '')
        dad.insert(0, '')
        square = [self.correct_grammar(m + d)
                  for m, d in itertools.product(dad, mom)]

        square = [square[i:i+num+1] for i in range(0, len(square), num + 1)]
        return square

    def make_pheno_square(self, geno_square):
        pheno_square = []
        for row_num, row in enumerate(geno_square):
            this_row = []
            for col_num, geno in enumerate(row):
                if col_num != 0 and row_num != 0:
                    pheno_list = []
                    for locus in [geno[:2], geno[2:]]:
                        try:
                            pheno_list.append(self.all_phenos[locus])
                        except KeyError:
                            pass
                    phenotype = ' and '.join(pheno_list)
                    this_row.append('{}\n({})'.format(phenotype, geno))
                else:
                    this_row.append(geno)

            pheno_square.append(this_row)

        return pheno_square

    def make_trait_info(self):
        """Generate given info for user

        :return: string
        """
        given_info = []
        for trait in self.traits:
            if trait['dom_type'] == 'complete':
                dom1 = trait['alleles'][0].upper()
                rec1 = dom1.lower()
                if random.choice([True, False]):
                    given = (
                        '{0}{0} and {0}{1} animals have {2}, and '
                        '{1}{1} animals have {3}.'. format(
                            dom1, rec1, trait['phenos'][dom1 + dom1],
                            trait['phenos'][rec1 + rec1]))
                else:
                    given = '{0} ({1}) is dominant to {2} ({3}).'.format(
                        trait['phenos'][dom1 + dom1].capitalize(), dom1,
                        trait['phenos'][rec1 + rec1], rec1)
            else:
                three_string = ('{0} animals have {1}, {2} animals have '
                                '{3}, and {4} animals have {5}.')
                given = three_string.format(
                        *[x for item in trait['phenos'].items()
                          for x in item])

            given_info.append(given)
        return ' '.join(given_info)

    def choose_info_type(self):
        """Chose info type for each parent: genotype, phenotype, or zygosity

        :return:
        """
        mom_options = ['geno', 'pheno', 'zygous']
        dad_options = ['geno', 'pheno', 'zygous']

        if self.trait1['dom_type'] == 'complete' or (
                        self.trait2 is None) or (
                    self.trait2['dom_type'] == 'complete'):
            mom_options.remove('pheno')
            dad_options.remove('pheno')

        return [random.choice(x) for x in [mom_options, dad_options]]

    def make_zygous(self, geno):
        geno = ''.join(geno)
        description = []
        for trait, locus in zip([self.trait1, self.trait2],
                                [geno[:2], geno[2:]]):
            zygous = ''
            if trait is not None:
                if locus[0] != locus[1]:
                    zygous += 'heterozygous'
                    if self.trait2 is not None:
                        zygous += ' for {}'.format(trait['name'])
                else:
                    zygous += 'homozygous '
                    if trait['dom_type'] == 'co-dom':
                        zygous += 'for {}'.format(self.all_phenos[locus])
                    else:
                        if locus[0].isupper():
                            zygous += 'dominant'
                        else:
                            zygous += 'recessive'
                        if self.trait2 is not None:
                            zygous += ' for {}'.format(trait['name'])
                description.append(zygous)
        if self.trait2 is not None:
            doubles = ['heterozygous', 'homozygous dominant',
                       'homozygous recessive']
            for each in doubles:
                if all([each in x for x in description]):
                    description = ['{} for both traits'.format(each)]
        return description

    def make_parent_info(self):
        description = []

        for info, geno, pheno in zip(
                self.info_type, [self.mom.genotype, self.dad.genotype],
                [self.mom.phenotype, self.dad.phenotype]):
            if info == 'geno':
                description.append('is ' + ''.join(geno))
            elif info == 'pheno':
                description.append('has ' + ' and '.join(pheno))
            elif info == 'zygous':
                description.append('is ' + ' and '.join(self.make_zygous(geno)))
            else:
                raise ValueError('info_type must be "geno", "pheno", '
                                 'or "zygous".')
        mom_phrase = 'Mom {}.'.format(description[0])
        dad_phrase = 'Dad {}.'.format(description[1])
        return mom_phrase + ' ' + dad_phrase

    def make_person(self):
        """Randomly select a genotype and return with phenotype

        :return: Person (namedTuple)
        """
        geno1 = select_genotype(self.trait1)
        pheno1 = self.all_phenos[geno1]
        if self.trait2 is not None:
            geno2 = select_genotype(self.trait2)
            pheno2 = self.all_phenos[geno2]
            gametes = (geno1[0] + geno2[0], geno1[1] + geno2[0],
                       geno1[0] + geno2[1], geno1[1] + geno2[1])
            return Person((geno1, geno2), {pheno1, pheno2}, set(gametes))
        return Person(geno1, {pheno1}, {geno1[0], geno1[1]})

    def make_offspring(self):
        """Combine parent genotypes to form kid genotypes

        :return: list of strings (genotypes)
        """
        if self.loci_num == 1:
            kids = [x + y for x, y in
                    itertools.product(self.mom.gametes, self.dad.gametes)]
        else:
            kids = [x[0] + y[0] + x[1] + y[1] for x, y in
                    itertools.product(self.mom.gametes, self.dad.gametes)]
        result = []
        for geno in kids:
            next_kid = ''
            if geno[1].isupper():
                next_kid += geno[1] + geno[0]
            else:
                next_kid += geno[0] + geno[1]
            if self.loci_num == 2:
                if geno[3].isupper():
                    next_kid += geno[3] + geno[2]
                else:
                    next_kid += geno[2] + geno[3]
            result.append(next_kid)
        return result

    def genotypic_ratio(self):
        """Calculate genotypic ratio of kids

        :return: list [(genotype, count of genotype), ...]
        """
        uniques = set(self.kids)
        geno_count = []
        for geno in uniques:
            geno_count.append((geno, self.kids.count(geno)))
        if len(geno_count[0][0]) == 4:
            multiple = 16 / sum([num for geno, num in geno_count])
        elif len(geno_count[0][0]) == 2:
            multiple = 4 / sum([num for geno, num in geno_count])
        else:
            raise ValueError('Kid genotypes should be 2 or 4 alleles.')
        geno_count = [(geno, int(num * multiple)) for geno, num in geno_count]
        geno_count.sort()
        return geno_count

    def phenotypic_ratio(self):
        """Calculate phenotypic ratio of kids

        :return: list [({phenotype}, count of phenotype), ...]
        """
        pheno_dict = {}
        for geno, count in self.kid_geno:
            geno = self.correct_grammar(geno)
            if len(geno) == 4:
                phenotype = (self.all_phenos[geno[:2]],
                             self.all_phenos[geno[2:]])
            elif len(geno) == 2:
                phenotype = tuple([self.all_phenos[geno]])
            else:
                raise ValueError('Genotype must consist of 2 or 4 alleles.')
            try:
                pheno_dict[phenotype] += count
            except KeyError:
                pheno_dict[phenotype] = count
        pheno_count = [(set(key), value) for key, value in pheno_dict.items()]
        pheno_count.sort()
        return pheno_count

    # region Questions
    def dom_type_question(self):
        """Ask how each trait is inherited (the type of dominance)

        :return: string (user response from gui.QuestionLoop)
        """

        prompt = ('\n\nPlease select the type of dominance for each trait '
                  'from the options below.')
        questions = ['How is {} inherited?'.format(x['name'])
                     for x in self.traits]

        converter = {'complete': 'complete dominance',
                     'incomplete': 'incomplete dominance',
                     'co-dom': 'co-dominance'}
        correct_answers = [converter[x['dom_type']] for x in self.traits]

        radio_choices = [DOMINANCE_TYPES for _ in self.traits]
        dom_solution = self.dom_type_solution()
        loop = gui.RadioLoop(title=BOX_TITLE,
                             prompt=self.info + '\n' + prompt,
                             questions=questions,
                             correct_answers=correct_answers,
                             solution=dom_solution,
                             choices=radio_choices)
        return loop.main_loop()

    def dom_type_solution(self):
        text = ""
        for trait in self.traits:
            dom = trait['alleles'][0].upper()
            rec = dom.lower()
            if trait['dom_type'] == "complete":
                text += ("In complete dominance, the dominant allele "
                         "({dom_allele}) completely masks the recessive "
                         "allele ({rec_allele}). So animals that have at "
                         "least one {dom_allele} allele "
                         "({dom_allele}{dom_allele} and "
                         "{dom_allele}{rec_allele} genotypes) have "
                         "{dom_pheno} and an animals that have only "
                         "{rec_allele} alleles ({rec_allele}{rec_allele} "
                         "genotype) have {rec_pheno}."
                         "".format(dom_allele=dom, rec_allele=rec,
                                   dom_pheno=trait['phenos'][dom + dom],
                                   rec_pheno=trait['phenos'][rec + rec]))
            if trait['dom_type'] == "incomplete":
                text += ("In incomplete dominance, heterozygotes "
                         "({dom_allele}{rec_allele}) have a phenotype that "
                         "is partway between the dominant phenotype "
                         "({dom_pheno}) and the recessive phenotype "
                         "({rec_pheno}). In this case, heterozygotes have "
                         "{hetero_pheno}, which is partway between "
                         "{dom_pheno} ({dom_allele}{dom_allele} genotype) "
                         "and {rec_pheno} ({rec_allele}{rec_allele} genotype)."
                         "".format(dom_allele=dom, rec_allele=rec.lower(),
                                   dom_pheno=trait['phenos'][dom + dom],
                                   rec_pheno=trait['phenos'][rec + rec],
                                   hetero_pheno=trait['phenos'][dom + rec]))
            if trait['dom_type'] == "co-dom":
                a = trait['alleles'][0]
                b = trait['alleles'][1]
                hetero = self.correct_grammar(a + b, target_trait=trait)
                text += ("In co-dominance, heterozygotes "
                         "({a_allele}{b_allele}) have a phenotype that "
                         "combines the phenotypes of two equally dominant "
                         "alleles ({a_allele} and {b_allele}). In this "
                         "case, heterozygotes have {hetero_pheno}, which is "
                         "a combination of {a_pheno} "
                         "({a_allele}{a_allele} genotype) and "
                         "{b_pheno} ({b_allele}{b_allele} genotype)."
                         "".format(a_allele=a, b_allele=b,
                                   hetero_geno=hetero,
                                   a_pheno=trait['phenos'][a + a],
                                   b_pheno=trait['phenos'][b + b],
                                   hetero_pheno=trait['phenos'][hetero]))
            text += "\n\n"

        return text

    def gamete_question(self):
        """Ask what gametes can be made for this PunnetSet

        :return: string (user response from gui.QuestionLoop)
        """
        prompt = ('\n\nPlease enter the gametes each parent can make below, '
                  'separated by spaces.')
        questions = ['What eggs can mom make?', 'What sperm can dad make?']
        correct_answers = [' '.join(self.mom.gametes),
                           ' '.join(self.dad.gametes)]

        gamete_solution = self.gamete_solution()
        loop = gui.QuestionLoop(title=BOX_TITLE,
                                prompt=self.info + '\n' + prompt,
                                questions=questions,
                                correct_answers=correct_answers,
                                solution=gamete_solution,
                                checker=self.check_gamete_answers)
        return loop.main_loop()

    def gamete_solution(self):
        """Create string explaining how to solve for parent gametes

        :return: string
        """
        text = 'Each gamete needs to have 1 and only 1 allele for each trait.\n'
        parent_words = {'dad': {'he': 'he', 'his': 'his', 'sperm': 'sperm',
                                'geno': ''.join(self.dad.genotype),
                                'gametes': ', '.join(self.dad.gametes)},
                        'mom': {'he': 'she', 'his': 'her', 'sperm': 'eggs',
                                'geno': ''.join(self.mom.genotype),
                                'gametes': ', '.join(self.mom.gametes)}}

        for parent in ('mom', 'dad'):
            target = parent_words[parent]
            if self.trait2:
                a, b, c, d = ''.join(target['geno'])
                text += (
                    '\n{Name} is {geno}. {He} has {A} and {B} alleles for '
                    '{trait1}. {He} has {C} and {D} alleles for {trait2}. '
                    '{His} first allele for {trait1} ({A}) can be paired up '
                    'with each of {his} alleles for {trait2} ({C} & {D}) '
                    'making two gametes ({sperm}): {A}{C} and {A}{D}. '
                    '{His} second allele for {trait1} ({B}) can be paired up '
                    'with each of {his} alleles for {trait2} ({C} & {D}) '
                    'making two gametes ({sperm}): {B}{C} and {B}{D}. '
                    'So {name} can make the following unique gametes: '
                    '{gametes}.\n'.format(
                        Name=parent.capitalize(), name=parent,
                        geno=target['geno'], A=a, B=b, C=c, D=d,
                        He=target['he'].capitalize(),
                        trait1=self.trait1['name'], trait2=self.trait2['name'],
                        His=target['his'].capitalize(), his=target['his'],
                        sperm=target['sperm'], gametes=target['gametes']))
            else:
                a, b = ''.join(target['geno'])
                text += (
                    '\n{Name} is {geno}. {He} has {A} and {B} alleles for '
                    '{trait1}. So {name} can make the following unique '
                    'gametes ({sperm}): {gametes}.\n'.format(
                        Name=parent.capitalize(), name=parent,
                        geno=target['geno'], A=a, B=b,
                        He=target['he'].capitalize(),
                        trait1=self.trait1['name'],
                        sperm=target['sperm'], gametes=target['gametes']))
        return text

    def check_gamete_answers(self, raw_answers):
        """Compare user answers (raw) to the gametes of this PunnetSet

        :param raw_answers: list of strings
        :return: list of booleans
        """
        formatted = [{self.correct_grammar(gamete, True)
                      for gamete in parent.split()} for parent in raw_answers]
        correct_answers = [self.mom.gametes, self.dad.gametes]
        result = [user == correct for user, correct in
                  zip(formatted, correct_answers)]
        return result

    def parent_phenotype_question(self):
        """Ask for the phenotypes of each parent in this PunnetSet

        :return: string (user response from gui.QuestionLoop)
        """
        prompt = ('\n\nPlease enter the phenotype of each parent below. '
                  'If the phenotype includes multiple traits, use "and" '
                  'between them. Ex: brown hair and blue eyes')
        questions = ["What is mom's phenotype?", "What is dad's phenotype?"]
        if self.loci_num == 1:
            correct_answers = [''.join(self.mom.phenotype),
                               ''.join(self.dad.phenotype)]
        else:
            correct_answers = [' and '.join(self.mom.phenotype),
                               ' and '.join(self.dad.phenotype)]

        parent_pheno_solution = self.parent_solution_for("pheno")

        loop = gui.QuestionLoop(title=BOX_TITLE,
                                prompt=self.info + '\n' + prompt,
                                questions=questions,
                                correct_answers=correct_answers,
                                solution=parent_pheno_solution,
                                checker=self.parent_phenotype_checker)
        return loop.main_loop()

    def parent_phenotype_checker(self, raw_answers):
        """Compare user answers (raw) to the parent phenotypes

        :param raw_answers: list of strings
        :return: list of booleans
        """
        formatted = [set(x.lower().split(' and ')) for x in raw_answers]
        correct_answers = [self.mom.phenotype, self.dad.phenotype]
        correct_answers = [set([x.lower() for x in parent])
                           for parent in correct_answers]
        result = [user == correct for user, correct in
                  zip(formatted, correct_answers)]
        return result

    def parent_genotype_question(self):
        """Ask for the genotypes of each parent in this PunnetSet

        :return: string (user response from gui.QuestionLoop)
        """

        prompt = ('\n\nPlease enter the genotype of each parent '
                  'in the boxes below.')
        questions = ["What is mom's genotype?", "What is dad's genotype?"]

        parent_geno_solution = self.parent_solution_for("geno")
        correct_answers = [self.correct_grammar(''.join(x))
                           for x in [self.mom.genotype, self.dad.genotype]]
        loop = gui.QuestionLoop(title=BOX_TITLE,
                                prompt=self.info + '\n' + prompt,
                                questions=questions,
                                correct_answers=correct_answers,
                                solution=parent_geno_solution,
                                checker=self.parent_genotype_checker)
        return loop.main_loop()

    def parent_solution_for(self, question_type):
        """Return solution for parent_genotype or parent_phenotype

        :param question_type: string
        :return: string
        """
        if question_type not in ["geno", "pheno"]:
            raise ValueError("question_type must be 'geno' or 'pheno'.")

        parent_words = {'dad': {'his': 'his', 'info':self.info_type[1],
                                'geno': ''.join(self.dad.genotype),
                                'pheno': ' and '.join(self.dad.phenotype)},
                        'mom': {'his': 'her', 'info':self.info_type[0],
                                'geno': ''.join(self.mom.genotype),
                                'pheno': ' and '.join(self.mom.phenotype)}}
        text = self.dom_type_solution() + "\n"
        type_words = {'pheno': {'self_long': 'phenotype', 'self_short': 'pheno',
                                'other_long': 'genotype', 'other_short': 'geno'},
                      'geno': {'self_long': 'genotype', 'self_short': "geno",
                               'other_long': 'phenotype', 'other_short': 'pheno'}}
        q_words = type_words[question_type]
        for person in ["mom", "dad"]:
            parent = parent_words[person]
            if parent["info"] == question_type:
                text += ("{name}’s {self_long} is given in the description of "
                         "the problem. ".format(name=person.capitalize(),
                                                self_long=q_words['self_long']))
            if parent["info"] == q_words['other_short']:
                text += ("{name}’s {other_long} is {other_calc_ed}. "
                         "Therefore, {his} {self_long} is {self_calc_ed}. "
                         "".format(name=person.capitalize(), his=parent["his"],
                                   other_long=q_words['other_long'],
                                   self_long=q_words['self_long'],
                                   other_calc_ed=parent[q_words['other_short']],
                                   self_calc_ed=parent[q_words['self_short']]))
            if parent["info"] == "zygous":
                zygous_type = " and ".join(self.make_zygous(parent["geno"]))
                text += ("Homozygous means having two of the same allele. "
                         "Heterozygous means having two different alleles. "
                         "Since we know {name} is {zygous}, we can "
                         "conclude that {name} is {geno}"
                         "".format(name=person, his=parent["his"],
                                   geno=parent["geno"], pheno=parent["pheno"],
                                   zygous=zygous_type))
                if question_type == "pheno":
                    text += (" and {his} phenotype is {pheno}. "
                             "".format(his=parent["his"],
                                       pheno=parent["pheno"]))
                else:
                    text += ". "

        return text

    def parent_genotype_checker(self, raw_answers):
        """Compare user answers (raw) to the parent genotypes

        :param raw_answers: list of strings
        :return: list of booleans
        """
        formatted = [self.correct_grammar(geno) for geno in raw_answers ]
        correct_answers = [self.correct_grammar(''.join(x))
                           for x in [self.mom.genotype, self.dad.genotype]]
        result = [user == correct for user, correct in
                  zip(formatted, correct_answers)]
        return result

    def kid_phenotype_question(self):
        """Ask for the phenotypic ratio of children for this PunnetSet

        :return: string (user response from gui.QuestionLoop)
        """
        prompt = ('\n\nPlease enter the phenotypic ratio of the offspring '
                  'below. Include a single phenotype in each box, along with '
                  'the number number of offspring that will have that '
                  'phenotype. Some boxes may remain blank.')
        if self.trait2 is None:
            joiner = ""
        else:
            joiner = " and "
        correct_answers = [str(num) + ' ' + joiner.join(pheno)
                           for pheno, num in self.kid_pheno]
        if len(correct_answers) <= 4:
            entry_num = 4
        elif len(correct_answers) <= 6:
            entry_num = 6
        else:
            entry_num = 9
        questions = [""] * entry_num
        kid_phenotype_solution = (
            'To answer this question you should construct a punnet square '
            'like the one shown below. Then you need to count the number of '
            'squares (representing children) with each unique phenotype. '
            'The phenotype ratio of this problem is: {}').format(
            ': '.join(['{} {}'.format(num, ' and '.join(phenos))
                      for phenos, num in self.kid_pheno]))
        kid_phenotype_table = self.make_pheno_square(self.make_geno_square())
        loop = gui.QuestionLoop(title=BOX_TITLE,
                                prompt=self.info + '\n' + prompt,
                                questions=questions,
                                correct_answers=correct_answers,
                                solution=kid_phenotype_solution,
                                checker=self.kid_phenotype_checker,
                                solution_table=kid_phenotype_table)
        return loop.main_loop()

    @staticmethod
    def multi_answer_checker(formatted, correct):
        """Determine if all formatted are in correct without repeats

        :param formatted: list of strings or tuples
        :param correct: list of strings or tuples
        :return: list of booleans
        """
        correct_list = []
        correct_copy = correct[:]
        for answer in formatted:
            try:
                correct_copy.remove(answer)
                correct_list.append(True)
            except ValueError:
                correct_list.append(False)

        len_dif = len(correct) - len(correct_list)
        if len_dif > 0:
            for _ in range(len_dif):
                correct_list.append(False)
        return correct_list

    def kid_phenotype_checker(self, raw_answers):
        """Compare user answers (raw) to the kid phenotypic ratio.

        Compare to both the full ratio and the reduced ratio.
        Return the comparison with the most TRUEs

        :param raw_answers: list of strings
        :return: list of booleans
        """
        numeric_answers = []
        for phrase in raw_answers:
            if phrase:
                if phrase[0].isnumeric():
                    numeric_answers.append(phrase[0])
                else:
                    numeric_answers.append('0')
            else:
                numeric_answers.append('0')
        pheno_answers = [x.replace(num, '').strip().lower()
                         for x, num in zip(raw_answers, numeric_answers)]
        formatted_answers = [(set(phrase), int(num)) for phrase, num in zip(
            [set(x.lower().split(' and ')) for x in pheno_answers],
            numeric_answers)]
        correct_list = self.multi_answer_checker(formatted_answers,
                                                 self.kid_pheno)
        reduced_correct_list = self.multi_answer_checker(formatted_answers,
                                                         self.kid_pheno_reduced)

        if sum(reduced_correct_list) > sum(correct_list):
            return reduced_correct_list
        else:
            return correct_list

    def kid_genotype_question(self):
        """Ask for the genotypic ratio of children for this PunnetSet

        :return: string (user response from gui.QuestionLoop)
        """
        prompt = ('\n\nPlease enter the genotypic ratio of the offspring '
                  'below. Include a single genotype in each box, along with '
                  'the number number of offspring that will have that '
                  'genotype. Some boxes may remain blank.')
        kid_geno_solution = (
            'To answer this question you should construct a punnet square '
            'like the one shown below. Then you need to count the number of '
            'squares (representing children) with each unique genotype. '
            'The genotype ratio of this problem is: {}').format(
            ': '.join(['{} {}'.format(num, geno)
                      for geno, num in self.kid_geno]))
        kid_geno_table = self.make_geno_square()
        correct_answers = ['{} {}'.format(num, geno)
                           for geno, num in self.kid_geno]

        if len(correct_answers) <= 4:
            entry_num = 4
        elif len(correct_answers) <= 6:
            entry_num = 6
        else:
            entry_num = 9
        questions = [""] * entry_num
        loop = gui.QuestionLoop(title=BOX_TITLE,
                                prompt=self.info + '\n' + prompt,
                                questions=questions,
                                correct_answers=correct_answers,
                                solution=kid_geno_solution,
                                checker=self.kid_genotype_checker,
                                solution_table=kid_geno_table)
        return loop.main_loop()

    def kid_genotype_checker(self, raw_answers):
        """Compare user answers (raw) to the kid genotypic ratio.

        Compare to both the full ratio and the reduced ratio.
        Return the comparison with the most TRUEs

        :param raw_answers: list of strings
        :return: list of booleans
        """

        num_answers = [int(word) for phrase in raw_answers
                       for word in phrase.split() if word.isnumeric()]
        geno_answers = [self.correct_grammar(word)
                        for phrase in raw_answers for word in phrase.split()
                        if not word.isnumeric()]
        formatted_answers = list(zip(geno_answers, num_answers))

        correct_list = self.multi_answer_checker(formatted_answers,
                                                 self.kid_geno)
        reduced_correct_list = self.multi_answer_checker(formatted_answers,
                                                         self.kid_geno_reduced)

        if sum(reduced_correct_list) > sum(correct_list):
            return reduced_correct_list
        else:
            return correct_list
    # endregion

    def ask(self):
        """Ask all appropriate questions for this PunnetSet

        :return: string, int, int (response, points earned, points possible)
        """
        question_list = [self.dom_type_question,
                         self.parent_phenotype_question,
                         self.parent_genotype_question,
                         self.gamete_question,
                         self.kid_genotype_question,
                         self.kid_phenotype_question]

        if all([x == 'geno' for x in self.info_type]):
            question_list.remove(self.parent_genotype_question)
        if all([x == 'pheno' for x in self.info_type]):
            question_list.remove(self.parent_genotype_question)
        if self.loci_num == 2:
            question_list.remove(self.kid_genotype_question)

        for question in question_list:
            response = question()
            if response in ("Main Menu", "Exit", None):
                return response
        return response


def ask_questions(prob_type='both'):
    """Sequentially ask all question for a PunnetSet

    :param prob_type: string (1, 2, or both)
    :return: None
    """
    want_more = True
    while want_more:
        want_more = False
        if prob_type == 'both':
            num = random.choice([1, 2])
            question = PunnetSet(num)
        elif prob_type == '2':
            question = PunnetSet(2)
        else:
            question = PunnetSet(1)
        response = question.ask()
        if response == "New Question":
            want_more = True



def run():
    """Select type of PunnetSet for questions

    :return: string (user response)
    """

    window = gui.SimpleWindow(
        title=BOX_TITLE, msg=('Which type of punnet square problems '
                              'would you like to practice?'),
        buttons=['One trait', 'Two trait', 'One and two trait',
                 'Main Menu', 'Exit Program'])
    window.run()
    user_choice = window.clicked
    if user_choice == 'One trait':
        ask_questions('1')
    elif user_choice == 'Two trait':
        ask_questions('2')
    elif user_choice == 'One and two trait':
        ask_questions('both')
    elif user_choice == 'Main Menus':
        main.run()
    return user_choice

if __name__ == "__main__":
    run()
