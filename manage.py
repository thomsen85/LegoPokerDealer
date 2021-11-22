from app.content.window import main
#from app.bluetooth import bluetooth
#from app.manual_controller import controller
import sys
import os

def cases(arg):
    if arg == "start":
        main()
        
    elif arg == "help":
        print("Argument options:")
        print("\t- start")
        print("\t- help")

    elif arg=="test":
        os.system("pytest")

    else:
        print(str(arg) + " is an unvalid argument. See python manage.py help for options")



if __name__ == '__main__':
    if len(sys.argv) > 1:
        cases(sys.argv[1])
    else:
        print("Enter a valid argument. See python manage.py help for options")
