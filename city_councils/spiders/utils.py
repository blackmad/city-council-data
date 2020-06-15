import re
phoneNumberPattern = re.compile('(\(?\d{3}\)?[- ]?\d{3}-\d{4})')

def getFax(lines):
  faxLine = [l for l in lines if 'fax' in l or 'Fax' in l]
  faxNumber = None
  if faxLine:
      faxMatch = phoneNumberPattern.search(faxLine[0] or '')
      if faxMatch:
          faxNumber = faxMatch.groups()[0]

def getFax(lines):
  phoneLine = [l for l in lines if 'fax' in l or 'Fax' in l and phoneNumberPattern.search(l)]
  phoneNumber = None
  if phoneLine:
      phoneMatch = phoneNumberPattern.search(phoneLine[0] or '')
      if phoneMatch:
        return phoneMatch.groups()[0]

def getPhone(lines):
  phoneLine = [l for l in lines if 'fax' not in l and 'Fax' not in l and phoneNumberPattern.search(l)]
  phoneNumber = None
  if phoneLine:
      phoneMatch = phoneNumberPattern.search(phoneLine[0] or '')
      if phoneMatch:
        return phoneMatch.groups()[0]

def getAddress(addressLines):
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