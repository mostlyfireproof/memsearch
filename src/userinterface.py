import json
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


def scan_mem() -> dict:
    """ Calls on Frida to scan the memory of a program """
    # TODO: use Frida
    # const p = Process.enumerateModules()[0]; console.log(hexdump(p.base));
    addresses = {}
    return addresses


def update_mem(addrs1: dict, addrs2: dict):
    """ Takes in 2 dictionaries of addresses and updates the first one with values from the second """
    for addr in addrs2.keys():
        if addr in addrs1.keys():
            addrs1[addr].update(addrs2[addr].value)


def find_val(addrs, value):
    """Searches memory to find an exact value, and returns any addresses that hold it"""
    validated = {}
    for addr in addrs.keys():
        if addrs[addr].value == value:
            validated.update({addr, addrs[addr]})
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

# attach to program up here?
# temp data:
proc_info = json.loads('{"name":"a.out","base":"0x55b29249d000","size":20480,"path":"/mnt/d/final/src/a.out"}')
# get these from const p = Process.enumerateModules()[0]; console.log(JSON.stringify(p))
proc_name = proc_info["name"]
proc_base = proc_info["base"]     # reformat?
proc_size = proc_info["size"]

# Set up variables and data for my analyzer
to_exit = False

saved_addresses: dict = {}        # saved addresses
filtered_addresses: dict = {}     # addresses on display on the screen

data_format = "hex"         # one of hex, dec, str, or bin

# samples to test things
zero = Address("0x0", hex(0))
data = Address("0x123", hex(123))

print("Welcome to memsearch!")
print("Analyzing", proc_name, "starting from", proc_base)
while not to_exit:
    print("Choose an option: "
          "\n* "+gren("[i]")+"nitial scan"
          "\n* "+gren("[p]")+"rint SAVED addresses"
          "\n* print FILTERED "+gren("[a]")+"ddresses"
          "\n* "+gren("[s]")+"ave current filtered addresses"
          
          "\n* "+gren("[>]")+" greater than previous scan, "
          + gren("[<]")+" less than previous scan, "+gren("[=]")+" same as previous scan"
          "\n* "+gren("[e]")+"xact value"
                             
          "\n* choose "+gren("[f]")+"ormat"
                                    
          # "\n* "+gren("[h]")+"elp"
          "\n* e"+gren("[x]")+"it")

    choice = input("> ").lower()

    print("\n")

    if choice == "i":
        print("this will call Frida to dump the memory with hexdump")
        filtered_addresses = scan_mem()
        filtered_addresses.update({zero.addr: zero})
        filtered_addresses.update({data.addr: data})
    elif choice == "s":
        print("Saving", len(filtered_addresses), "addresses")
        saved_addresses.update(filtered_addresses)
    elif choice == "a":     # print filtered addresses
        print(addrs_to_str(filtered_addresses.values()))
    elif choice == "p":     # print saved addresses
        print(addrs_to_str(saved_addresses.values()))

    elif choice == "e":
        val = input("Enter a value: ")
        scan = scan_mem()
        # TODO: combine scan and filtered
        # TODO: convert val to hex based on data_format
        filtered_addresses = find_val(filtered_addresses, val)
    elif choice == "=":
        pass
    elif choice == ">":
        pass
    elif choice == "<":
        pass

    elif choice == "f":
        print("Choose one of "+gren("[h]")+"ex, "+gren("[d]")+"ec, "+gren("[b]")+"inary, or "+gren("[s]")+"tring")
        print("(Currently" + data_format + ")")
        selection = input("> ").lower()

        if selection == "h":
            data_format = "hex"
        elif selection == "d":
            data_format = "dec"
        elif selection == "b":
            data_format = "bin"
        elif selection == "s":
            data_format = "str"
            # will need to do things like hex(ord( ))
        else:
            print(cr.Fore.YELLOW + "Invalid input!")

    elif choice == "x":
        to_exit = True
    else:
        print(cr.Fore.YELLOW + "Invalid input!")

    print("\n--------------------------------\n")


print("")

