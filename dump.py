import os
if __name__ == "__main__":
   try:
       os.system("git pull")
       import("dump").menu()
   except Exception as e:
       exit(str(e))
