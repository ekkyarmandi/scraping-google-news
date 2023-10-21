# Eastern World War Google News Related Topic

Google news data scraping project to scrape news related to Palistine and Israel War

### Setup

1. Environtment variables required

```.env
PROXIES="http://username:password@host:port"
TURNON_PROXIES=False
MIN_DATE="mm/dd/yyyy"
MAX_DATE="mm/dd/yyyy"
```

- `PROXIES` is the way you hide your computer IP. You can buy proxy service on ProxyScrape or IPRoyal.
- `TURNON_PROXIES` put True with capital T after equal to let the function read your Proxies. It will return an error if there's something wrong with your proxies or network connection.
- `MIN_DATE` and `MAX_DATE` is range of article you want to go.

2. Virtual Environtment  
   In Python you can create a Virtual Environtment where we isolate our project dependencies in the directory we use. This is a good practice to avoid error in the future when the dependencies got updated or if you want to use different version of the dependencies. You can skip it if you think you don't need it.

Here's how you can create and activate the virtual environtment on your local machine:

```bash
python -m venv [dir-name]

# on MaxOS/Linux
source [dir-name]/bin/activate

# on WindowOS
[dir-name]\Scripts\Activate
```

Use this command below if you want to `deactivate` the virtual environtment

```bash
deactivate
```

### How to run

1. Install the dependencies

```bash
pip install -r requirements.txt
```

2. List the keywords
   Go to main.py and look for `KEYWORDS`, you can define the you want to look there

```python
KEYWORDS = [
  ...
]
```

3. Run the main script
   By executing the command below on your terminal, it will read the `KEYWORDS` variable and iterate the keyword in it. You can add the keyword on `exclude` variable if you do not want the keyword being queried.

```bash
python3 main.py
```

4. Merge the result
   By executing the commmand below on your terminal, it will go through [data](./data/) directory and look for csv files then merge it.

```bash
python3 merge.py
```
