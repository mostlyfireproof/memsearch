import json
import sys

import frida
import colorama as cr
# colorama init:
cr.init(autoreset=True)


class Address:
    """ Represents a memory address and its contents """
    def __init__(self, addr, value, note="", tag=0):
        self.addr = addr            # memory address
        self.init_value = value     # initial value
        self.prev_value = value     # previous value
        self.value = value          # cuurent value
        self.tag = tag              # tag for reasons
        self.note = note            # lets the user mark something about the address

    def update_val(self, new_value):
        self.prev_value = self.value
        self.value = new_value


def on_message(message, data):
    """ Receives a message from the script """
    # print("[on_message] message:", message, "data:", data)
    global temp_addresses, proc_info

    if not 'payload' in message:
        print(cr.Fore.RED + "Something went wrong!")

    elif 'type' in message['payload']:
        message_type = message['payload']['type']
        if message_type == "properties":
            # print("AAAAAAAAA")

            proc_info = message['payload']['data']
            # print("pi", proc_info)

        elif message_type == "dump":
            # print("dump")
            # print(message['payload']['data'])
            temp_addresses = scan_mem_old(message['payload']['data'])


def scan_mem() -> dict:
    """ Calls on Frida to scan the memory of a program """
    print(cr.Fore.MAGENTA + "SCANNING")

    addresses = {}

    from_frida = script.exports.add(1, 2)
    print(cr.Fore.RED + str(type(from_frida)))
    # from_frida = str(from_frida)
    # print(from_frida)

    for content in from_frida:

        lines = content.split("\n")

        for i in range(1, len(lines)):
            data = lines[i].split()
            location = data[0]

            # print("line", i, "has", data)

            value = ""
            for j in range(1, 17):
                value += data[j]

            addr = Address(location, value)
            # print(i, "has", location, "with", addr)
            addresses[location] = addr

    # print(addresses)
    return addresses


def scan_mem_old(dump) -> dict:
    """ Processes memory dumps """
    addresses = {}

    from_frida = str(dump)
    # print(from_frida)

    lines = from_frida.split("\n")

    for i in range(1, len(lines)):
        data = lines[i].split()
        location = data[0]

        # print("line", i, "has", data)

        value = ""
        for j in range(1, 17):
            value += data[j]

        addr = Address(location, value)
        # print(i, "has", location, "with", addr)
        addresses[location] = addr

    # print(addresses)
    return addresses


def update_mem(addrs1: dict, addrs2: dict) -> dict:
    """ Takes in 2 dictionaries of addresses and returns the first one with new values from the second """
    updated = filtered_addresses
    # for i in addrs1.keys():
    #     updated.update(i, addrs1[i])

    # print("updated1:", updated)
    for addr in addrs2.keys():
        if addr in addrs1.keys():
            updated[addr] = addrs2[addr]
    # print("updated:", updated)
    return updated


def find_val(addrs: dict, value: str) -> dict:
    """Searches memory to find an exact value, and returns any addresses that hold it"""
    # TODO: use rpc search(pattern)
    validated = {}
    for addr in addrs.keys():
        if value in addrs[addr].value:
            validated.update({addr, addrs[addr]})
    return validated


def values_same(addrs: dict) -> dict:
    """ Returns any values that stayed the same between scans """
    validated = {}
    for addr in addrs.keys():
        if addrs[addr].value == addrs[addr].prev_value:
            validated[addr] = addrs[addr]

    return validated


def values_greater(addrs: dict) -> dict:
    """ Returns any values that increased between scans """
    validated = {}
    for addr in addrs.keys():
        if addrs[addr].value > addrs[addr].prev_value:
            validated[addr] = addrs[addr]
    return validated


def values_less(addrs: dict) -> dict:
    """ Returns any values that decreased between scans """
    validated = {}
    for addr in addrs.keys():
        if addrs[addr].value < addrs[addr].prev_value:
            validated[addr] = addrs[addr]
    return validated


def gren(word: str) -> str:
    """ Makes a word green """
    return cr.Fore.GREEN + word + cr.Fore.RESET


def addrs_to_str(addrs: list):
    """convers a given list of addresses to a string to be printed"""
    output = ""
    for addr in addrs:
        line = cr.Fore.BLUE + addr.addr + "\t"
        line += cr.Fore.CYAN + addr.value + "\t"
        line += cr.Fore.MAGENTA + addr.note
        line += "\n"

        output += line

    return output


#############################
#   initialization code     #
#############################
if len(sys.argv) < 2:
    raise ValueError(f"USAGE {sys.argv[0]} [program_to_search: e.g., /bin/ls or ./a.out]")

# attach to program up here
inject_script = 'memsearch.js'
with open(inject_script, 'r') as f:
    js = f.read()

proc = sys.argv[1]
device = frida.get_device('local')
pid = device.spawn(proc)
session = device.attach(pid)

# print(pid)
# print(session)

# print("Process started, injecting", inject_script)
script = session.create_script(js)

# Set up variables and data for my analyzer
to_exit = False

saved_addresses: dict = {}      # saved addresses
filtered_addresses: dict = {}   # addresses on display on the screen
temp_addresses: dict = {}       # on_message puts things here, deal with them after scanning

data_format = "hex"         # one of hex, dec, UTF-8 str, UTF-16 str, or bin

proc_info = {}

