import xlrd, xlwt
import re, pymysql
import sys

def saveResults(procedureIdListPure, willAddChildren):

    dict_ID_TERM = readORP()

    excel1 = xlrd.open_workbook('sources/pref-card-rpt-150719.xlsx')
    table1 = excel1.sheet_by_name(u'Preference Card')
    surgeonListEpic = table1.col_values(5)[5:]
    locationListEpic = table1.col_values(7)[5:]
    cardIdListEpic = table1.col_values(0)[5:]
    cardIdListEpic = [id.replace('M-','') for id in cardIdListEpic]


    if willAddChildren == True:
        rawData, rawData2 = connect_sql()
        global dict_SID_DID
        dict_SID_DID = get_dict_SID_DID(rawData)
        # dict_CID_PRE = get_dict_CID_PRE(rawData2) # don't need preferred name

        newProcIdsListWithChildren = []
        for i, idList in enumerate(procedureIdListPure):
            if idList != []:
                childernIdList = getAllChildrenFromIdList(idList)
                childernIdList = [id for id in childernIdList if id in dict_ID_TERM.keys()]
                idList = idList + childernIdList
            newProcIdsListWithChildren.append(idList)
            procedureIdListPure = newProcIdsListWithChildren


    dict_Triple_cardId = {}
    for surgeon, location, idList, cardId \
    in zip(surgeonListEpic, locationListEpic, procedureIdListPure, cardIdListEpic):
        for id in idList:
            thisKey = (surgeon, location, id)
            if dict_Triple_cardId.get(thisKey) == None:
                dict_Triple_cardId[thisKey] = cardId
            else:
                dict_Triple_cardId[thisKey] = 'dup'

    # dup_list = [k for k,v in dict_Triple_cardId.items() if v == 'dup']
    # print(dup_list)


    print('Saving results...')
    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet('output_file')
    thisRow = table1.row_values(4)
    for j in range(10):
        worksheet.write(0, j, thisRow[j])
    worksheet.write(0, 10, 'REVIEW ID')
    worksheet.write(0, 11, 'REVIEW TERM')

    worksheet2 = workbook.add_sheet('output_file2')
    worksheet2.write(0, 0, 'Procedure ID')
    worksheet2.write(0, 1, 'Procedure Name')
    worksheet2.write(0, 2, 'Any Not Shown?')
    worksheet2.write(0, 3, 'Any Duplication?')

    rowCount = 1
    for i, idList in enumerate(procedureIdListPure):
        if idList != []:

            dupIdList = []
            for id in idList:
                thisKey = (surgeonListEpic[i], locationListEpic[i], id)
                try:
                    if dict_Triple_cardId[thisKey] == 'dup':
                        dupIdList.append(id)
                except Exception as e:
                    sys.exit(e)

            dupNameList = [dict_ID_TERM.get(id,[''])[-1] for id in dupIdList]

            thisRow = table1.row_values(5+i)
            for dupId, dupName in zip(dupIdList, dupNameList):
                for j in range(10):
                    worksheet.write(rowCount, j, thisRow[j])
                worksheet.write(rowCount, 10, dupId)
                worksheet.write(rowCount, 11, dupName)
                rowCount += 1

            nameList = [dict_ID_TERM.get(id,[''])[-1] for id in idList]
            if len(idList) > 20:
                tempMsg = 'Only 20' + '/' + str(len(idList)) + ' shown due to space limit.'
                # idList = idList[:20]
                nameList = nameList[:20]
                worksheet2.write(i+1, 2, tempMsg)
            worksheet2.write(i+1, 0, '\n'.join(idList).strip())
            worksheet2.write(i+1, 1, '\n'.join(nameList).strip())

            if len(dupIdList) > 20:
                tempMsg = 'Only 20' + '/' + str(len(dupIdList)) + ' shown due to space limit.'
                # dupIdList = dupIdList[:20]
                # dupIdList.append(tempMsg)
            worksheet2.write(i+1, 3, '\n'.join(dupIdList).strip())


    workbook.save('results/Excel_test.xls')

    return None


def getAllChildrenFromIdList(idList):
    # print(idList)
    childernIdList = []
    toProcessIdList = idList.copy()
    while toProcessIdList != []:
        thisId = toProcessIdList.pop()
        if thisId not in idList:
            childernIdList.append(thisId)
        itsChildern = dict_SID_DID.get(thisId)
        if itsChildern != None:
            toProcessIdList.extend(itsChildern)
    # print(childernIdList)
    return list(set(childernIdList))


