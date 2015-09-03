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
    elif prop == 'class':
        setattr(obj, 'className', dico['class'])
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

class VaultObject(object):
    def __init__(self, dico):
        loadProps(self, dico, self.__class__.AUTOPROPS)

class DeathclawManager(VaultObject):
    AUTOPROPS = ['canDeathclawEmergencyOccurs', 'deathclawCooldownID', 'deathclawTotalExtraChance']
    def __str__(self):
        return 'DeathclawManager'

class ConstructManager(VaultObject):
    AUTOPROPS = ['roomDeserializeID']
    def __str__(self):
        return 'ConstructManager'

class EquipmentItem(VaultObject):
    AUTOPROPS = ['hasBeenAssigned', 'hasRandonWeaponBeenAssigned', 'id', 'type']
    def __str__(self):
        return 'Item(%s,%s)' % (self.TYPE, self.ID)

class Inventory(VaultObject):
    AUTOPROPS = ['_items(EquipmentItem)']
    def __str__(self):
        return 'Inventory[%s]' % [str(i) for i in self.items]

class StorageBonus(VaultObject):
    AUTOPROPS = ['Energy', 'Food', 'Lunchbox', 'Nuka', 'RadAway', 'StimPack', 'Water']
    def __str__(self):
        return 'Bonus[Energy=%s, Food=%s, Lunchbox=%s, Nuka=%s, RadAway=%s, StimPack=%s, Water=%s]' % (self.Energy, self.Food, self.Lunchbox, self.Nuka, self.RadAway, self.StimPack, self.Water)

class StorageResources(VaultObject):
    AUTOPROPS = ['Energy', 'Food', 'Lunchbox', 'Nuka', 'RadAway', 'StimPack', 'Water']
    def __str__(self):
        return 'Resources[Energy=%s, Food=%s, Lunchbox=%s, Nuka=%s, RadAway=%s, StimPack=%s, Water=%s]' % (self.Energy, self.Food, self.Lunchbox, self.Nuka, self.RadAway, self.StimPack, self.Water)

class Storage(VaultObject):
    AUTOPROPS = ['bonus(StorageBonus)', 'resources(StorageResources)']
    def __str__(self):
        return 'Storage[%s,%s]' % (str(self.bonus), str(self.resources))

class Equipment(VaultObject):
    AUTOPROPS = ['inventory(Inventory)', 'storage(Storage)']
    def __str__(self):
        return 'Equipment[%s]' % str(self.inventory)

class Experience(VaultObject):
    AUTOPROPS = ['accum', 'currentLevel', 'experienceValue', 'needLvUp', 'storage', 'wastelandExperience']
    def __str__(self):
        return 'exp=%s' % self.experienceValue

class Happiness(VaultObject):
    AUTOPROPS = ['happinessValue']
    def __str__(self):
        return 'happiness=%s' % self.happinessValue

class Health(VaultObject):
    AUTOPROPS = ['healthValue', 'lastLevelUpdated', 'maxHealth', 'permaDeath', 'radiationValue']
    def __str__(self):
        return 'health=%s/%s (-%s)' % (self.healthValue, self.maxHealth, self.radiationValue)

class Relations(VaultObject):
    AUTOPROPS = ['_ascendants', 'lastPartner', 'partner', '_relations']
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

    def getParents(self):
        if self.ascendants[0] == None or self.ascendants[1] == None:
            return None
        return (self.ascendants[0], self.ascendants[1])

    def mergeDwellers(self, dwellers):
        for i in range(6):
            self.ascendants[i] = dwellers.findDwellerFromId(self.ascendants[i])
        self.lastPartner = dwellers.findDwellerFromId(self.lastPartner)
        self.partner = dwellers.findDwellerFromId(self.partner)

class Stat(VaultObject):
    AUTOPROPS = ['exp', 'mod', 'value']
    def __str__(self):
        if self.mod:
            return str(self.value) + '+' + str(self.mod) + '(' + str(self.value + self.mod) + ')'
        else:
            return str(self.value)

    def getFullValue(self):
        return self.value + self.mod

class Stats(VaultObject):
    AUTOPROPS = ['_stats(Stat)']
    def __str__(self):
        return 'S=%s,P=%s,E=%s,C=%s,I=%s,A=%s,L=%s' % (str(self.stats[1]), str(self.stats[2]), str(self.stats[3]), str(self.stats[4]), str(self.stats[5]), str(self.stats[6]), str(self.stats[7]))

    def get(self, statName):
        statLetter = statName[0].upper()
        if statLetter == 'S':
            return self.stats[1]
        elif statLetter == 'P':
            return self.stats[2]
        elif statLetter == 'E':
            return self.stats[3]
        elif statLetter == 'C':
            return self.stats[4]
        elif statLetter == 'I':
            return self.stats[5]
        elif statLetter == 'A':
            return self.stats[6]
        elif statLetter == 'L':
            return self.stats[7]
        else:
            return None

