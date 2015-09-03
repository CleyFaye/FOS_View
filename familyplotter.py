#!/usr/bin/env python

from datahandle import Vault
from codecs import open

def getColorFromId(Id):
    Id = Id % 10
    if Id == 0:
        return 'red'
    elif Id == 1:
        return 'green'
    elif Id == 2:
        return 'blue'
    elif Id == 3:
        return 'cyan'
    elif Id == 4:
        return 'magenta'
    elif Id == 5:
        return 'yellow'
    elif Id == 6:
        return 'pink'
    elif Id == 7:
        return 'palegreen'
    elif Id == 8:
        return 'navy'
    elif Id == 9:
        return 'sienna'

def incCoupleCounter(dweller):
    try:
        dweller.couplesCount = dweller.couplesCount + 1
    except AttributeError:
        dweller.couplesCount = 1

def getCoupleCounter(dweller):
    try:
        return dweller.couplesCount
    except AttributeError:
        return 0

def setDwellerFirstCoupleRole(dweller, role):
    if role == 'couple0':
        raise Exception("pills here")
    try:
        return dweller.firstCouple
    except AttributeError:
        dweller.firstCouple = role

def getDwellerFirstCouple(dweller):
    return dweller.firstCouple

def setAsChild(dweller):
    dweller.isAChild = True

def isAChild(dweller):
    try:
        return dweller.isAChild
    except AttributeError:
        return False

def addOutputNodeToDweller(dweller, name):
    try:
        if name not in dweller.roles:
            dweller.roles.append(name)
    except AttributeError:
        dweller.roles = [name]

def getRoles(dweller):
    try:
        return dweller.roles
    except AttributeError:
        return ['dweller_%s_solonely' % dweller.serializeId]

class Couple(object):
    counter = 0

    def __init__(self, father, mother):
        self.father = father
        self.mother = mother
        [incCoupleCounter(x) for x in (father,mother)]
        self.index = Couple.counter
        Couple.counter = Couple.counter + 1

    def isParentOf(self, dweller):
        try:
            rel = dweller.relations
            l = rel.ascendants[0]
            r = rel.ascendants[1]
            return l == self.father and r == self.mother
        except AttributeError:
            return False

    def coupleId(self):
        return 'couple%s' % self.index

    def mergedDotName(self):
        fatherDot = dwellerDotName(self.father, self.coupleId())
        motherDot = dwellerDotName(self.mother, self.coupleId())
        return '%sAnd%s' % (fatherDot, motherDot)

    def dotOutput(self, output):
        fatherDot = dwellerDotName(self.father, self.coupleId())
        motherDot = dwellerDotName(self.mother, self.coupleId())
        mergeNode = self.mergedDotName()
        output.write('subgraph couple_%s_graph {\n' % self.index)
        output.write('rankdir=LR\n')
        output.write('style=invis\n')
        output.write('rank=same\n')
        output.write('%s\n' % fatherDot)
        output.write('%s\n' % motherDot)
        output.write('%s [shape=point]\n' % mergeNode)
        output.write('%s -> %s [dir=none,weight=1000,penwidth=2,color=%s]\n' % (fatherDot, mergeNode, getColorFromId(self.index)))
        output.write('%s -> %s [dir=none,weight=1000,penwidth=2,color=%s]\n' % (mergeNode, motherDot, getColorFromId(self.index)))
        output.write('}\n')

    @staticmethod
    def create(dwellers):
        couplesDwellers = []
        for dweller in dwellers:
            try:
                rel = dweller.relations
                father = rel.ascendants[0]
                mother = rel.ascendants[1]
            except AttributeError:
                father = None
                mother = None
            if father:
                couple = {'father': father, 'mother': mother}
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
        [setAsChild(x) for x in brothers]
        self.index = Brotherhoods.counter
        Brotherhoods.counter = Brotherhoods.counter + 1

    def dotOutput(self, output):
        lvl1Node = '%sSons' % self.parents.mergedDotName()
        output.write('subgraph brotherhood_lvl1_%s_graph {\n' % self.index)
        output.write('rankdir=LR\n')
        output.write('style=invis\n')
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
                name = dwellerDotName(brother, 'topnode')
                output.write('%s [shape=point]\n' % name)
            else:
                name = lvl1Node
            if not needMiddle:
                if index == leftLink:
                    output.write('%s->%s [dir=none,color=gray]\n' % (name, lvl1Node))
                if index == rightLink:
                    output.write('%s->%s [dir=none,color=gray]\n' % (lvl1Node, name))
            left = right
            right = name
            if index > 1:
                if needMiddle or index != rightLink:
                    output.write('%s->%s [dir=none,color=gray]\n' %(left, right))
            index = index + 1
        output.write('}\n')
        if False:
            output.write('subgraph brotherhood_%s_graph {\n' % self.index)
            output.write('rankdir=LR\n')
            output.write('style=invis\n')
            output.write('rank=same\n')
            for brother in self.brothers:
                output.write('%s\n' % dwellerDotName(brother, 'child'))
            output.write('}\n')
        index = 1
        for brother in self.brothers:
            if index == middle:
                topName = lvl1Node
            else:
                topName = dwellerDotName(brother, 'topnode')
            output.write('%(top)s->%(id)s [dir=none,color="gray"]\n' % {'top': topName, 'id': dwellerDotName(brother, 'child')})
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

