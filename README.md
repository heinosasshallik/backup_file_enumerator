# backup_file_enumerator
  
Enumerates web files to see if any backup versions of them have been left behind.  
  
  -h, --help  show this help message and exit  
  -f          Name of the file which contains a list of valid web pages,
              separated by newlines.  
  -c          Optional cookie value. Not tested.  
  
Example:  
python bkup_file_enumeration.py -f <name_of_file> -c <optional cookie parameter>  
