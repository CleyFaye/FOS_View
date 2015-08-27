import json
from decrypt import decrypt

def loadFromDico(dico, className):
    if className:
        return globals()[className](dico)
    else:
        return dico

def loadProp(obj, dico, prop):
    if prop == 'id':
        setattr(obj, 'ID', dico['id'])
    elif prop == 'type':
        setattr(obj, 'TYPE', dico['type'])
    else:
        openIndex = prop.find('(')
        closeIndex = prop.find(')')
        if openIndex != -1:
            className = prop[openIndex+1:closeIndex]
            prop = prop[:openIndex]
        else:
            className = None
        if prop[0:1] == '_':
            prop = prop[1:]
            result = []
            for subDic in dico[prop]:
                newInstance = loadFromDico(subDic, className)
                result.append(newInstance)
        else:
            if not prop in dico:
                result = None
            else:
                result = loadFromDico(dico[prop], className)
        if result is not None:
            setattr(obj, prop, result)

def loadProps(obj, dico, propList):
    for prop in propList:
        loadProp(obj, dico, prop)

class DeathclawManager(object):
    def __init__(self, dico):
        loadProps(self, dico, ['canDeathclawEmergencyOccurs', 'deathclawCooldownID', 'deathclawTotalExtraChance'])

    def __str__(self):
        return 'DeathclawManager'

class ConstructManager(object):
    def __init__(self, dico):
        loadProps(self, dico, ['roomDeserializeID'])

    def __str__(self):
        return 'ConstructManager'

class EquipmentItem(object):
    def __init__(self, dico):
        loadProps(self, dico, ['hasBeenAssigned', 'hasRandonWeaponBeenAssigned', 'id', 'type'])

    def __str__(self):
        return 'Item(%s,%s)' % (self.TYPE, self.ID)

class Inventory(object):
    def __init__(self, dico):
        self.items = []
        for obj in dico['items']:
            self.items.append(EquipmentItem(obj))

    def __str__(self):
        return 'Inventory[%s]' % [str(i) for i in self.items]

class StorageBonus(object):
    def __init__(self, dico):
        loadProps(self, dico, ['Energy', 'Food', 'Lunchbox', 'Nuka', 'RadAway', 'StimPack', 'Water'])

    def __str__(self):
        return 'Bonus[Energy=%s, Food=%s, Lunchbox=%s, Nuka=%s, RadAway=%s, StimPack=%s, Water=%s]' % (self.Energy, self.Food, self.Lunchbox, self.Nuka, self.RadAway, self.StimPack, self.Water)

class StorageResources(object):
    def __init__(self, dico):
        loadProps(self, dico, ['Energy', 'Food', 'Lunchbox', 'Nuka', 'RadAway', 'StimPack', 'Water'])

    def __str__(self):
        return 'Resources[Energy=%s, Food=%s, Lunchbox=%s, Nuka=%s, RadAway=%s, StimPack=%s, Water=%s]' % (self.Energy, self.Food, self.Lunchbox, self.Nuka, self.RadAway, self.StimPack, self.Water)

class Storage(object):
    def __init__(self, dico):
        loadProps(self, dico, ['bonus(StorageBonus)', 'resources(StorageResources)'])

    def __str__(self):
        return 'Storage[%s,%s]' % (str(self.bonus), str(self.resources))

class Equipment(object):
    def __init__(self, dico):
        loadProps(self, dico, ['inventory(Inventory)', 'storage(Storage)'])

    def __str__(self):
        return 'Equipment[%s]' % str(self.inventory)

class Experience(object):
    def __init__(self, dico):
        loadProps(self, dico, ['accum', 'currentLevel', 'experienceValue', 'needLvUp', 'storage', 'wastelandExperience'])

    def __str__(self):
        return 'exp=%s' % self.experienceValue

class Happiness(object):
    def __init__(self, dico):
        loadProps(self, dico, ['happinessValue'])

    def __str__(self):
        return 'happiness=%s' % self.happinessValue

class Health(object):
    def __init__(self, dico):
        loadProps(self, dico, ['healthValue', 'lastLevelUpdated', 'maxHealth', 'permaDeath', 'radiationValue'])

    def __str__(self):
        return 'health=%s/%s (-%s)' % (self.healthValue, self.maxHealth, self.radiationValue)

class Relations(object):
    def __init__(self, dico):
        loadProps(self, dico, ['_ascendants', 'lastPartner', 'partner', '_relations'])

    def __str__(self):
        if self.ascendants[0] == None:
            parents = None
        else:
            parents = 'parents=(%s,%s)' % (self.ascendants[0].getFullName(), self.ascendants[1].getFullName())
        if self.lastPartner == None:
            lastPartner = None
        else:
            lastPartner = self.lastPartner.getFullName()
        if self.partner == None:
            partner = None
        else:
            partner = self.partner.getFullName()
        if partner is None and lastPartner is not None:
            partner = lastPartner
        if parents is None:
            result = ''
        else:
            result = parents
        if partner is not None:
            if result == '':
                result = 'partner:%s' % partner
            else:
                result = '%s,partner:%s' % (result, partner)
        return result

    def mergeDwellers(self, dwellers):
        for i in range(6):
            self.ascendants[i] = dwellers.findDwellerFromId(self.ascendants[i])
        self.lastPartner = dwellers.findDwellerFromId(self.lastPartner)
        self.partner = dwellers.findDwellerFromId(self.partner)

