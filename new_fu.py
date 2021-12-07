from gsheets import read, write

def read_log():
    file = open('temp/base.log', 'r')
    list_hw_models=[]
    for line in file:
        line = line.split("|")
        # print(len(line))
        list_hw_models.append(line[:-1])
    write.hw_models(list_hw_models,1)

# def compare():
    # litte_list = []read.smart('accounting','Items!E1:E')
    # big_list   = []read.smart('servers','servers!E2:E')
    # for each in big_list:
    # '' if each in litte_list else print(each)