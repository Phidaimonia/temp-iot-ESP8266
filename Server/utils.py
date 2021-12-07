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



def fix_isoformat(weakISO, localize=False):                                    # "13:5:9"  ->  "13:05:09"
    return fuzzy_ISO_to_datetime(weakISO, localize).isoformat()



def aimtec_isoformat(tm):                                
    return fuzzy_ISO_to_datetime(tm, localize=True).isoformat(timespec='milliseconds')
            
            
            
            

if __name__ == '__main__':

    t = "2021-12-2T23:7:3.397000"
    print(t)

    print(aimtec_isoformat(t))