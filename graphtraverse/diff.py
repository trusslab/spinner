from itertools import islice

#input1 = input('File name 1:')
#input2 = input('File name 2:')
input1 = 'file69'
input2 = 'file65'
file1 = open(input1, "r")

reports1_dict = {}
reports1 = set()
while True:
    report_type = 'context confusion'
    report= ''.join(list(islice(file1, 3)))
    #print(report)
    if not report:
        break
    if 'nested issue' in report:
        report_type = 'nested issue'

    split =report.split()
    real_report = split[1]+" "+report_type+" "+split[-2]+" "+split[-1]
    if real_report not in reports1_dict:
        reports1_dict[real_report]=[report]
    else:
        reports1_dict[real_report].append(report)
    reports1.add(real_report)
#print(len(reports1))
file1.close()

file2 = open(input2, "r")

reports2_dict = {}
reports2 = set()
while True:
    report_type = 'context confusion'
    report= ''.join(list(islice(file2, 3)))
    #print(report)
    if not report:
        break
    if 'nested issue' in report:
        report_type = 'nested issue'

    split =report.split()
    real_report = split[1]+" "+report_type+" "+split[-2]+" "+split[-1]
    reports2.add(real_report)
    if real_report not in reports2_dict:
        reports2_dict[real_report]=[report]
    else:
        reports2_dict[real_report].append(report)
#print(len(reports2))
file2.close()

print(len(reports1-reports2))
print(len(reports2-reports1))


diff1=open('diff1.txt', 'w')
for real_report in reports1-reports2:
    #diff1.writelines(real_report)
    diff1.writelines(reports1_dict[real_report])
diff1.close()

diff2= open('diff2.txt', 'w')
for real_report in reports2-reports1:
    #diff2.writelines(real_report)
    diff2.writelines(reports2_dict[real_report])
diff2.close()

