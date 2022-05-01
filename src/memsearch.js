console.log("--------------------------------")
console.log("Script running!")
console.log("--------------------------------")

// Find the module for the program itself, always at index 0:
let m = Process.enumerateModules()[0];

// Print its properties:
const properties = JSON.stringify(m);
send({type:"properties", data:properties});

// Dump it from its base address:
function sendDump() {
    const dump = hexdump(m.base, 8);
    send({type:"dump", data:dump});
    console.log("JS: Sent data");
}
sendDump();


// I HAVE NO IDEA WHY RPCDUMP DOESN'T WORK, BUT ADD DOES
rpc.exports = {
    rpcDump(arg) {
        // console.log("JS: Sent data");
        // return hexdump(m.base);
        return("AAAAAAAAAa")
    },
    // dumps the memory
    add(a, b) {
        var mems = new Array();
        const modules = Process.enumerateModules();
        for (let i = 0; i < modules.length; i++) {
            mems.push(hexdump(modules[i].base));
        }

        return mems
    },
    // Scans the memory for a given pattern
    search(pattern) {
        // var found = new Array();
        // const modules = Process.enumerateModules();
        // for (let x in modules) {
        //     Memory.scan(x.base, x.size, pattern, {
        //         found.push(address);
        //         console.log('Memory.scan() found match at', address,
        //                     'with size', size);
        //     });
        // }

        m = Process.enumerateModules()[0];
        var found = new Array()
        Memory.scan(m.base, m.size, pattern, {
            onMatch(address, size) {
                found.push(address)
                console.log('Found match of', pattern, 'at', address,
                            'with size', size);
            }
        });
        return found;

    }
};