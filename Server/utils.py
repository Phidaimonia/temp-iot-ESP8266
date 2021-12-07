import datetime
import time
import pytz



def fuzzy_ISO_to_datetime(weakISO, localize=False):
    t = None
    try:
        t = datetime.datetime.fromisoformat(weakISO)            # try normal isoformat
    except Exception:
        pass

    if t is None:
        t = datetime.datetime.strptime(weakISO, "%Y-%m-%dT%H:%M:%S.%f")         # in case of bad isoformat

    if localize:
        t = pytz.utc.localize(t)            # add UTC timeozone info

    return t



def fix_isoformat(weakISO, localize=False):
    return fuzzy_ISO_to_datetime(weakISO, localize).isoformat()

            
            
            
            

if __name__ == '__main__':
    print("")
    #t = "2021-12-2T23:7:3.397000"
    #print(t)
    #print(aimtecTimeFormat(t))