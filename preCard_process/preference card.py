import xlrd
import xlwt
import os
import re

#this file use for extracting unstructed preference card into a structed data

path=os.getcwd()+'../preference card/'
#preference_card
def precedure_surgeon():
    sur=''
    procedure=''
    xlsfile=path+"Final-merged preference card.xlsx"
    book=xlrd.open_workbook(xlsfile)
    sheet=[]
    for i in book.sheets():
        sheet.append(i.name)

    output=xlwt.Workbook(encoding='ascii')
    worksheet1=output.add_sheet('Sheet1')

    for index,sheet_item in enumerate(sheet):
        surgeon_set=list()
        procedure_set=list()
        table=book.sheet_by_name(sheet_item)
        print(sheet_item)
        if(len(table.row_values(0)[0])!=0):
            if(table.row_values(0)[0]!='Preference Card: Surgeon Mr A'):
                temp=''
                if(table.row_values(0)[0][:25]=="Preference Card: Surgeon "):
                    temp=table.row_values(0)[0].split("Surgeon ")[1]
                else:
                    temp=table.row_values(0)[0][17:]
                surgeon_set.append(temp)
                temp7=table.row_values(4)
                procedure3 = ''
                for iiiiiii in range(8):
                    if (len(temp7[iiiiiii]) != 0):
                        procedure3 = procedure3 +" "+ str(temp7[iiiiiii])
                procedure_set.append(procedure3)
            elif(table.row_values(0)[0]=='Preference Card: Surgeon Mr A'):
                temp1=table.row_values(2)
                #print(temp1)
                for ii in range(len(temp1)):
                    if(len(temp1[ii])!=0):
                        if(temp1[ii]=='SPR'):
                            continue
                        #print(temp1[ii])
                        surgeon_set.append(temp1[ii])
                if(table.row_values(3)[0]!='Procedures'):
                    temp2 = table.row_values(3)
                    #print(temp2)
                    for iii in range(len(temp2)):
                        if (len(temp2[iii]) != 0):
                            if (temp2[iii] == 'SPR'):
                                continue
                            #print(temp2[iii])
                            surgeon_set.append(temp2[iii])
                    if(table.row_values(4)[0]=='Procedures'):
                        temp5=table.row_values(5)
                        procedure1 = ''
                        for iiiii in range(8):
                            if (len(temp5[iiiii]) != 0):
                                procedure1 = procedure1 + " "+str(temp5[iiiii])
                        procedure_set.append(procedure1)
                    else:
                        print("Error 1")
                elif(table.row_values(3)[0]=='Procedures'):
                    temp6 = table.row_values(4)
                    procedure2 = ''
                    for iiiiii in range(8):
                        if (len(temp6[iiiiii]) != 0):
                            procedure2 = procedure2 + " "+str(temp6[iiiiii])
                    procedure_set.append(procedure2)

        else:
            temp3=table.row_values(2)
            for iii in range(len(temp3)):
                if(len(temp3[iii])!=0):
                    if (temp3[iii] == 'SPR'):
                        continue
                    #print(temp3[iii])
                    surgeon_set.append(temp3[iii])
            temp4=table.row_values(4)
            #print(temp4)
            procedure=''
            for iiii in range(8):
                if(len(temp4[iiii])!=0):
                    procedure=procedure+" "+str(temp4[iiii])
            procedure_set.append(procedure)

        for i1 in range(len(surgeon_set)):
            sur+=surgeon_set[i1]+"$"

        for i2 in range(len(procedure_set)):
            procedure=procedure_set[i2]

        #worksheet1.write(index,0,label=sur)
        #worksheet1.write(index,1,label=procedure)

    #output.save("preference card.xls")

