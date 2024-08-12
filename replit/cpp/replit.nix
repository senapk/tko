{ pkgs }: {
	deps = [
        pkgs.python3
        pkgs.graphviz
        pkgs.clang_12
        pkgs.ccls
        pkgs.gdb
        pkgs.gnumake
	];
}