def dwellerDotName(dweller, role):
    # Here's how I'll do it:
    # If we want a "topnode" node, always give it. It is used for structure.
    # If we want a "child" node, always give id. Child nodes can only happen once.
    # If we want a coupleX node...
    # - if the dweller is only in ONE couple, return either the "child" node, or the "unique" node, whichever exist.
    # - if the dweller is part of multiple couples, produce multiple "coupleX" nodes. Later, if:
    #   - the dweller is also a child, link them to the child node
    #   - the dweller is not a child, link all "secondary" coupleX nodes to the couple0 node
    if role == 'topnode':
        name = 'dweller_%s_topnode' % dweller.serializeId
    elif role == 'child':
        name = 'dweller_%s_child' % dweller.serializeId
        addOutputNodeToDweller(dweller, name)
    else:
        if getCoupleCounter(dweller) == 1:
            if isAChild(dweller):
                name = dwellerDotName(dweller, 'child')
            else:
                name = 'dweller_%s_%s' % (dweller.serializeId, role)
                addOutputNodeToDweller(dweller, name)
                setDwellerFirstCoupleRole(dweller, name)
        else:
            name = 'dweller_%s_%s' % (dweller.serializeId, role)
            addOutputNodeToDweller(dweller, name)
            setDwellerFirstCoupleRole(dweller, name)
    return name

def specialString(dweller):
    try:
        stats = dweller.stats
    except AttributeError:
        return ''
    merged = {}
    for statName in 'SPECIAL':
        merged[statName] = stats.get(statName).getFullValue()
    return 'S:%(S)s P:%(P)s E:%(E)s\\nC:%(C)s I:%(I)s A:%(A)s\\nL%(L)s' % merged

def dotOutputDweller(dweller, output):
    roles = getRoles(dweller)
    for role in roles:
        try:
            if dweller.gender == 1:
                outlineColor = 'pink'
            else:
                outlineColor = 'blue'
            if dweller.health.healthValue <= 0:
                backgroundColor = 'gray'
            else:
                backgroundColor = 'white'
        except AttributeError:
            outlineColor = 'black'
            backgroundColor = 'red'
        label = '%s\\n%s' % (dweller.getFullName(), specialString(dweller))
        output.write('%(id)s [shape=box,label="%(label)s",color="%(outline)s",bgcolor="%(bg)s"]\n' % {'id': role, 'label': label, 'outline': outlineColor, 'bg': backgroundColor})
    if getCoupleCounter(dweller) > 10000:
        for role in roles:
            if role[-5:] == 'child':
                continue
            if isAChild(dweller):
                output.write('%s -> %s [weight=-1000,style=dotted]\n' % (role, dwellerDotName(dweller, 'child')))

def main(config):
    vault = Vault('data/VaultEd.sav')
    couples = Couple.create(vault.dwellers.dwellers)
    brotherhoods = Brotherhoods.create(vault.dwellers.dwellers, couples)
    with open('family.dot' ,'w', encoding='utf-8') as output:
        output.write('digraph A {\n')
        output.write('rankdir=TB\n')
        for couple in couples:
            couple.dotOutput(output)
        for brotherhood in brotherhoods:
            brotherhood.dotOutput(output)
        for dweller in vault.dwellers.dwellers:
            if dweller.serializeId == 1005:
                print 'derp'
                print dweller
            dotOutputDweller(dweller, output)
        output.write('}\n')

if __name__ == '__main__':
    config = {}
    main(config)
