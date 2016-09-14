### WORK IN PROGRESS  

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
python client.pt

# Open file /tmp/test.har with http://www.softwareishard.com/har/viewer/
# Have fun
```