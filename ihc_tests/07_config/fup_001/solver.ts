let __lines: string[] = require("fs").readFileSync(0).toString().split("\n");
let input = () : string => __lines.length === 0 ? "" : __lines.shift()!;
let write = (text: any, end:string="\n")=> process.stdout.write("" + text + end);