# Get properties
script.on("message", on_message)
script.load()
# script.eternalize()

# I HAVE NO IDEA WHY RPCDUMP DOESN'T WORK, BUT ADD DOES
# print(script.exports.add(1, 2))
# print(script.exports.add(3, 7))
# print(script.exports.rpcDump("hi"))

proc_info = json.loads(proc_info)

proc_name = proc_info["name"]
proc_base = proc_info["base"]
proc_size = proc_info["size"]

device.resume(pid)

#############################
#   run the project here    #
#############################

print(cr.Fore.BLACK + cr.Back.WHITE + "Welcome to memsearch!")
print("Analyzing", proc_name, "starting from", proc_base, "with PID", pid)
while not to_exit:
    # print(filtered_addresses)
    print("Choose an option: "
          "\n* "+gren("[i]")+"nitial scan"
          "\n* "+gren("[p]")+"rint SAVED addresses"
          "\n* print FILTERED "+gren("[a]")+"ddresses"
          "\n* "+gren("[s]")+"ave selected filtered address"                                  
          "\n* "+gren("[S]")+"ave current filtered addresses"
          
          "\n* "+gren("[>]")+" greater than previous scan, "
          + gren("[<]")+" less than previous scan, "+gren("[=]")+" same as previous scan"
          "\n* "+gren("[e]")+"xact value"
                              
          "\n* choose "+gren("[f]")+"ormat"
                                    
          "\n* "+gren("[w]")+"rite to an address"      
                             
          # "\n* "+gren("[h]")+"elp"
          "\n* e"+gren("[x]")+"it")

    choice = input("> ")    #.lower()

    print("\n")

    if choice == "i":
        print(cr.Fore.MAGENTA + "Calling Frida to dump the memory with hexdump")
        # filtered_addresses = scan_mem_old()
        # script.on("message", on_message)
        # script.load()
        # temp_addresses = scan_mem_old(script.exports.add(1, 2))
        temp_addresses = scan_mem()
        filtered_addresses = temp_addresses.copy()
        print(cr.Fore.MAGENTA + "Found " + str(len(filtered_addresses)) + " addresses")

    elif choice == "s":
        print("Which address would you like to save?")
        addr = input("> ")
        print("Saving", filtered_addresses[addr])
        saved_addresses.update(filtered_addresses[addr])

    elif choice == "S":
        print("Saving", len(filtered_addresses), "addresses")
        saved_addresses.update(filtered_addresses)

    elif choice == "a":     # print filtered addresses
        print(addrs_to_str(filtered_addresses.values()))
    elif choice == "p":     # print saved addresses
        print(addrs_to_str(saved_addresses.values()))

    elif choice == "e":
        val = input("Enter a value: ")
        # script.on("message", on_message)
        # TODO: convert val to hex based on data_format
        # filtered_addresses = find_val(update_mem(saved_addresses, temp_addresses), val)
        # pattern = ord(val)
        results = script.exports.search(val)
        print(results)


    elif choice == "=":
        # script.on("message", on_message)
        # script.load()
        temp_addresses = scan_mem()
        prev_size = len(filtered_addresses)
        filtered_addresses = values_same(update_mem(filtered_addresses, temp_addresses))
        print(cr.Fore.MAGENTA + str(len(filtered_addresses)) + " out of " + str(prev_size) + " remain")
    elif choice == ">":
        # script.on("message", on_message)
        # script.load()
        temp_addresses = scan_mem()
        prev_size = len(filtered_addresses)
        filtered_addresses = values_greater(update_mem(filtered_addresses, temp_addresses))
        print(cr.Fore.MAGENTA + str(len(filtered_addresses)) + " out of " + str(prev_size) + " remain")
    elif choice == "<":
        # script.on("message", on_message)
        # script.load()
        temp_addresses = scan_mem()
        prev_size = len(filtered_addresses)
        filtered_addresses = values_less(update_mem(filtered_addresses, temp_addresses))
        print(cr.Fore.MAGENTA + str(len(filtered_addresses)) + " out of " + str(prev_size) + " remain")

    elif choice == "f":
        print("Choose one of "+gren("[h]")+"ex, "+gren("[d]")+"ec, "+gren("[b]")+"inary, "
              "UTF-"+gren("[8]")+" string, or UTF-1"+gren("[6]")+" string")
        print("(Currently" + data_format + ")")
        selection = input("> ").lower()

        if selection == "h":
            data_format = "hex"
        elif selection == "d":
            data_format = "dec"
        elif selection == "b":
            data_format = "bin"
        elif selection == "8":
            data_format = "utf8"
        elif selection == "6":
            data_format = "utf16"
            # will need to do things like hex(ord( ))
        else:
            print(cr.Fore.YELLOW + "Invalid input!")

    elif choice == "w":
        print("Choose an address:")
        location = input("> ")
        # if the location is actually in the program range [proc_base, proc_base + proc_size]
        # TODO: all memory if they look somewhere that's not in the filtered list
        print("The current value at " + cr.Fore.BLUE + location + " is " + cr.Fore.CYAN + filtered_addresses[location])
        print("Choose a new value")
        value = input("> ")
        # TODO: finish implementing this

    elif choice == "x":
        to_exit = True
    else:
        print(cr.Fore.YELLOW + "Invalid input!")

    print("\n--------------------------------\n")


print("")

