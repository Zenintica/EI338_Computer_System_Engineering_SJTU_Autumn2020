import os
import subprocess
import re


# delimiters = [" ", "<", ">"]


def parse_command(command: str):
    """
    Parse the command into a list consisting of command name and arguments (if any).
    Params:
        command: the command to be parsed.
    Return:
        command_list: the list consisting of command name and arguments (if any).
    """
    return command.split(" ")


def check_redirection(command: str):
    """
    Check if redirection occurs.
    Params:
        command: the command to be parsed.
    Return:
        command: the original command.
        fd_in: the name of input file (None if not exist).
        fd_out: the name of output file (None if not exist).
    """
    fd_in = fd_out = None
    if ">" in command:
        fd_in, command = command.split(">")[0].lstrip(" ").rstrip(" "), command.split(">")[1].lstrip(" ").rstrip(" ")
    if "<" in command:
        command, fd_out = command.split("<")[0].lstrip(" ").rstrip(" "), command.split("<")[1].lstrip(" ").rstrip(" ")
    return command, fd_in, fd_out


def check_pipe(command: str):
    """
    Check if pipe occurs.
    Params:
        command: the command to be parsed.
    Return:
        command_1: the former command as the input of the latter command; if no pipes are needed, it is identically the original command.
        command_2: the latter command (None if not exist).
        status: the boolean value, True indicates pipes exist, and vice versa.
    """
    command_1 = command
    command_2 = None
    status = False
    if "|" in command:
        command_1, command_2 = command.split("|")[0].lstrip(" ").rstrip(" "), command.split("|")[1].lstrip(" ").rstrip(" ")
        status = True
    return command_1, command_2, status


def main():
    should_run = True
    command_now = command_last = ""

    while should_run:
        print("osh>", end="")
        command_now = str(input())

        if command_now == "exit":
            print("Exiting.")
            should_run = False
            return

        elif command_now == "!!":
            if command_last == None:
                print("[ERROR] Command history not available yet.")
            else:
                command_now = command_last

        # store the command history
        command_last = command_now

        # TODO: 
        #   check ampersand
        # what have done:
        #   check pipes
        #   parse the command into a list
        #   check I/O redirection

        command_1, command_2, status = check_pipe(command_now)

        if not status:
            command_now = command_1
            command_now, fd_in, fd_out = check_redirection(command_now)
            command_list = parse_command(command_now)

            if command_list == ["help"]:
                print("[INFO] This is a simple linux shell simulator implemented by the subprocess module of python.\n \
                Functions achieved for now:\n \
                \tordinary executing commands;\n \
                \tchecking redirection;\n \
                \tcommunication via pipes.\n \
                Usages:\n \
                \thelp: \tprint this message;\n \
                \t!!: \texecute the last command given;\n \
                \texit: \texit the shell simulator.")

            else:
                try:
                    proc = subprocess.Popen(command_list, 
                                            stdin=subprocess.PIPE, 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE)

                    if fd_in is not None:
                        try:
                            with open(fd_in, 'rb') as f:
                                outs, errs = proc.communicate(input=f.read())
                        except FileNotFoundError:
                            print("[ERROR] stdin redirection error: input file not found.")
                    else:
                        outs, errs = proc.communicate()

                    if errs:
                        print("[ERROR] {}".format(errs.decode('UTF-8').rstrip("\n")))
                    else:
                        if fd_out is not None:
                            with open(fd_out, 'w') as f:
                                f.write(outs.decode("UTF-8").rstrip("\n"))
                        else:
                            print(outs.decode("UTF-8").rstrip("\n"))

                    print("[INFO] command executed with code {}".format(proc.poll()))

                except FileNotFoundError:
                    print("[ERROR] an error occurred when executing command. Please check the spelling of your command.\nYou can type \"help\" for showing usages.")
        else:
            command_1, fd_in_1, fd_out_1 = check_redirection(command_1)
            command_2, fd_in_2, fd_out_2 = check_redirection(command_2)
            command_list_1 = parse_command(command_1)
            command_list_2 = parse_command(command_2)

            # print(command_list_1, fd_in_1, fd_out_1)
            # print(command_list_2, fd_in_2, fd_out_2)

            try:
                proc_1 = subprocess.Popen(command_list_1,
                                            stdout=subprocess.PIPE)
                proc_2 = subprocess.Popen(command_list_2, 
                                            stdin=proc_1.stdout, 
                                            stdout=subprocess.PIPE)

                if fd_in_1 is not None:
                    with open(fd_in_1, 'rb') as f_1:
                        file_in = f_1.read()
                        proc_1 = subprocess.Popen(command_list_1,
                                                stdin=file_in,
                                                stdout=subprocess.PIPE)
                else:
                    proc_1 = subprocess.Popen(command_list_1,
                                            stdout=subprocess.PIPE)

                outs, errs = proc_2.communicate()

                if fd_out_2 is not None:
                    with open(fd_out_2, 'w') as f_2:
                        f_2.write(outs.decode("UTF-8").rstrip("\n"))
                else:
                    print(outs.decode("UTF-8").rstrip("\n"))

                if errs:
                    print("[ERROR] {}".format(errs.decode('UTF-8').rstrip("\n")))

                print("[INFO] command executed with code {}".format(proc_2.poll()))

            except FileNotFoundError:
                print("[ERROR] an error occurred when executing command. Please check the spelling of your command.\nYou can type \"help\" for showing usages.")
        
        


if __name__ == "__main__":
    main()