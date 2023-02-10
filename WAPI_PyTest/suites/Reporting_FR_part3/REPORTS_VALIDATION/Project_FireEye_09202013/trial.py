import os

#def get_fireeye_hit():
#        cmd = "./run_alert_tests.sh "
#        returned_value = commands.getoutput(cmd)  # returns the exit code in unix
#        print('returned value:', returned_value)
#
#
#
#load=get_fireeye_hit()


output=os.system("./run_alert_tests.sh")
print(output)
