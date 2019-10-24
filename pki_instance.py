import ds_instance
import re
import subprocess

cmd_list=['pkispawn -v -f ca.cfg -s CA','sed -n "/^internal=/ s/^[^=]*=// p" < /etc/pki/pki-tomcat/password.conf > password.txt','certutil -L -d /etc/pki/pki-tomcat/alias','certutil -K -d /etc/pki/pki-tomcat/alias -f password.txt']

def check_pki():
    cmd="pki-server instance-find"
    out,ret_code = ds_instance.run_locally(cmd)
    iter_out = out.split("\n")
    #print(iter_out)
    for ele in iter_out:
        if re.match("^[1-9]+",ele):
            return True    
    return False

def pki_spawn():
    for cmd in cmd_list:
        print(cmd)
        out,ret = ds_instance.run_locally(cmd)


def main():
#    print(check_pki())
    if check_pki():
        print("pki instance exists. Please Check using command 'pki-server instance-find'")
    else:pki_spawn()

if __name__=="__main__":
    main()