def supplies():
    xlsfile="../preference card/Final-merged preference card.xlsx"
    book=xlrd.open_workbook(xlsfile)
    sheet=[]
    for i in book.sheets():
        sheet.append(i.name)

    output_file=xlwt.Workbook(encoding='ascii')
    worksheet1=output_file.add_sheet('Sheet1')

    for index,sheet_item in enumerate(sheet):
        table = book.sheet_by_name(sheet_item)
        print(sheet_item)
        rows=table.nrows
        supplies=list()
        temp1=table.row_values(7)[0] #supplies  #regularly supplier row in 7
        #but sometimes in 6 row or 8 row
        flag=7
        if(temp1!='Supplies'):    # Shai JJ-Grommets    Khai-Grommets  Han JJ-Grommets  And-Grommets
            #print(sheet_item)
            temp1=table.row_values(8)[0]
            flag=8
            if temp1!='Supplies':      #McD-OPEN MYOMECTOMY
                #print("6"+sheet_item)
                temp1=table.row_values(6)[0]
                flag=6

        flag=flag+3  #skip open&avaliable row and code&amount&item&alias
        #extract all supplies by iteration
        #print("flag:"+str(flag))
        standby_output=[]
        output=[]
        while(flag<rows):
            if(table.row_values(flag)[0]=='Drugs'):
                break
            else:
                first_row=table.row_values(flag)[:3]
                second_row=table.row_values(flag)[4:7]

                #判断是否为空
                if(check_empty(first_row)!=True):
                    output.append(first_row)
                    #print()
                #    print(first_row)
                if(check_empty(second_row)!=True):
                    #print()
                    #判断standby的情况
                    if(table.row_values(flag)[4]=='Have Standby'):
                        flag_standby=flag+2
                        while(flag_standby<rows):
                            if (table.row_values(flag_standby)[0] == 'Drugs'):
                                break
                            else:
                                standby_row = table.row_values(flag_standby)[4:7]
                                if(check_empty(standby_row)!=True):
                                    standby_output.append(standby_row)
                                flag_standby+=1
                    else:
                        output.append(second_row)
                flag+=1

        print("sheet item " + sheet_item)
        print("Open")

        ress=list()
        open_new=delete_standby_in_open(output,standby_output)
        print(open_new)
        for ii in open_new:
            res=''
            for iii in ii:
                res+=str(iii)+"|"
            res=res+'1'
            ress.append(res)

        #print(open_new)
        print("Standby")
        print(standby_output)
        for iiii in standby_output:
            res2=''
            for iiiii in iiii:
                res2+=str(iiiii)+"|"
            res2=res2+'0'
            ress.append(res2)
        print(ress)

        result=''
        for i2 in ress:
            result+=i2+'\n'
        print(result)

        worksheet1.write(index,0,result)
    output_file.save("Supplies.xls")

        #print(len(standby_output))


#在open里 去除standby
def delete_standby_in_open(open,standby):
    open_new=[]
    i=0
    while(i<len(open)):
        if(open[i][0]!='Code' and open[i] not in standby):
            open_new.append(open[i])
            i=i+1
        else:
            i=i+1
    return open_new

def check_empty(test):      #check a list empty or not
                            # empty return True
                            # otherwise return False
    length=len(test)
    for i in range(length):
        if(test[i]!=''):
            return False
    return True

