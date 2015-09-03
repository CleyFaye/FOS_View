#!/usr/bin/env python

from datahandle import Vault
from codecs import open

class Couple(object):
    counter = 0

    def __init__(self, father, mother):
        self.father = father
        self.mother = mother
        self.index = Couple.counter
        Couple.counter = Couple.counter + 1

    def isParentOf(self, dweller):
        rel = dweller.relations
        l = rel.ascendants[0]
        r = rel.ascendants[1]
        return (l == self.father and r == self.mother) or (l == self.mother and r == self.father)

    def mergedDotName(self):
        fatherDot = dwellerDotName(self.father)
        motherDot = dwellerDotName(self.mother)
        return '%sAnd%s' % (fatherDot, motherDot)

    def dotOutput(self, output):
        fatherDot = dwellerDotName(self.father)
        motherDot = dwellerDotName(self.mother)
        mergeNode = self.mergedDotName()
        output.write('subgraph couple_%s_graph {\n' % self.index)
        output.write('rank=same\n')
        output.write('%s\n' % fatherDot)
        output.write('%s\n' % motherDot)
        output.write('%s [shape=point]\n' % mergeNode)
        output.write('%s -> %s [dir=none]\n' % (fatherDot, mergeNode))
        output.write('%s -> %s [dir=none]\n' % (mergeNode, motherDot))
        output.write('}\n')

    @staticmethod
    def create(dwellers):
        couplesDwellers = []
        for dweller in dwellers:
            rel = dweller.relations
            if rel.ascendants[0]:
                if rel.ascendants[0].gender == 2:
                    couple = {'father': rel.ascendants[0], 'mother': rel.ascendants[1]}
                else:
                    couple = {'father': rel.ascendants[1], 'mother': rel.ascendants[0]}
                if couple not in couplesDwellers:
                    couplesDwellers.append(couple)
        result = []
        for coupleDwellers in couplesDwellers:
            result.append(Couple(**coupleDwellers))
        return result

class Brotherhoods(object):
    counter = 0

    def __init__(self, brothers, couple):
        self.brothers = brothers[:]
        self.parents = couple
        self.index = Brotherhoods.counter
        Brotherhoods.counter = Brotherhoods.counter + 1

    def dotOutput(self, output):
        lvl1Node = '%sSons' % self.parents.mergedDotName()
        output.write('subgraph brotherhood_lvl1_%s_graph {\n' % self.index)
        output.write('rank=same\n')
        output.write('%s [shape=point]\n' % lvl1Node)
        index = 1
        count = len(self.brothers)
        needMiddle = count % 2 == 1
        if needMiddle:
            middle = count / 2 + 1
        else:
            middle = 0
            leftLink = count / 2
            rightLink = count / 2 + 1
        right = None
        for brother in self.brothers:
            if index != middle:
                name = '%s_top' % dwellerDotName(brother)
                output.write('%s [shape=point]\n' % name)
            else:
                name = lvl1Node
            if not needMiddle:
                if index == leftLink:
                    output.write('%s->%s [dir=none]\n' % (name, lvl1Node))
                if index == rightLink:
                    output.write('%s->%s [dir=none]\n' % (lvl1Node, name))
            left = right
            right = name
            if index > 1:
                output.write('%s->%s [dir=none]\n' %(left, right))
            index = index + 1
        output.write('}\n')
        if False:
            output.write('subgraph brotherhood_%s_graph {\n' % self.index)
            output.write('rank=same\n')
            for brother in self.brothers:
                output.write('%s\n' % dwellerDotName(brother))
            output.write('}\n')
        index = 1
        for brother in self.brothers:
            if index == middle:
                topName = lvl1Node
            else:
                topName = '%s_top' % dwellerDotName(brother)
            output.write('%(top)s->%(id)s [dir=none]\n' % {'top': topName, 'id': dwellerDotName(brother)})
            index = index + 1
        output.write('%s->%s [dir=none]\n' % (self.parents.mergedDotName(), lvl1Node))

    @staticmethod
    def create(dwellers, couples):
        result = []
        for couple in couples:
            brothers = []
            for dweller in dwellers:
                if couple.isParentOf(dweller):
                    brothers.append(dweller)
            if brothers:
                result.append(Brotherhoods(brothers, couple))
        return result

def dwellerDotName(dweller):
    return 'dweller_%s' % dweller.serializeId

def specialString(dweller):
    stats = dweller.stats
    merged = {}
    for statName in 'SPECIAL':
        merged[statName] = stats.get(statName).getFullValue()
    return 'S:%(S)s P:%(P)s E:%(E)s\\nC:%(C)s I:%(I)s A:%(A)s\\nL%(L)s' % merged

def dotOutputDweller(dweller, output):
    if dweller.gender == 1:
        outlineColor = 'pink'
    else:
        outlineColor = 'blue'
    if dweller.health.healthValue <= 0:
        backgroundColor = 'gray'
    else:
        backgroundColor = 'white'
    label = '%s\\n%s' % (dweller.getFullName(), specialString(dweller))
    output.write('%(id)s [shape=box,label="%(label)s",color="%(outline)s",bgcolor="%(bg)s"]\n' % {'id': dwellerDotName(dweller), 'label': label, 'outline': outlineColor, 'bg': backgroundColor})

def main(config):
    vault = Vault('data/Vault1.sav')
    couples = Couple.create(vault.dwellers.dwellers)
    brotherhoods = Brotherhoods.create(vault.dwellers.dwellers, couples)
    with open('family.dot' ,'w', encoding='utf-8') as output:
        output.write('digraph A {\n')
        for dweller in vault.dwellers.dwellers:
            dotOutputDweller(dweller, output)
        for couple in couples:
            couple.dotOutput(output)
        for brotherhood in brotherhoods:
            brotherhood.dotOutput(output)
        output.write('}\n')

if __name__ == '__main__':
    config = {}
    main(config)
