import re
phoneNumberPattern = re.compile('(\(?\d{3}\)?[- ]?\d{3}-\d{4})')

def getFax(lines):
  if isinstance(lines, str):
    lines = lines.split('\n')
  phoneLine = [l for l in lines if 'fax' in l or 'Fax' in l and phoneNumberPattern.search(l)]
  phoneNumber = None
  if phoneLine:
      matches = phoneNumberPattern.findall(phoneLine[0] or '')
      if not matches:
        return None
      return matches

def getPhone(lines):
  if isinstance(lines, str):
    lines = lines.split('\n')
  phoneLine = [l for l in lines if 'fax' not in l and 'Fax' not in l and phoneNumberPattern.search(l)]
  phoneNumber = None
  if phoneLine:
      matches = phoneNumberPattern.findall(phoneLine[0] or '')
      if not matches:
        return None
      return matches

def getLinesUntilPhone(lines):
  if isinstance(lines, str):
    lines = lines.split('\n')

  addressLines = []
  for l in lines:
    if phoneNumberPattern.search(l):
      break
    addressLines.append(l.strip())

  return addressLines

def getAddress(addressLines):
  print(addressLines)
  addressLine1 = addressLines[0]
  addressLine2 = None
  addressLine3 = None

  if len(addressLines) > 2:
      addressLine2 = addressLines[1]
  if len(addressLines) > 3:
      addressLine3 = addressLines[2]

  # New York, NY 10027

  stateAndZipPattern = re.compile('(.*) (\d{5}-?\d{0,4})')
  city = None
  state = None
  zipCode = None
  if ',' in addressLines[-1]:
      city = addressLines[-1].split(',')[0]
      otherPart = addressLines[-1].split(',')[1]
      match = stateAndZipPattern.search(otherPart)
      state = match.groups()[0].strip().upper()
      zipCode = match.groups()[1]
  
  return {
    'line1': addressLine1,
    'line2': addressLine2,
    'line3': addressLine3,
    'city': city,
    'state': state,
    'zip': zipCode
  }

from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()