def drugs():
    maybe_error_list=[]
    xlsfile="../preference card/Final-merged preference card.xlsx"
    book=xlrd.open_workbook(xlsfile)
    sheet=[]
    for i in book.sheets():
        sheet.append(i.name)

    output_file=xlwt.Workbook(encoding='ascii')
    worksheet1=output_file.add_sheet('Sheet1')

    for index,sheet_item in enumerate(sheet):
        table = book.sheet_by_name(sheet_item)
        #print(sheet_item)
        rows=table.nrows
        open=[]
        avaiable=[]
        flag_drug=0
        for i in range(rows):
            if(table.row_values(i)[0]=='Drugs'):
                flag_drug=i

        flag_drug_end=0
        for i1 in range(flag_drug,rows):
            if(table.row_values(i1)[0]=='Equipment' or table.row_values(i1)[0]=='EQUIPMENT' or table.row_values(i1)[0]=='Theatre Equipment'):
                flag_drug_end=i1

        while(flag_drug<flag_drug_end):
            if(table.row_values(flag_drug)[0]=='Drugs' and table.row_values(flag_drug+1)[0]=='Open'
                    and table.row_values(flag_drug+1)[5]=='Available'):
                flag_drug=flag_drug+2
                for i2 in range(flag_drug,flag_drug_end):
                    for open_temp1 in table.row_values(i2)[0:3]:
                        #print(open_temp1)
                        if(open_temp1):
                            open.append(open_temp1)
                    for avaiable_temp1 in table.row_values(i2)[4:7]:
                        if(avaiable_temp1):
                            avaiable.append(avaiable_temp1)
                flag_drug=flag_drug_end

            elif(table.row_values(flag_drug)[0]=='Drugs' and table.row_values(flag_drug)[5]=='Available'
                and table.row_values(flag_drug+1)[0]=='Open'):
                flag_drug=flag_drug+1
                for i3 in range(flag_drug,flag_drug_end):
                    for open_temp2 in table.row_values(i3)[0:3]:
                        if(open_temp2 and open_temp2!='Open'):
                            open.append(open_temp2)
                    for avaiable_temp2 in table.row_values(i3)[4:7]:
                        if(avaiable_temp2):
                            avaiable.append(avaiable_temp2)

                flag_drug=flag_drug_end

            elif(table.row_values(flag_drug)[0]=='Drugs' and table.row_values(flag_drug+1)[0]=='Open'
                    and table.row_values(flag_drug+1)[4]=='Have Standby'):
                flag_drug=flag_drug+2
                for i4 in range(flag_drug,flag_drug_end):
                    for open_temp3 in table.row_values(i4)[0:3]:
                        #print(open_temp3)
                        if(open_temp3):
                            open.append(open_temp3)
                    for avaiable_temp3 in table.row_values(i4)[4:7]:
                        if(avaiable_temp3):
                            avaiable.append(avaiable_temp3)
                flag_drug=flag_drug_end
            else:
                print("Error happen in sheet:"+str(sheet_item))
                flag_drug=flag_drug_end

        print(sheet_item)
        open_new=[]
        for ii in open:
            if (re.match(r'-?([1-9]\d*\.\d*|0\.\d*[1-9]\d*|0?\.0+|0)$', str(ii)) == None):
                open_new.append(ii)

        available_new=[]
        for iii in avaiable:
            if (re.match(r'-?([1-9]\d*\.\d*|0\.\d*[1-9]\d*|0?\.0+|0)$', str(iii)) == None):
                available_new.append(iii)


        res=list()
        print("Open")
        print(open_new)
        for i1 in open_new:
             res.append(str(i1)+'|1')

        print("Available")
        print(available_new)
        for i2 in available_new:
             res.append(str(i2)+'|0')

        result=''
        for i3 in res:
             result+=i3+'\n'

        worksheet1.write(index,0,result)

        if(len(open_new)!=len(open) or len(available_new)!=len(avaiable)):
            maybe_error_list.append(sheet_item)

    output_file.save("Durgs.xls")
    print(maybe_error_list)


def equipment():
    maybe_error_list=[]
    xlsfile="../preference card/Final-merged preference card.xlsx"
    book=xlrd.open_workbook(xlsfile)
    sheet=[]

    output_file=xlwt.Workbook(encoding='ascii')
    worksheet1=output_file.add_sheet('Sheet1')

    for i in book.sheets():
        sheet.append(i.name)

    for index,sheet_item in enumerate(sheet):
        table = book.sheet_by_name(sheet_item)
        rows=table.nrows
        print("sheet_name:"+str(sheet_item))
        equipment=[]
        flag_equipment=0
        for i in range(rows):
            if(table.row_values(i)[0]=='Equipment' or table.row_values(i)[0]=='EQUIPMENT' or table.row_values(i)[0]=='Theatre Equipment'):
                flag_equipment=i

        flag_equipment_end=0
        for i1 in range(flag_equipment,rows):
            if(table.row_values(i1)[0]=='Instruments' or table.row_values(i1)[0]=='Surgical Instruments (NHNN) Open'):
                flag_equipment_end=i1

        for i2 in range(flag_equipment+1,flag_equipment_end):
            temp=table.row_values(i2)[0:8]
            for i3 in temp:
                if(i3):
                    if(";" in str(i3)):
                        temp3=i3.split(";")
                        for i5 in temp3:
                            if(i5):
                                equipment.append(i5)
                    else:
                        equipment.append(i3)

        result=''
        for ii in equipment:
            result+=str(ii)+'\n'
        worksheet1.write(index,0,result)
    output_file.save("Equipment.xls")


