from gsheets import write


def read_log():
    file = open('temp/base.log', 'r')
    list_hw_models = []
    for line in file:
        line = line.split("|")
        # print(len(line))
        list_hw_models.append(line[:-1])
    write.hw_models(list_hw_models, 1)