class Stat(object):
    def __init__(self, dico):
        loadProps(self, dico, ['exp', 'mod', 'value'])

    def __str__(self):
        if self.mod:
            return str(self.value) + '+' + str(self.mod) + '(' + str(self.value + self.mod) + ')'
        else:
            return str(self.value)

class Stats(object):
    def __init__(self, dico):
        loadProps(self, dico, ['_stats(Stat)'])

    def __str__(self):
        return 'S=%s,P=%s,E=%s,C=%s,I=%s,A=%s,L=%s' % (str(self.stats[1]), str(self.stats[2]), str(self.stats[3]), str(self.stats[4]), str(self.stats[5]), str(self.stats[6]), str(self.stats[7]))

class Dweller(object):
    def __init__(self, dico):
        loadProps(self, dico, ['WillGoToWasteland', 'assigned', 'babyReady', 'deathTime', 'gender', 'hair', 'hairColor', 'lastChildBorn', 'lastName', 'name', 'outfitColor', 'pendingExperienceReward', 'pregnant', 'rarity', 'savedRoom', 'sawIncident', 'serializeId', 'skinColor', 'equipedOutfit(EquipmentItem)', 'equipedWeapon(EquipmentItem)', 'equipment(Equipment)', 'experience(Experience)', 'happiness(Happiness)', 'health(Health)', 'relations(Relations)', 'stats(Stats)', 'faceMask', 'daysOnWasteland', 'hoursOnWasteland', 'uniqueData'])

    def getFullName(self):
        return self.name + ' ' + self.lastName

    def getGender(self):
        if self.gender == 2:
            return 'Male'
        else:
            return 'Female'

    def __str__(self):
        family = str(self.relations)
        if family == '':
            return '%(name)s[%(rarity)s %(gender)s, %(health)s, %(outfit)s, %(weapon)s, %(equipment)s, %(exp)s exp., %(happy)s %%]' % {
                    'name': self.getFullName(),
                    'rarity': self.rarity,
                    'gender': self.getGender(),
                    'health': str(self.health),
                    'outfit': str(self.equipedOutfit),
                    'weapon': str(self.equipedWeapon),
                    'equipment': str(self.equipment),
                    'exp': str(self.experience),
                    'happy': str(self.happiness)
                    }
        else:
            return '%(name)s[%(rarity)s %(gender)s, %(health)s, %(outfit)s, %(weapon)s, %(equipment)s, %(exp)s exp., %(happy)s %%, family=%(family)s]' % {
                    'name': self.getFullName(),
                    'rarity': self.rarity,
                    'gender': self.getGender(),
                    'health': str(self.health),
                    'outfit': str(self.equipedOutfit),
                    'weapon': str(self.equipedWeapon),
                    'equipment': str(self.equipment),
                    'exp': str(self.experience),
                    'happy': str(self.happiness),
                    'family': family
                    }

    def mergeDwellers(self, dwellers):
        self.lastChildBorn = dwellers.findDwellerFromId(self.lastChildBorn)
        self.relations.mergeDwellers(dwellers)

class Handy(object):
    def __init__(self, dico):
        raise Exception('I don\'t know anything about Mr. Handys... yet:%s' % dico)

class DwellersList(object):
    def __init__(self, dico):
        loadProps(self, dico, ['_dwellers(Dweller)', 'id', 'min_happiness', '_mrHandys(Handy)', 'mrhId'])

    def __str__(self):
        return ','.join([str(x) for x in self.dwellers])

    def findDwellerFromId(self, dwellerId):
        for dweller in self.dwellers:
            if dweller.serializeId == dwellerId:
                return dweller
        return None

class VaultInfo(object):
    def __init__(self, dico):
        loadProps(self, dico, ['Achievements', 'LunchBoxesByType', 'LunchBoxesCount', 'VaultName', 'dwellerFoodConsumption', 'dwellerWaterConsumption', 'emergencyData', 'inventory', 'rocks', 'roomConsumption', 'rooms', 'storage', 'wasteland'])

    def __str__(self):
        return 'Vault %s' % self.VaultName

class Vault(object):
    def __init__(self, srcFile):
        jsonStr = decrypt(srcFile)
        jsonObj = json.loads(jsonStr)
        loadProps(self, jsonObj, ['DeathclawManager(DeathclawManager)', 'LunchBoxCollectWindow', 'PromoCodesWindow', 'constructMgr(ConstructManager)', 'deviceName', 'dwellerSpawner', 'dwellers(DwellersList)', 'happinessManager', 'localNotificationMgr', 'objectiveMgr', 'ratingMgr', 'refugeeSpawner', 'survivalW', 'swrveEventsManager', 'taskMgr', 'timeMgr', 'tutorialManager', 'unlockableMgr', 'vault(VaultInfo)'])
        self.mergeDwellers()

    def mergeDwellers(self):
        """Replace dwellers integer references by actual object references"""
        for dweller in self.dwellers.dwellers:
            dweller.mergeDwellers(self.dwellers)

    def __str__(self):
        return str(self.vault) + ',dwellers=[' + str(self.dwellers) + ']'

if __name__ == '__main__':
    raise Exception('This program cannot run in DOS mode')

