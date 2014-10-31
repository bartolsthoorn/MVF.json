import json
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup

shimanouchi_vol_1 = 'http://webbook.nist.gov/cgi/cbook.cgi?Source=1972SHI1-160B&Mask=800'

with urlopen(shimanouchi_vol_1) as f:
    html = f.read()
    soup = BeautifulSoup(html)
    data = []

    for item in soup.ol.find_all('li'):
        compound = {}
        compound['name'] = item.a.encode_contents().decode('utf-8').strip()

        relative_url = item.a['href']
        print('+ Downloading', compound['name'], relative_url)

        netloc = urlparse(shimanouchi_vol_1).netloc
        absolute_url = 'http://' + netloc + relative_url

        with urlopen(absolute_url) as f_compound:
            compound_html = f_compound.read()
            compound_soup = BeautifulSoup(compound_html)

            tt = compound_soup.tt
            if tt:
                compound['InChI'] = tt.string.replace('InChI=', '')
            else:
                compound['InChI'] = ''

            matches = compound_soup.find_all('a', href=True, text='Permanent link')
            if matches:
                permanent_url = matches[0]['href']
            else:
                if len(compound['InChI']) > 0:
                    permanent_url = 'http://' + netloc + '/inchi/' + compound['InChI']

            compound['url'] = 'http://' + netloc + permanent_url

            vibrational_table = compound_soup.find_all('table', {'summary': 'Vibrational data'})[0]
            vibrations = vibrational_table.find_all('tr', {'valign': 'top'})

            compound['vibrations'] = []
            for vibration in vibrations:
                columns = vibration.find_all('td')
                vibration = {}
                vibration['sym_species'] =          columns[0].get_text()
                vibration['no'] =                   columns[1].get_text()
                vibration['mode'] =                 columns[2].get_text()
                vibration['selected_value'] =       columns[3].get_text()
                vibration['uncertainty'] =          columns[4].get_text().strip()
                #vibration['infrared_value'] =       columns[5].get_text()
                #vibration['infrared_phase'] =       columns[6].get_text()

                compound['vibrations'].append(vibration)

        data.append(compound)

    with open('shimanouchi.vol1.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=2, separators=(',', ': '))
