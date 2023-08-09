
# Instagram profile scraper with Selenium

## Strategy

1. Use keywords to search for profiles in instagram search
2. Search suggested accounts of profiles from keyword search
3. Get profile information


## Workflow

1. Create Working directory

   ```
   mkdir <directory name>
   ```

2. Inside the directory create a file named keywords.csv with the keywords in a new line
3. Keyword search

   ```
   python selenium_key_word_search.py <username> <password> <folder> <keyword file>
    
   ```

4. Search suggested accounts of profiles from keyword search

   ```
   python selenium_suggestions_fast.py <username> <password> <folder> <searched profiles file>
    
   ```

5. Get profile information

   ```
   python selenium_profile_info.py <username> <password> <folder> <searched profiles file>
    
   ```