def connect_sql():
    print('Loading database...')
    try:
        conn=pymysql.connect(read_default_file="sources/my.cnf")

        cur=conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql="select id,effectiveTime,sourceId,destinationId,typeId from NHS_dbo.relationship_activelist \
        where typeId = '116680003'"
        cur.execute(sql)
        rawData = cur.fetchall()
        #rawData = cur.fetchmany(10)
        #print(rawData)
        cur.close()

        cur2=conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql2 = "Select effectiveTime,conceptId,term from NHS_dbo.merge_concept_description where typeId='900000000000013009' \
            and id in (SELECT referencedComponentId FROM NHS_dbo.refset_lan_gb_int_activelist \
			where acceptabilityId='900000000000548007')" # Preferred Name
        cur2.execute(sql2)
        rawData2 = cur2.fetchall()
        cur2.close()

        conn.close()

    except Exception as e:
        print("Fail:", e)

    return rawData, rawData2

def get_dict_SID_DID(rawData):
    dict_SID_DID = {}
    for item in rawData:
        varTerm = item['destinationId']
        getDID = dict_SID_DID.get(varTerm)
        if getDID == None:
            dict_SID_DID[varTerm] = []
        dict_SID_DID[varTerm].append(item['sourceId'])
    return dict_SID_DID

def get_dict_CID_PRE(rawData2):
    dict_CID_PRE = {}
    dict_PRE_ETIME = {}
    for item in rawData2:
        varTerm = item['conceptId']
        getPRE = dict_CID_PRE.get(varTerm)
        if getPRE == None:
            dict_CID_PRE[varTerm] = item['term']
            dict_PRE_ETIME[varTerm] = item['effectiveTime']
        else:
            if dict_PRE_ETIME[varTerm] < item['effectiveTime']:
                dict_CID_PRE[varTerm] = item['term']
                dict_PRE_ETIME[varTerm] = item['effectiveTime']
    return dict_CID_PRE

def readORP():

    excel2 = xlrd.open_workbook('sources/orp170619-NameLocations.xlsx')
    table2 = excel2.sheet_by_name(u'Sheet1')
    termList = table2.col_values(0)[1:]
    aliasList = table2.col_values(1)[1:]
    flagList = table2.col_values(2)[1:]
    idList = table2.col_values(3)[1:]
    locationList = table2.col_values(4)[1:]

    if len(termList) != len(idList) or len(termList) != len(locationList) \
    or len(termList) != len(aliasList) or len(termList) != len(flagList):
        print('# WARNING: LENGTH')

    dict_ID_TERM = {}
    dict_ID_TERM_conflict = {}
    # dict_ID_TERM_NHNN = {}
    # dict_ID_TERM_NHNNIMRI = {}
    for i in range(len(termList)):

        if flagList[i] == 'Yes':
            # print('# WARNING:', 'INACTIVE:', termList[i])
            continue

        thisId = ''
        if len(idList[i].split()) > 2:
            print('!# WARNING:', idList[i].split())
            exit()
        elif len(idList[i].split()) == 2:
            tempCount = 0
            for id in idList[i].split():
                id = id.strip()

                if re.search('\D',id) or len(id)<6 or len(id)>18:
                    pass
                elif id[:3] != '777':
                    thisId = id
                    tempCount += 1
            if tempCount > 1:
                print('!# WARNING:', idList[i].split())
                exit()
            if tempCount == 0:
                print('Skip:', idList[i].split())
                continue
        else:
            thisId = idList[i].strip()
            if thisId == '' or re.search('\D',thisId) or len(thisId)<6 or len(thisId)>18:
                if thisId != '':
                    print('Skip:', thisId)
                continue

        if thisId == '':
            print('!# WARNING:', 'HERE')
            exit()

        theseTerm = []
        for alias in aliasList[i].split('\n'):
            if alias.strip() != '':
                theseTerm.append(alias.strip())
        theseTerm.append(termList[i].strip())

        if dict_ID_TERM.get(thisId) == None:
            dict_ID_TERM[thisId] = theseTerm
        elif set(theseTerm).issubset(set(dict_ID_TERM[thisId])):
            pass
            # print('pass1')
        elif set(dict_ID_TERM[thisId]).issubset(set(theseTerm)):
            dict_ID_TERM[thisId] = theseTerm
            # print('pass2')
        else:
            if dict_ID_TERM_conflict.get(thisId) == None:
                dict_ID_TERM_conflict[thisId] = (dict_ID_TERM[thisId],theseTerm)
                del dict_ID_TERM[thisId]
            else:
                print('# WARNING: MORE CONFLICT')
                sys.exit(0)

    return dict_ID_TERM

if __name__ == '__main__':
    print('********** Scripts start. **********')
    main()
    print('********** Scripts end. **********')
