// Find the module for the program itself, always at index 0:
const m = Process.enumerateModules()[0];

// Or load a module by name:
//const m = Module.load('win32u.dll');

// Print its properties:
const properties = JSON.stringify(m);
console.log(properties);

send({type:"properties", data:properties});

// Dump it from its base address:
const dump = hexdump(m.base);
console.log(dump);

send({type:"dump", data:dump});


// // The pattern that you are interested in:
// const pattern = '00 00 00 00 ?? 13 37 ?? 42';
//
// Memory.scan(m.base, m.size, pattern, {
//   onMatch(address, size) {
//     console.log('Memory.scan() found match at', address,
//         'with size', size);
//
//     // Optionally stop scanning early:
//     return 'stop';
//   },
//   onComplete() {
//     console.log('Memory.scan() complete');
//   }
// });
//
// const results = Memory.scanSync(m.base, m.size, pattern);
// console.log('Memory.scanSync() result:\n' +
//     JSON.stringify(results));