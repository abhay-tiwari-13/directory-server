import subprocess
import re
import argparse

def parse_cli():
    parser = argparse.ArgumentParser(description="Subscription Check")
    parser.add_argument('username', help="username for subscription")
    parser.add_argument('password', help="user's password for subscription")
    parser.add_argument('--server_type', default="ds", choices=["ds", "das", "as"], help="server types, chooes from choices: \n1)ds: A DS instance\n2)das(A DS instance with Admin Server \n3)as: Admin server on existing DS instance")
    args = parser.parse_args()
    user, passwd, server_type = args.username, args.password, args.server_type
    return user,passwd,server_type

def run_locally(cmd):
    """
    Run the cmd locally and return the output
    """
    pipe = subprocess.Popen( cmd.strip().split(), stdout=subprocess.PIPE)
    pipe.wait()
    out,err = pipe.communicate()
    return out.decode(), pipe.returncode

def check_subscription():
    cmd="subscription-manager status"
    out,ret_code = run_locally(cmd)
    iter_out = out.split("\n")
    for line in iter_out:
        if re.match("^Overall",line):
            if line.split()[2]=="Unknown":
                return False
            else: return True


def register_and_subscribe(user,passwd):
    cmd=f"subscription-manager register --auto-attach --username={user} --password={passwd}"
    proc, ret_code = run_locally(cmd)
    print(proc)
    return check_subscription()

def subscribe_DS():
    cmd1='subscription-manager list --available --all'
    cmd2='grep -20 Directory'
    out1 = subprocess.Popen(cmd1.strip().split(), stdout=subprocess.PIPE)
    out1.wait()
    out2 = subprocess.Popen(cmd2.strip().split(), stdin=out1.stdout, stdout=subprocess.PIPE)
    out2.wait()
    out2 = out2.communicate()[0].decode().split('\n')
    for ele in out2:
        print(ele)
        if ele.startswith("Pool"):
            pool_id=ele.split()[2]

    cmd3=f'subscription-manager attach --pool={pool_id}'
    print(cmd3)
    out, ret_code = run_locally(cmd3)
    cmd4 = "subscription-manager repos --enable='rhel-7-server-rhds-10-rpms'"
    out, ret_code = run_locally(cmd4)
    cmd5 = "yum install -y redhat-ds"
    out, ret_code = run_locally(cmd5)
    return out


def Setup_DS():
    hostname,ret_code = run_locally("hostname")
    with open("DS.inf", "r") as fd:
        conf_list=fd.readlines()

    conf_list[1] = f'FullMachineName={hostname} \n'

    with open("DS.inf", "w") as wfd:
        wfd.writelines(conf_list)

    out, ret_code = run_locally("setup-ds.pl -s -f DS.inf")
    print(out)


def main():
    #checking system settings and subscribing to redhat network if not
    user,passwd,server_type = parse_cli()
    if check_subscription():
        print("system subscribed")
    else:
        print("System not subscribed. Subscribing system with Red Hat")
        print(register_and_subscribe(user,passwd))
        subscribe_DS()
    #Silent installation starts from here
    Setup_DS()

if __name__ == "__main__":
    main()