class Dweller(VaultObject):
    AUTOPROPS = ['WillGoToWasteland', 'assigned', 'babyReady', 'deathTime', 'gender', 'hair', 'hairColor', 'lastChildBorn', 'lastName', 'name', 'outfitColor', 'pendingExperienceReward', 'pregnant', 'rarity', 'savedRoom', 'sawIncident', 'serializeId', 'skinColor', 'equipedOutfit(EquipmentItem)', 'equipedWeapon(EquipmentItem)', 'equipment(Equipment)', 'experience(Experience)', 'happiness(Happiness)', 'health(Health)', 'relations(Relations)', 'stats(Stats)', 'faceMask', 'daysOnWasteland', 'hoursOnWasteland', 'uniqueData']

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

    def mergeRooms(self, vaultInfo):
        self.savedRoom = vaultInfo.findRoomFromId(self.savedRoom)

class Handy(VaultObject):
    def __init__(self, dico):
        raise Exception('I don\'t know anything about Mr. Handys... yet:%s' % dico)

class DwellersList(VaultObject):
    AUTOPROPS = ['_dwellers(Dweller)', 'id', 'min_happiness', '_mrHandys(Handy)', 'mrhId']
    def __str__(self):
        return ','.join([str(x) for x in self.dwellers])

    def findDwellerFromId(self, dwellerId):
        for dweller in self.dwellers:
            if dweller.serializeId == dwellerId:
                return dweller
        return None

class RoomHealth(VaultObject):
    AUTOPROPS = ['damageValue']
    def __str__(self):
        return str(self.damageValue)

class Room(VaultObject):
    AUTOPROPS = ['broken', 'class', 'col', 'currentState', 'currentStateName', '_deadDwellers', 'deserializeID', '_dwellers', 'emergencyDone', 'level', 'mergeLevel', '_mrHandyList', 'power', 'roomHealth(RoomHealth)', 'row', 'rushTask', 'storage(Storage)', 'type', 'ExperienceRewardIsDirty']
    def __str__(self):
        return '%s(Damage:%s,%s;%s/%s occupancy)' % (self.TYPE, str(self.roomHealth), self.currentStateName, self.getWorkersCount(), self.maxWorkers())

    def maxWorkers(self):
        if self.TYPE == 'Entrance':
            return 2
        elif self.className == 'Production' or self.className == 'Consumable':
            return self.mergeLevel * 2
        else:
            return 0

    def getWorkersCount(self):
        return len(self.dwellers) + len(self.deadDwellers)

    def getRoomWidth(self):
        if self.TYPE == 'Elevator':
            return 1
        else:
            return self.mergeLevel * 3

    def mergeDwellers(self, dwellers):
        for i in range(len(self.dwellers)):
            self.dwellers[i] = dwellers.findDwellerFromId(self.dwellers[i])
        for i in range(len(self.deadDwellers)):
            self.deadDwellers[i] = dwellers.findDwellerFromId(self.deadDwellers[i])

class Rock(VaultObject):
    AUTOPROPS = ['c', 'r']
    def __str__(self):
        return 'Rock(%s,%s)' % (self.c, self.r)

class VaultInfo(VaultObject):
    AUTOPROPS = ['Achievements', 'LunchBoxesByType', 'LunchBoxesCount', 'VaultName', 'dwellerFoodConsumption', 'dwellerWaterConsumption', 'emergencyData', 'inventory(Inventory)', '_rocks(Rock)', 'roomConsumption', '_rooms(Room)', 'storage(Storage)', 'wasteland']
    def __str__(self):
        rooms = ','.join([str(room) for room in self.rooms])
        return 'Vault %s[%s]' % (self.VaultName, rooms)
    
    def findRoomFromId(self, roomId):
        for room in self.rooms:
            if room.deserializeID == roomId:
                return room
        return None

    def mergeDwellers(self, dwellers):
        for room in self.rooms:
            room.mergeDwellers(dwellers)

class Vault(VaultObject):
    AUTOPROPS = ['DeathclawManager(DeathclawManager)', 'LunchBoxCollectWindow', 'PromoCodesWindow', 'constructMgr(ConstructManager)', 'deviceName', 'dwellerSpawner', 'dwellers(DwellersList)', 'happinessManager', 'localNotificationMgr', 'objectiveMgr', 'ratingMgr', 'refugeeSpawner', 'survivalW', 'swrveEventsManager', 'taskMgr', 'timeMgr', 'tutorialManager', 'unlockableMgr', 'vault(VaultInfo)']
    def __init__(self, srcFile):
        jsonStr = decrypt(srcFile)
        with open('debug.txt', 'w') as out:
            out.write(jsonStr)
        jsonObj = json.loads(jsonStr)
        super(Vault, self).__init__(jsonObj)
        self.mergeDwellers()
        self.mergeRooms()

    def mergeDwellers(self):
        """Replace dwellers integer references by actual object references"""
        for dweller in self.dwellers.dwellers:
            dweller.mergeDwellers(self.dwellers)
        self.vault.mergeDwellers(self.dwellers)

    def mergeRooms(self):
        """Replace rooms integer references by actual room references"""
        for dweller in self.dwellers.dwellers:
            dweller.mergeRooms(self.vault)

    def __str__(self):
        return str(self.vault) + ',dwellers=[' + str(self.dwellers) + ']'

if __name__ == '__main__':
    raise Exception('This program cannot run in DOS mode')

