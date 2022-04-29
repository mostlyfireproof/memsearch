// Find the module for the program itself, always at index 0:
const m = Process.enumerateModules()[0];

// console.log("--------------------------------")
// console.log("Script running!")
// console.log("--------------------------------")

// Print its properties:
const properties = JSON.stringify(m);
send({type:"properties", data:properties});

// Dump it from its base address:
const dump = hexdump(m.base);
send({type:"dump", data:dump});
