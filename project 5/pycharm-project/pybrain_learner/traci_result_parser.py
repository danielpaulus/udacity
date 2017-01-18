
"""
Sadly, traci has no method to gather aggregated simulation statistics
That's why I wrote this simple parser.

"""
import pandas as pd
file = open('../../simulation-runs-lust', 'r')

content= file.read()
entries= content.split("-->")

columns=None
rows=[]

def to_float(n):
    if not n.strip():
        return 0
    try:
        return  float(n)
    except:
        raise

for entry in entries:
    lines= entry.split("\n")
    lines= filter(lambda x: x != '', lines)
    splitted= map(lambda x: [x.split(":")[0].strip(), x.split(":")[1].strip()], lines)
    splitted[6][1]= splitted[6][1].replace("ms","")
    splitted[6][0]+=" ms"
    splitted[10][1]=splitted[10][1].split("(")[0]

    if columns is None:
        columns= map(lambda x:x[0], splitted)
    row=[]
    values = map(lambda x: x[1],splitted[0:6])
    row.extend(values)
    values= splitted[6:20]
    values = map(lambda x: to_float(x[1]), values)
    row.extend(values)
    simulation_total_steps= row[3].split("~")[0]
    row.append(float(simulation_total_steps))
    rows.append(row)

columns.append("simulation_total_steps")
df= pd.DataFrame(rows, columns=columns)
print df