def staff():
    xlsfile="../preference card/Final-merged preference card.xlsx"
    book=xlrd.open_workbook(xlsfile)
    sheet=[]
    output_file=xlwt.Workbook(encoding='ascii')
    worksheet1=output_file.add_sheet('Sheet1')

    for i in book.sheets():
        sheet.append(i.name)

    for index,sheet_item in enumerate(sheet):
        table = book.sheet_by_name(sheet_item)
        rows=table.nrows
        print("sheet_name:"+str(sheet_item))
        i=rows-1
        flag_staff=0
        while(i>0):
            if(table.row_values(i)[0]=='Staff'):
                flag_staff=i
            i=i-1

        flag_1=0
        flag_2=0
        flag_3=0
        for ii in range(flag_staff+1,rows):
            if(table.row_values(ii)[0]=='Surgical Staff'):
                flag_1=ii
            elif(table.row_values(ii)[0]=='Anaesthetic Staff'):
                flag_2=ii
            elif(table.row_values(ii)[0]=='Other staff'):
                flag_3=ii

        res=list()
        print('Surgical Staff')
        Surgical_Staff=[]
        for i1 in range(flag_1+1,flag_2):
            Surgical_Staff_temp=[]
            for ii1 in table.row_values(i1)[0:8]:
                if(ii1):
                    Surgical_Staff_temp.append(ii1)
            if(Surgical_Staff_temp):
                Surgical_Staff.append(Surgical_Staff_temp)
        print(Surgical_Staff)
        res.append('Surgical Staff:')
        for m1 in Surgical_Staff:
            if(len(m1)==2 and m1!=[' ',' ']):
                res.append(str(m1[0])+'|'+str(m1[1]))
            elif(len(m1)==1 and m1!=[' ']):
                res.append(str(m1[0])+'|1')

        Anaesthetic_Staff=[]
        print('Anaesthetic Staff')
        for i2 in range(flag_2+1,flag_3):
            Anaesthetic_Staff_temp = []
            for ii2 in table.row_values(i2)[0:8]:
                if (ii2):
                    Anaesthetic_Staff_temp.append(ii2)
            if(Anaesthetic_Staff_temp):
                Anaesthetic_Staff.append(Anaesthetic_Staff_temp)
        print(Anaesthetic_Staff)

        res.append('Anaesthetic Staff:')
        for m2 in Anaesthetic_Staff:
            if(len(m2)==2 and m2!=[' ',' ']):
                res.append(str(m2[0])+'|'+str(m2[1]))
            elif(len(m2)==1 and m2!=[' ']):
                res.append(str(m2[0])+'|1')

        print('Other staff')
        Other_Staff=[]
        for i3 in range(flag_3+1,rows):
            Other_Staff_temp = []
            for ii3 in table.row_values(i3)[0:8]:
                if(ii3):
                    Other_Staff_temp.append(ii3)
            if(Other_Staff):
                Other_Staff.append(Other_Staff_temp)
        print(Other_Staff)

        res.append('Other Staff:')
        for m3 in Anaesthetic_Staff:
            if(len(m3)==2 and m3!=[' ',' ']):
                res.append(str(m3[0])+'|'+str(m3[1]))
            elif (len(m3) == 1 and m3 != [' ']):
                res.append(str(m3[0])+'|1')

        result=''
        for m4 in res:
            result+=m4+'\n'
        worksheet1.write(index,0,result)
    output_file.save("Staff.xls")
if __name__ == '__main__':
    staff()
