### POC - Use as reference

### Extract HAR files using Chrome  

```bash
cd python-chrome-har/

# Create virtual environment and install deps
virtualenv env
source env/bin/activate
pip install -r requirements.txt

# Run Chrome or Chromium or Headless shell
/Applications/Chromium.app/Contents/MacOS/Chromium --remote-debugging-port=9222  --enable-benchmarking --enable-net-benchmarking

# Run HAR collector
python client.py

# Open file /tmp/test.har with http://www.softwareishard.com/har/viewer/
# Have fun
```

### Reference Links
#### Headless Chromium
https://chromium.googlesource.com/chromium/src/+/master/headless/README.md  
https://docs.google.com/document/d/11zIkKkLBocofGgoTeeyibB2TZ_k7nR78v7kNelCatUE/edit#  
https://chromium.googlesource.com/chromium/src/+/master/third_party/WebKit/Source/core/inspector/browser_protocol.json  
https://github.com/cyrus-and/chrome-har-capturer  



