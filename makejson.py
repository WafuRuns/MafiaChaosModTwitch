import csv
import json

data = {}
with open('effects.csv', newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    data['effects'] = []
    for i in r:
        if i[3] == 'Instant':
            duration = 0
        else:
            duration = int(i[3])
        data['effects'].append({
            'id': int(i[0]),
            'name': i[1],
            'duration': duration
        })

with open('effects.json', 'w') as outfile:
    json.dump(data, outfile)
